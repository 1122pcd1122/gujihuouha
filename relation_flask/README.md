# EPERR: 融合多源特征的古籍实体关系抽取系统

这是一个针对古代汉语（文言文）设计的实体关系抽取（Relation Extraction）项目。该系统基于 **GuWen-Bert** 预训练模型，创新性地融合了**实体词性特征**、**相对位置编码**以及**文本语义特征**，并通过交叉注意力机制和门控融合模块来提升关系分类的准确性。

## 📚 项目简介

本项目的核心模型 `EPERR` (Entity Position and Entity Relation Recognition) 旨在解决古文语境下的关系抽取问题。

### 主要特性

- **预训练基座**: 使用 `GuWen-Bert` 作为强大的古文语义特征提取器。
- **多特征融合**:
  - **POS Embedding**: 引入实体的词性信息（如 nh, ns 等）。
  - **Relative Position Encoding**: 显式编码两个实体在句子中的相对距离，捕捉位置依赖关系。
- **高级交互机制**:
  - **Fixed Cross Attention**: 利用交叉注意力机制增强 `[CLS]` 向量与实体特征的交互。
  - **Gated Feature Fusion**: 使用门控机制动态融合文本特征与词性特征。
- **服务化部署**: 提供基于 Flask 的 RESTful API 接口，支持实时推理。

## 📂 项目结构

所有核心代码与模型文件夹位于同一级目录下：

Plaintext

```
.
├── GuWen-Bert/         # [核心] 预训练模型文件夹 (config.json, pytorch_model.bin 等)
├── new_model/          # [核心] 训练好的模型权重文件夹 (存放 EPERR-sem+pos+rel.pth)
├── app.py              # Flask Web 服务接口
├── test.py             # 单句推理测试脚本
├── EPERR.py            # 模型架构定义
├── preprocess.py       # 数据预处理
├── relation2id.json    # 关系标签映射表
├── pos2id.json         # 词性标签映射表
└── requirements.txt    # 依赖说明
```

## 🛠️ 环境与配置

### 1. 安装依赖

请确保 Python 版本 >= 3.8，并安装以下依赖：

Bash

```
pip install -r requirements.txt
```

### 2. 模型文件准备 (Model Preparation)

请确保下载以下模型文件，并按照目录结构放置：

#### A. 训练好的模型权重 (EPERR Model)

请下载 `EPERR-sem+pos+rel.pth` 并放入 `new_model/` 文件夹中：

- **下载链接 (Baidu Netdisk)**: [点击跳转](https://pan.baidu.com/s/1XBwoZXMQN2kJu729855O-A?pwd=1234)
- **提取码**: `1234`
- **存放位置**: `./new_model/EPERR-sem+pos+rel.pth`

#### B. 预训练基座 (GuWen-Bert)

请确保 `./GuWen-Bert/` 目录下包含 Bert 的配置文件和权重 (`config.json`, `pytorch_model.bin`, `vocab.txt` 等)。

### 3. ⚠️ 关键配置修改

**请务必修改 `app.py` 和 `test.py` 中的路径配置**：

**在 `app.py` 和 `test.py` 中：**

Python

```
def get_configs():
    return {
        # ... 其他配置 ...

        'pretrain_model_path': 'GuWen-Bert',  
        
        'model_save_dir': 'new_model',        
        
        # ... 其他配置 ...
    }
```

## 🚀 快速开始

### 方式一：命令行测试

使用 `test.py` 脚本直接测试单句预测效果。

1. 修改 `test.py` 中的 `target_data` 变量为你想要测试的句子。

2. 运行脚本：

   Bash

   ```
   python test.py
   ```

3. 输出示例：

   Plaintext

   ```
   >>> 正在进行关系抽取预测...
   文本: 辛巳，立皇子冏为清河王...
   主体: 曹休 (nh)
   客体: 征东大将军 (ns)
   ------------------------------------------------------------
   >>> 预测结果: 【升迁】
   ```

### 方式二：启动 Web API 服务

使用 `app.py` 启动 Flask 服务，通过 HTTP 请求进行调用。

1. 启动服务：

   Bash

   ```
   python app.py
   ```

   *服务默认监听 `0.0.0.0:5000`*。

2. **API 接口说明**:

   - **URL**: `/predict`
   - **Method**: `POST`
   - **Content-Type**: `application/json`

   **请求体示例**:

   JSON

   ```
   {
       "text": "辛巳，立皇子冏为清河王。吴将诸葛瑾、张霸等寇襄阳，抚军大将军司马宣王讨破之，斩霸，征东大将军曹休又破其别将於寻阳",
       "subject_word": "曹休",
       "subject_pos": "nh",
       "object_word": "征东大将军",
       "object_pos": "ns"
   }
   ```

   **响应示例**:

   JSON

   ```
   {
       "status": "success",
       "data": {
           "text": "...",
           "subject": "曹休",
           "object": "征东大将军",
           "predicted_relation": "升迁"
       }
   }
   ```

## 🧠 模型架构详解

该模型在 `EPERR.py` 中定义，主要流程如下：

1. **输入处理**: 使用 BertTokenizer 对文本进行分词，并在 Entity1 和 Entity2 前后插入 `*` 标记。
2. **BERT 编码**: 获取 `last_hidden_state`。
3. **特征提取**:
   - **实体特征**: 对实体 tokens 进行平均池化 (Average Pooling)。
   - **词性特征**: 通过 `POSEmbedding` 将 POS 标签映射为向量。
   - **位置特征**: 计算两个实体 mask 的中心距离，映射为 `Relative Position Embeddings`。
4. **特征融合**:
   - 使用 `FeatureFusion` 模块，通过门控机制 (Gate) 和动态权重 (Alpha/Beta) 融合实体的文本特征与词性特征。
5. **交互与分类**:
   - 将融合后的实体特征与位置特征拼接。
   - 通过 `FixedCrossAttention` 让 `[CLS]` 向量关注实体特征。
   - 最后通过全连接层输出 15 种关系的概率分布。
