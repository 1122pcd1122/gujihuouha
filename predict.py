import os
import torch
from torch.utils.data import DataLoader
from data_preprocessing import RadicalProcessor, radical_word2vec_model_path, radical_dict_path, POSProcessor, \
    pos_word2vec_model_path, Dataset, device
from label_Reflection import get_lid, label2id, id2label

from model import GuWenBERTModel
from model import GuWenBERTEmbedding
from model import EncoderWithMHSA
from model import RoFormerModule
from model import RadicalCNNEncoder
from model import PosCNNEncoder


class SingleSentencePredictor:
    def __init__(self, model_path, label2id, id2label, device):
        self.device = device
        self.label2id = label2id
        self.id2label = id2label

        print(f"Loading model from {model_path}...")
        # 加载模型 (注意：必须确保当前文件中有 GuWenBERTModel 等类的定义)
        self.model = torch.load(model_path, map_location=device)
        self.model.to(device)
        self.model.eval()

        # 初始化特征提取器 (必须与训练时使用的路径一致)
        self.radical_processor = RadicalProcessor(radical_word2vec_model_path, radical_dict_path)
        self.pos_processor = POSProcessor(pos_word2vec_model_path)

    def predict(self, text):
        """
        核心预测逻辑
        """
        if not text:
            return [], {}, {}  # 修改返回值匹配

        # 1. 构造假标签数据
        # 【修正点】：必须构造为 [[chars_list, labels_list]] 的形式
        # 之前的 list(zip(...)) 结构会导致 get_lid 错把汉字当成标签读取
        chars = list(text)
        dummy_labels = ['O'] * len(chars)

        # 正确的结构：一个样本由 [字符列表, 标签列表] 组成
        raw_data = [[chars, dummy_labels]]

        # 2. 数字化 (调用原有的 get_lid 函数)
        # 此时 get_lid 读取 item[1] 得到的是 ['O', 'O'...]，不会再报错
        trans_data = get_lid(raw_data, self.label2id)

        # 3. 构造 Dataset 和 DataLoader (batch_size=1)
        dataset = Dataset(trans_data, self.label2id, self.id2label, self.device,
                          radical_processor=self.radical_processor,
                          pos_processor=self.pos_processor)
        dataloader = DataLoader(dataset, batch_size=1, shuffle=False, collate_fn=dataset.collate_fn)

        # 4. 模型推理
        pred_labels = []
        with torch.no_grad():
            for batch_samples in dataloader:
                batch_data, batch_token_starts, batch_tags, batch_radicals, batch_pos = batch_samples

                # 获取 mask
                batch_masks = batch_data.gt(0)

                # 前向传播
                outputs = self.model((batch_data, batch_token_starts, batch_radicals, batch_pos),
                                     token_type_ids=None,
                                     attention_mask=batch_masks,
                                     labels=None)
                logits = outputs[0]

                # 构造解码 Mask
                seq_len = logits.shape[1]
                decode_mask = torch.ones((1, seq_len), dtype=torch.uint8).to(self.device) > 0

                # CRF 解码
                batch_output = self.model.crf.decode(logits, mask=decode_mask)

                # 将 ID 转回 BIO 标签
                pred_labels = [self.id2label.get(idx) for idx in batch_output[0]]
                break

                # 5. 提取实体
        entities = self.extract_entities(chars, pred_labels)
        return chars, pred_labels, entities

    def extract_entities(self, chars, tags):
        """
        辅助函数：从 BIO 标签序列中解析实体
        """
        entities = {}
        entity = ""
        label = ""

        for char, tag in zip(chars, tags):
            if tag.startswith("B-"):
                if entity:
                    if label not in entities: entities[label] = []
                    entities[label].append(entity)
                entity = char
                label = tag[2:]
            elif tag.startswith("I-") and label == tag[2:]:
                entity += char
            else:
                if entity:
                    if label not in entities: entities[label] = []
                    entities[label].append(entity)
                entity = ""
                label = ""
        if entity:
            if label not in entities: entities[label] = []
            entities[label].append(entity)

        return entities


# -------------------------------------------------------------------------
# 主执行入口
# -------------------------------------------------------------------------
if __name__ == '__main__':
    # 1. 设置模型路径
    model_path = "model_best/model.pt"

    if not os.path.exists(model_path):
        print(f"错误: 找不到模型文件 {model_path}")
    else:
        # 2. 初始化预测器
        predictor = SingleSentencePredictor(model_path, label2id, id2label, device)

        # 3. 设置要预测的句子
        sentence = "令绍使洛阳方略武吏，检司诸宦者。又令绍弟虎贲中郎将术选温厚虎贲二百人，当入禁中，代持兵黄门陛守门户"

        print(f"\n正在预测句子: {sentence}")
        print("-" * 50)

        # 4. 执行预测
        chars, tags, entities = predictor.predict(sentence)

        # 5. 打印结果
        # print(f"字/标签序列: {list(zip(chars, tags))}") # 如果想看每个字的标签，取消此行注释

        if entities:
            print("【识别结果】:")
            for label, items in entities.items():
                print(f"  类型 [{label}]: {', '.join(items)}")
        else:
            print("【识别结果】: 未发现实体")
        print("-" * 50)
