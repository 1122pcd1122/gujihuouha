import json

# 创建label2id和id2label字典
def trans_dic(labels):
    """
    获取label2id和id2label映射关系
    """
    label2id = {label: id for id, label in enumerate(labels)}
    id2label = {id: label for label, id in label2id.items()}
    return label2id, id2label

def save_dic2txt(save_path, dic):
    """
    保存label2id和id2label映射关系至txt文件
    """
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(dic, ensure_ascii=False, indent=2))

# 新的标签集合
labels_schema = ["O", "B-PER", "B-OFI", "B-LOC", "B-TIME", "I-PER", "I-OFI", "I-LOC", "I-TIME"]

# 创建和保存label2id和id2label字典
label2id, id2label = trans_dic(labels_schema)
save_dic2txt('./Dataset/BIO/label2id.txt', label2id)
save_dic2txt('./Dataset/BIO/id2label.txt', id2label)

# 读取BIO格式文件
def read_bio(file_path):
    """
    读取BIO格式文件
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = []  # 用于存储所有句子的单词和标签对
        words = []  # 当前句子的单词列表
        labels = []  # 当前句子的标签列表

        for line in f:
            contends = line.strip()
            tokens = contends.split(' ')

            # 如果该行是有效的单词-标签对
            if len(tokens) == 2:
                words.append(tokens[0])  # 单词
                labels.append(tokens[1])  # 标签

            else:  # 处理空行（表示句子的结束）
                if len(contends) == 0 and len(words) > 0:
                    # 将当前句子的单词和标签添加到lines中
                    lines.append([words, labels])
                    words = []  # 清空当前句子的单词列表
                    labels = []  # 清空当前句子的标签列表

        # 如果文件没有以空行结尾（即文件没有以空行标识句子的结束）
        if len(words) > 0:
            lines.append([words, labels])

    return lines


def get_lid(lines,label2id):
  """
  将数据中的label转换成id
  trans_lines =[(刀，郎),(1,5)]
  """
  trans_lines = []
  for item in lines:
    ids = [label2id[label] for label in item[1]]
    trans_lines.append([item[0], ids])
  return trans_lines

# test_lines = read_bio('./Dataset/BIO/test_bio.txt')
# print(test_lines[0])
# trans_lines = get_lid(test_lines, label2id)
# print(trans_lines[0])