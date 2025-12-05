import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, BertTokenizer
import json

pos_ids = 'pos2id.json'

def read_id(id_path):
    with open(id_path, "r", encoding="utf-8") as f:
        lines = json.load(f)
    return lines

class Dataset(torch.utils.data.Dataset):
    def __init__(self, data_lines, predicate2id, device, model_path, max_seq_length):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, do_lower_case=True)
        self.predicate2id = predicate2id
        self.max_seq_length = max_seq_length
        self.device = device
        self.dataset = self.process_data(data_lines)
        self.pre_train_path = model_path

        self.token = BertTokenizer.from_pretrained(self.pre_train_path)
        
        

    def find_entity_positions(self, tokens, subject_text, object_text):
        """
        根据主体和客体的文本，在分词后的 tokens 中找到它们的位置，并插入 * 标记。
        
        :param tokens: 分词后的文本列表
        :param subject_text: 主体实体文本
        :param object_text: 客体实体文本
        :return: 实体位置字典 {'entity1': (start, end), 'entity2': (start, end)} 和标记后的 tokens
        """
        def find_single_position(tokens, target_text, used_indices):
            """
            查找指定文本的起始和结束位置，避免重复匹配。
            """
            for i in range(len(tokens) - len(target_text) + 1):
                if i in used_indices:
                    continue
                if tokens[i:i + len(target_text)] == target_text:
                    return [i, i + len(target_text) - 1]
            return None

        # 分词主体和客体
        subject_tokens = self.tokenizer.tokenize(subject_text)
        object_tokens = self.tokenizer.tokenize(object_text)
        
        # 查找主体和客体的位置
        used_indices = set()
        subject_pos = find_single_position(tokens, subject_tokens, used_indices)
        if subject_pos:
            used_indices.update(range(subject_pos[0], subject_pos[1] + 1))
        
        object_pos = find_single_position(tokens, object_tokens, used_indices)
        if object_pos:
            used_indices.update(range(object_pos[0], object_pos[1] + 1))

        if not subject_pos or not object_pos:
            raise ValueError(f"Cannot find positions for subject '{subject_text}' or object '{object_text}'.")

        # # 插入 * 标记
        marked_tokens = tokens[:]
        # 插入主体标记
        marked_tokens.insert(subject_pos[0], "*")
        marked_tokens.insert(subject_pos[1] + 2, "*")  # +2 因为前面插入了一个 *
        # 更新主体位置
        subject_pos = [subject_pos[0], subject_pos[1] + 2]

        # 插入客体标记（动态调整索引）
        object_start = object_pos[0] + 2 if object_pos[0] > subject_pos[1] else object_pos[0]
        object_end = object_pos[1] + 2 if object_pos[0] > subject_pos[1] else object_pos[1]
        marked_tokens.insert(object_start, "*")
        marked_tokens.insert(object_end + 2, "*")  # +2 因为前面插入了一个 *
        # 更新客体位置
        object_pos = [object_start, object_end + 2]

        # 如果主体在客体之后，需要再次更新主体位置
        if subject_pos[0] > object_pos[1]:
            subject_pos = [subject_pos[0] + 2, subject_pos[1] + 2]
        # 返回实体位置和标记后的 tokens
        entity_pos = {
            "entity1": subject_pos,  # 主体位置
            "entity2": object_pos   # 客体位置
        }
        return entity_pos, marked_tokens

    def process_data(self, data_lines):
        """
        数据预处理，标记实体位置，提取特征。

        Args:
            data_lines : relation data
            tokenizer: GuwenBERT
            predicate2id 
            max_seq_length (int)

        Returns:
            features (list): 包含所有样本的特征字典列表。
        """

        features = []
        data_lines = [json.loads(line.strip()) for line in data_lines]

        for sample in data_lines:
            text = sample['text']
            subject = sample['subject_word']
            object = sample['object_word']
            subject_POS = sample['subject_pos']
            object_POS = sample['object_pos']
            predicate = sample['predicate']

            # 映射关系标签到 ID
            predicate_id = self.predicate2id.get(predicate, -1)
            if predicate_id == -1:
                continue

            POS2ids = read_id(pos_ids)
            subject_POS_id = int(POS2ids[f'{subject_POS}'])
            object_POS_id = int(POS2ids[f'{object_POS}'])



            tokens = self.tokenizer.tokenize(text)
            tokens = tokens[:self.max_seq_length - 2]

            # 找到实体位置并标记
            try:
                entity_pos, marked_tokens = self.find_entity_positions(tokens, subject, object)
                # print(entity_pos)
                # print(marked_tokens)
            except ValueError as e:
                print(e)
                continue  # 跳过无法匹配的样本
            # 转换为输入 ID
            # print(entity_pos)
            # print(marked_tokens)
            input_ids = self.tokenizer.convert_tokens_to_ids(marked_tokens)
            input_ids = self.tokenizer.build_inputs_with_special_tokens(input_ids)
            # e1 mask, e2 mask
            e1_mask = [0] * len(input_ids)
            e2_mask = [0] * len(input_ids)
            # print(entity_pos["entity1"])
            # print(e1_mask, e2_mask)
            for i in range(entity_pos["entity1"][0], entity_pos["entity1"][1]):
                e1_mask[i] = 1
            for i in range(entity_pos["entity2"][0], entity_pos["entity2"][1]):
                e2_mask[i] = 1

            # 构建特征
            features.append({
                "input_ids": torch.tensor(input_ids),
                "attention_mask": torch.tensor([1] * len(input_ids)),
                "relation_label": torch.tensor(predicate_id),
                "e1_mask": torch.tensor(e1_mask),
                "e2_mask": torch.tensor(e2_mask),
                "e1_pos": subject_POS_id,
                "e2_pos": object_POS_id,
                })

        return features

    def __getitem__(self, idx):
        """sample data to get batch"""
        return {
            "input_ids": self.dataset[idx]["input_ids"],
            "attention_mask": self.dataset[idx]["attention_mask"],
            "relation_label": self.dataset[idx]["relation_label"],
            # "entity_labels": self.dataset[idx]["entity_labels"],
            "e1_mask": self.dataset[idx]["e1_mask"],
            "e2_mask": self.dataset[idx]["e2_mask"],
            "e1_pos": self.dataset[idx]["e1_pos"],
            "e2_pos": self.dataset[idx]["e2_pos"],
        }

    def __len__(self):
        """get dataset size"""
        return len(self.dataset)

    def collate_fn(self, batch):
       
        input_ids = [item["input_ids"] for item in batch]
        attention_mask = [item["attention_mask"] for item in batch]
        relation_labels = [item["relation_label"] for item in batch]
        # entity_labels = [item["entity_labels"] for item in batch]
        e1_mask = [item["e1_mask"] for item in batch]
        e2_mask = [item["e2_mask"] for item in batch]
        e1_pos = [item["e1_pos"] for item in batch]
        e2_pos = [item["e2_pos"] for item in batch]
        
        # 使用padding对齐长度
        max_len = self.max_seq_length
        padded_input_ids = torch.zeros((len(batch), max_len), dtype=torch.long)
        padded_attention_mask = torch.zeros((len(batch), max_len), dtype=torch.long)
        padded_e1_mask = torch.zeros((len(batch), max_len), dtype=torch.long)
        padded_e2_mask = torch.zeros((len(batch), max_len), dtype=torch.long)

        for i, ids in enumerate(input_ids):
            padded_input_ids[i, :len(ids)] = ids
            padded_attention_mask[i, :len(attention_mask[i])] = attention_mask[i]
            padded_e1_mask[i, :len(e1_mask[i])] = e1_mask[i]
            padded_e2_mask[i, :len(e2_mask[i])] = e2_mask[i]
        

        return {
            "input_ids": padded_input_ids.to(self.device),
            "attention_mask": padded_attention_mask.to(self.device),
            "relation_labels": torch.tensor(relation_labels, dtype=torch.long).to(self.device),
            # "entity_labels": torch.stack(entity_labels).to(self.device),  # 实体标签
            "e1_mask": padded_e1_mask.to(self.device),
            "e2_mask": padded_e2_mask.to(self.device),
            "e1_pos": torch.tensor(e1_pos, dtype=torch.long).to(self.device),
            "e2_pos": torch.tensor(e2_pos, dtype=torch.long).to(self.device),
        }
