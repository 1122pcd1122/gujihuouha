import json
import re
import torch
from gensim.models import Word2Vec
from transformers import BertPreTrainedModel, BertModel, BertTokenizer
import numpy as np
from jiayan import WordNgramTokenizer, CRFPOSTagger

def txt2bio(inputfile_path, outfile_path):
  """
  将txt文件转换成bio格式
  """
  with open(inputfile_path, 'r', encoding='utf-8') as f, open(outfile_path, 'w', encoding='utf-8') as fout:
    for line in f:
      words = []
      labels = []

      for item in re.findall(".*?(([{].*?[}])|[^\{]*)", line):
        if item[1]:  # 如果找到了实体名
          entity = item[1][1:-1].split('|')
          words.extend(list(entity[0]))
          labels.append('B-' + entity[1])
          labels.extend(['I-' + entity[1]] * (len(entity[0]) - 1))

        else:  # 如果没有找到实体名
          words.extend(list(item[0]))
          labels.extend(['O'] * len(item[0]))
      for idx in range(len(words)):
          fout.write(words[idx] + ' ' + labels[idx] + '\n')
      fout.write('\n')


guwenbert_base_path = 'GuWen-Bert'
use_gpu = torch.cuda.is_available()
device = torch.device('cuda' if use_gpu else 'cpu')


class RadicalProcessor:
  def __init__(self, radical_word2vec_model_path, radical_dict_path):
    """
    初始化RadicalProcessor类，加载word2vec模型和部首字典
    :param radical_word2vec_model_path: 训练好的word2vec模型路径
    :param radical_dict_path: 包含字到部首映射的JSON文件路径
    """
    # 加载训练好的word2vec模型
    self.radical_model = Word2Vec.load(radical_word2vec_model_path)

    # 加载部首字典
    self.radical_dict = self.load_radical_dict(radical_dict_path)

  def load_radical_dict(self, file_path):
    """
    从JSON文件加载部首字典
    :param file_path: JSON文件路径
    :return: 部首字典
    """
    with open(file_path, 'r', encoding='utf-8') as f:
      radical_dict = json.load(f)
    return radical_dict

  def get_radical(self, character):
    """
    获取字的部首
    :param character: 输入的汉字字符
    :return: 对应的部首
    """
    if character == 'O' or not character.strip():  # 如果是'O'或空格，直接跳过
      return None

    radical = self.get_radical_from_character(character)
    return radical

  def get_radical_from_character(self, character):
    """
    根据字符获取部首
    :param character: 输入的汉字字符
    :return: 对应的部首
    """
    # 从部首字典获取部首
    radical = self.radical_dict.get(character, None)
    return radical

  def get_radical_embedding(self, character):
    """
    获取部首的word2vec嵌入
    :param character: 输入的汉字字符
    :return: 对应的部首嵌入向量，如果没有部首或部首不在word2vec模型中，则返回零向量
    """
    radical = self.get_radical(character)  # 获取部首
    if radical is None:
      return np.zeros(self.radical_model.vector_size)  # 如果没有找到部首，返回零向量

    # 如果部首存在于word2vec模型中，则返回嵌入
    if radical in self.radical_model.wv:
      return self.radical_model.wv[radical]
    else:
      # 部首不在模型中，返回零向量
      return np.zeros(self.radical_model.vector_size)

class POSProcessor:
  def __init__(self, pos_word2vec_model_path):
    """
    初始化POSProcessor类，加载word2vec模型
    :param word2vec_model_path: 训练好的word2vec模型路径
    """
    # 加载训练好的word2vec模型
    self.pos_model = Word2Vec.load(pos_word2vec_model_path)

  def get_pos_embedding(self, pos_tag):
    """
    获取词性的word2vec嵌入
    :param pos_tag: 输入的词性标签
    :return: 对应的词性嵌入向量，如果词性不在word2vec模型中，则返回零向量
    """
    if pos_tag in self.pos_model.wv:
      return self.pos_model.wv[pos_tag]
    else:
      # 如果词性不在模型中，返回零向量
      return np.zeros(self.pos_model.vector_size)

# 加载训练好的word2vec模型
radical_word2vec_model_path = 'word2vec/radical_word2vec.model'
radical_dict_path = 'word2vec/char2radical.json'
pos_word2vec_model_path = 'word2vec/pos_word2vec.model'
tokenizer = WordNgramTokenizer()  # 分词工具
postagger = CRFPOSTagger()  # 词性标注工具
postagger.load('jiayan_models/pos_model')


