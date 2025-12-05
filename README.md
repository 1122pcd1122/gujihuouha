# Ancient Chinese NER (AC-NER) - 基于多特征融合的古文命名实体识别系统

本项目是一个针对古代汉语（文言文）的命名实体识别（NER）系统。模型基于 **GuWen-Bert** 预训练模型，并创新性地融合了 **RoFormer** 增强特征、**字形部首特征 (Radical)** 以及 **词性特征 (POS)**，通过 CNN 和 Cross-Attention 机制进行多模态特征融合，最后使用 CRF 层进行序列标注。

本项目提供了单句预测脚本 (`predict.py`) 和基于 Flask 的 Web API 服务 (`app.py`)。

## 📚 项目简介

  * **核心模型**: GuWen-Bert + RoFormer + Radical CNN + POS CNN + CRF
  * **特征融合**:
      * **语义特征**: GuWen-Bert & RoFormer
      * **字形特征**: 基于 Word2Vec 的部首嵌入 (Radical Embedding)
      * **语法特征**: 基于 Word2Vec 的词性嵌入 (POS Embedding)
  * **应用场景**: 自动识别古籍文本中的人名、地名、职官等实体。

## 📂 目录结构

请确保您的项目目录结构如下所示：

```text
.
├── app.py                  # Flask Web 服务启动脚本
├── predict.py              # 单句命令行预测脚本
├── model.py                # 模型架构定义
├── data_preprocessing.py   # 数据预处理
├── label_Reflection.py     # 标签ID映射文件
├── requirements.txt        # 项目依赖库
├── GuWen-Bert/             # [需准备] GuWen-Bert 预训练模型文件夹
├── roformer_v2_chinese_char_base/  # [需准备] RoFormer V2 预训练模型文件夹
├── model_best/             # [需准备] 训练好的 NER 模型文件夹
├── word2vec/               # [需准备] 特征嵌入模型文件夹
└── jiayan_models/          # [需准备] 甲言工具包模型文件夹
```

## 🛠️ 环境与模型准备

### 1\. 安装依赖

请确保 Python 版本 \>= 3.8。

```bash
pip install -r requirements.txt
```

*主要依赖: `torch`, `transformers`, `flask`, `jiayan`, `gensim`, `roformer`, `pytorch-crf`*

### 2\. 模型文件准备 (Model Preparation)

由于代码中使用硬编码路径加载模型，请务必在项目根目录下准备好以下 **5 个文件夹**：

#### A. 训练好的 NER 模型文件夹 (`model_best/`)

请下载训练好的模型权重 `model.pt` 并放入该文件夹。

  * **下载链接 (Baidu Netdisk)**: [点击跳转](https://pan.baidu.com/s/1fuvJOCp31cR-dsXvRuGKmQ?pwd=1234)
  * **提取码**: `1234`
  * **存放位置**: `model_best/model.pt`

#### B. 预训练基座文件夹 (`GuWen-Bert/`)

请准备 GuWen-Bert 预训练模型文件放入该文件夹。

  * **说明**: 代码中指定路径为 `GuWen-Bert`。

#### C. RoFormer 基座文件夹 (`roformer_v2_chinese_char_base/`)

请准备 RoFormer V2 (Chinese Char Base) 预训练模型文件放入该文件夹。

  * **说明**: 代码中指定路径为 `roformer_v2_chinese_char_base`。

#### D. 特征嵌入文件夹 (`word2vec/`)

请准备部首和词性的 Word2Vec 模型及映射表放入该文件夹。

  * **说明**: 需包含部首模型、词性模型及汉字部首映射表。

#### E. 甲言模型文件夹 (`jiayan_models/`)

请准备甲言 (Jiayan) 工具包的词性标注模型放入该文件夹。

  * **说明**: 需包含 `pos_model` 文件夹，用于古文分词和词性标注。

## 🚀 运行与使用

### 方式一：命令行单句预测

直接运行 `predict.py` 脚本进行测试。

1.  打开 `predict.py`，修改 `sentence` 变量为您想测试的句子。
2.  运行命令：
    ```bash
    python predict.py
    ```
3.  输出示例：
    ```text
    正在预测句子: 令绍使洛阳方略武吏...
    --------------------------------------------------
    【识别结果】:
      类型 [LOC]: 洛阳
      类型 [OFFI]: 方略武吏
    --------------------------------------------------
    ```

### 方式二：启动 Web API 服务

使用 `app.py` 启动 Flask 服务，提供 RESTful 接口。

1.  启动服务：

    ```bash
    python app.py
    ```

    *服务默认监听端口 `5001`*。

2.  **API 接口调用**:
    您可以使用 `request.py` 进行测试，或使用 Postman。

      * **URL**: `http://localhost:5001/predict`
      * **Method**: `POST`
      * **Content-Type**: `application/json`

    **请求体**:

    ```json
    {
        "text": "令绍使洛阳方略武吏，检司诸宦者。"
    }
    ```

    **响应体**:

    ```json
    {
        "code": 200,
        "msg": "success",
        "data": {
            "text": "令绍使洛阳方略武吏，检司诸宦者。",
            "entities": {
                "LOC": ["洛阳"],
                "OFFI": ["方略武吏", "检司"]
            }
        }
    }
    ```

## ⚠️ 常见问题

1.  **FileNotFoundError**:

      * 请务必检查 `model_best/`, `GuWen-Bert/` 等 5 个核心文件夹是否存在且拼写正确。代码使用相对路径，请在项目根目录下运行脚本。

2.  **ModuleNotFoundError**:

      * 加载 `model.pt` 时，PyTorch 需要能找到 `GuWenBERTModel` 等类的定义。请确保 `model.py` 在您的 `PYTHONPATH` 中，或者与运行脚本在同一目录下。

3.  **CUDA/CPU 问题**:

      * 代码会自动检测 CUDA。如果希望强制使用 CPU，请修改 `data_preprocessing.py` 中的 `device` 设置。

-----