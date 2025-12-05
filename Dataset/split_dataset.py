from sklearn.model_selection import train_test_split
from opencc import OpenCC
# 创建一个OpenCC的实例，指定转换类型为繁体到简体
cc = OpenCC('t2s')

def t2s(str, cc):
  """
  繁体转简体
  """
  return cc.convert(str)

def save_data(file_path, data):
  """
  保存切分后的数据集
  """
  with open(file_path, 'w', encoding='utf-8') as file:
    for item in data:
      file.write(f'{item.strip()}\n')

def split_dataset(file_path):
  """
  划分数据集,同时将繁体字转为简体字
  """
  data = []
  with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
      line = t2s(line, cc)
      data.append(line)
  # 划分训练集和其余部分，比例为7:3 (10分之7留给训练集)
  train_data, remaining = train_test_split(data, test_size=0.3)

  # 再将剩下的部分按照2:1的比例划分为验证集和测试集 (3的部分再划分为2份验证集和1份测试集)
  val_data, test_data = train_test_split(remaining, test_size=1/3)

  return train_data, val_data, test_data


train_data, val_data, test_data = split_dataset('./GuNER2023_train.txt')
save_data('./preprocess/train.txt', train_data)
save_data('./preprocess/val.txt', val_data)
save_data('./preprocess/test.txt', test_data)