class Dataset(torch.utils.data.Dataset):
  def __init__(self, lines, label2id, id2label, device, word_pad_idx=0, label_pad_idx=-1, radical_embedding_size=256, radical_processor=None,
               pos_embedding_size = 256, pos_processor=None):
    self.tokenizer = BertTokenizer.from_pretrained(guwenbert_base_path, do_lower_case=True)
    self.label2id = label2id
    self.id2label = id2label
    # 调试打印
    # print("radical_processor:", radical_processor)
    self.radical_processor = radical_processor  # 用来处理部首的实例
    self.radical_embedding_size = radical_embedding_size  # 设置部首嵌入的大小
    self.pos_processor = pos_processor
    self.pos_embedding_size = pos_embedding_size
    self.dataset = self.preprocess(lines)
    self.word_pad_idx = word_pad_idx
    self.label_pad_idx = label_pad_idx
    self.device = device



  def preprocess(self, lines):
    """
    Maps tokens and tags to their indices and stores them in the dict data.
    examples:
        word:['[CLS]', '浙', '商', '银', '行', '企', '业', '信', '贷', '部']
        sentence:([101, 3851, 1555, 7213, 6121, 821, 689, 928, 6587, 6956],
                    array([ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10]))
        label:[3, 13, 13, 13, 0, 0, 0, 0, 0]
    """
    # print(self.radical_processor.get_radical_embedding('浙'))
    data = []
    sentences = []
    labels = []
    radical_embeddings = []  # 用于存储部首嵌入
    pos_embeddings = []

    for line in lines:
      # replace each token by its index
      # we can not use encode_plus because our sentences are aligned to labels in list type
      words = []
      word_lens = []
      radical_embeddings_per_sentence = []  # 用于存储当前句子的部首嵌入
      # 将 `line[0]` 合并为一句话
      sentence = ''.join(line[0])

      # 使用 Jiayan 分词
      segmented_words = list(tokenizer.tokenize(sentence))

      # 词性标注
      pos_tags = postagger.postag(segmented_words)

      # 通过POSProcessor将词性转换为嵌入向量
      pos_embeddings_per_sentence = []
      for word, pos in zip(segmented_words, pos_tags):
        # 获取词性嵌入
        pos_embedding = self.pos_processor.get_pos_embedding(pos)  # 形状为 (1, 256)
        # 按词长度扩展到每个字符
        pos_embeddings_per_sentence.extend([pos_embedding] * len(word))
      pos_embeddings.append(pos_embeddings_per_sentence)  # 添加到句子嵌入列表


      for token in line[0]:
        # 获取部首嵌入
        radical_embedding = [self.radical_processor.get_radical_embedding(character) for character in token]
        words.append(self.tokenizer.tokenize(token))
        word_lens.append(len(token))
        radical_embeddings_per_sentence.append(radical_embedding)  # 存储当前token的部首嵌入

      # 变成单个字的列表，开头加上[CLS]
      words = ['[CLS]'] + [item for token in words for item in token]

      # 计算token的起始位置
      token_start_idxs = 1 + np.cumsum([0] + word_lens[:-1])

      sentences.append((self.tokenizer.convert_tokens_to_ids(words), token_start_idxs))
      labels.append(line[1])

      # 存储当前句子的部首嵌入
      radical_embeddings.append(radical_embeddings_per_sentence)

    # 返回句子、标签和部首嵌入
    for sentence, label, radical_embedding, pos_embeddings_per_token in zip(sentences, labels, radical_embeddings, pos_embeddings):
      data.append((sentence, label, radical_embedding, pos_embeddings_per_token))

    return data

  def __getitem__(self, idx):
    """sample data to get batch"""
    word = self.dataset[idx][0]
    label = self.dataset[idx][1]
    radical_embeddings = self.dataset[idx][2]
    pos_embeddings = self.dataset[idx][3]
    return [word, label, radical_embeddings, pos_embeddings]

  def __len__(self):
    """get dataset size"""
    return len(self.dataset)

  def collate_fn(self, batch):
    """
    process batch data, including:
        1. padding: 将每个batch的data padding到同一长度（batch中最长的data长度）
        2. aligning: 找到每个sentence sequence里面有label项，文本与label对齐
        3. tensor：转化为tensor
    """
    sentences = [x[0] for x in batch]
    labels = [x[1] for x in batch]
    radical_embeddings = [x[2] for x in batch]  # 获取每个样本的部首嵌入列表
    pos_embeddings = [x[3] for x in batch]
    # batch length
    batch_len = len(sentences)

    # compute length of longest sentence in batch
    max_len = max([len(s[0]) for s in sentences])
    max_label_len = 0

    # padding data 初始化
    batch_data = self.word_pad_idx * np.ones((batch_len, max_len))
    batch_label_starts = []

    # padding and aligning
    for j in range(batch_len):
      cur_len = len(sentences[j][0])
      batch_data[j][:cur_len] = sentences[j][0]
      # 找到有标签的数据的index（[CLS]不算）
      label_start_idx = sentences[j][-1]
      label_starts = np.zeros(max_len)
      label_starts[[idx for idx in label_start_idx if idx < max_len]] = 1
      batch_label_starts.append(label_starts)
      max_label_len = max(int(sum(label_starts)), max_label_len)

    # padding label
    batch_labels = self.label_pad_idx * np.ones((batch_len, max_label_len))
    for j in range(batch_len):
      cur_tags_len = len(labels[j])
      batch_labels[j][:cur_tags_len] = labels[j]
      # print(f"Shape of labels[j]: {np.shape(labels[j])}")  # 打印每个标签的形状

    # 初始化填充数组
    batch_radicals = np.zeros((batch_len, max_len-1, self.radical_embedding_size))
    # print("batch_radicals shape:", batch_radicals.shape)  # 应输出 (batch_len, max_len, self.radical_embedding_size)
    for j in range(batch_len):
      # 将 radical_embeddings[j] 转换为 NumPy 数组
      embeddings = np.array(radical_embeddings[j], dtype=np.float32)

      # 去掉多余的维度 (X, 1, 256) -> (X, 256)
      if embeddings.ndim == 3 and embeddings.shape[1] == 1:
        embeddings = embeddings.squeeze(axis=1)

      current_len = embeddings.shape[0]
      actual_len = min(current_len, max_len)

      # 调试输出
      # print(f"Sample {j}: embeddings shape = {embeddings.shape}")

      # 检查形状是否正确
      if embeddings.ndim != 2 or embeddings.shape[1] != self.radical_embedding_size:
        raise ValueError(f"radical_embeddings[{j}] 的形状为 {embeddings.shape}，期望为 (?, {self.radical_embedding_size})")

      # 赋值实际的嵌入
      batch_radicals[j, :actual_len, :] = embeddings[:actual_len, :]

    # 初始化填充数组
    batch_pos_embeddings = np.zeros((batch_len, max_len - 1, self.pos_embedding_size))

    for j in range(batch_len):
      # 将 pos_embeddings[j] 转换为 NumPy 数组
      embeddings = np.array(pos_embeddings[j], dtype=np.float32)

      # 去掉多余的维度 (X, 1, D) -> (X, D)
      if embeddings.ndim == 3 and embeddings.shape[1] == 1:
        embeddings = embeddings.squeeze(axis=1)

      # 获取当前句子的嵌入长度
      current_len = embeddings.shape[0]
      actual_len = min(current_len, max_len - 1)

      # 检查形状是否正确
      if embeddings.ndim != 2 or embeddings.shape[1] != self.pos_embedding_size:
        raise ValueError(f"pos_embeddings[{j}] 的形状为 {embeddings.shape}，期望为 (?, {self.pos_embedding_size})")

      # 赋值实际的嵌入
      batch_pos_embeddings[j, :actual_len, :] = embeddings[:actual_len, :]

    # convert data to torch LongTensors
    batch_data = torch.tensor(batch_data, dtype=torch.long)
    batch_label_starts = torch.tensor(batch_label_starts, dtype=torch.long)
    batch_labels = torch.tensor(batch_labels, dtype=torch.long)
    batch_radicals = torch.tensor(batch_radicals, dtype=torch.float32)
    batch_pos_embeddings = torch.tensor(batch_pos_embeddings, dtype=torch.float32)

    # shift tensors to GPU if available
    batch_data, batch_label_starts = batch_data.to(self.device), batch_label_starts.to(self.device)
    batch_labels = batch_labels.to(self.device)
    batch_radicals = batch_radicals.to(self.device)
    batch_pos_embeddings = batch_pos_embeddings.to(self.device)

    return [batch_data, batch_label_starts, batch_labels, batch_radicals, batch_pos_embeddings]



