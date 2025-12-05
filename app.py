import os
import torch
from flask import Flask, request, jsonify
from torch.utils.data import DataLoader

# 引入项目依赖
from data_preprocessing import RadicalProcessor, radical_word2vec_model_path, radical_dict_path, POSProcessor, \
    pos_word2vec_model_path, Dataset, device
from label_Reflection import get_lid, label2id, id2label

from model import GuWenBERTModel, GuWenBERTEmbedding, EncoderWithMHSA, RoFormerModule, RadicalCNNEncoder, \
    PosCNNEncoder

# 初始化 Flask 应用
app = Flask(__name__)
# 配置 Flask 支持中文返回，不转义为 ASCII
app.config['JSON_AS_ASCII'] = False


# -------------------------------------------------------------------------
# 预测核心类 (保持不变)
# -------------------------------------------------------------------------
class SingleSentencePredictor:
    def __init__(self, model_path, label2id, id2label, device):
        self.device = device
        self.label2id = label2id
        self.id2label = id2label

        print(f"正在加载模型: {model_path} ...")
        # 加载模型
        # 注意：torch.load 加载完整模型对象时，必须确保当前命名空间能找到模型类的定义
        self.model = torch.load(model_path, map_location=device)
        self.model.to(device)
        self.model.eval()

        print("正在初始化特征处理器...")
        # 初始化特征提取器
        self.radical_processor = RadicalProcessor(radical_word2vec_model_path, radical_dict_path)
        self.pos_processor = POSProcessor(pos_word2vec_model_path)
        print("模型服务初始化完成。")

    def predict(self, text):
        """
        核心预测逻辑
        """
        if not text:
            return [], {}, {}

        # 1. 构造数据结构 [[chars, labels]]
        chars = list(text)
        dummy_labels = ['O'] * len(chars)
        raw_data = [[chars, dummy_labels]]

        # 2. 数字化
        trans_data = get_lid(raw_data, self.label2id)

        # 3. 构造 DataLoader (batch_size=1)
        dataset = Dataset(trans_data, self.label2id, self.id2label, self.device,
                          radical_processor=self.radical_processor,
                          pos_processor=self.pos_processor)
        dataloader = DataLoader(dataset, batch_size=1, shuffle=False, collate_fn=dataset.collate_fn)

        # 4. 模型推理
        pred_labels = []
        with torch.no_grad():
            for batch_samples in dataloader:
                batch_data, batch_token_starts, batch_tags, batch_radicals, batch_pos = batch_samples

                batch_masks = batch_data.gt(0)

                outputs = self.model((batch_data, batch_token_starts, batch_radicals, batch_pos),
                                     token_type_ids=None,
                                     attention_mask=batch_masks,
                                     labels=None)
                logits = outputs[0]

                seq_len = logits.shape[1]
                decode_mask = torch.ones((1, seq_len), dtype=torch.uint8).to(self.device) > 0

                batch_output = self.model.crf.decode(logits, mask=decode_mask)
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
# 全局变量与初始化
# -------------------------------------------------------------------------
# 设置模型路径
MODEL_PATH = "model_best/model.pt"  # 请确保路径正确
predictor = None


def load_predictor():
    """在应用启动前加载模型"""
    global predictor
    if os.path.exists(MODEL_PATH):
        try:
            predictor = SingleSentencePredictor(MODEL_PATH, label2id, id2label, device)
        except Exception as e:
            print(f"模型加载失败: {e}")
    else:
        print(f"错误: 找不到模型文件 {MODEL_PATH}")


# -------------------------------------------------------------------------
# Flask 路由定义
# -------------------------------------------------------------------------

@app.route('/predict', methods=['POST'])
def predict_entity():
    """
    接口: /predict
    方法: POST
    参数: JSON {"text": "需要预测的古文句子"}
    返回: JSON {"code": 200, "data": {"entities": {...}, "tags": [...]}}
    """
    global predictor
    if not predictor:
        return jsonify({"code": 500, "msg": "模型未加载，请检查服务器日志"}), 500

    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"code": 400, "msg": "请求参数错误，请提供 'text' 字段"}), 400

        text = data['text']

        # 执行预测
        chars, tags, entities = predictor.predict(text)

        # 返回结果
        result = {
            "code": 200,
            "msg": "success",
            "data": {
                "text": text,
                "entities": entities,  # 实体字典
                # "details": list(zip(chars, tags))  # 可选：详细的字与标签对应关系
            }
        }
        return jsonify(result)

    except Exception as e:
        print(f"预测过程出错: {e}")
        return jsonify({"code": 500, "msg": f"服务器内部错误: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    status = "running" if predictor else "model_not_loaded"
    return jsonify({"status": status})


# -------------------------------------------------------------------------
# 启动服务
# -------------------------------------------------------------------------
if __name__ == '__main__':
    # 先加载模型
    load_predictor()

    # 启动 Flask 服务
    # host='0.0.0.0' 允许局域网访问，port=5000 为默认端口
    print("正在启动 Flask 服务...")
    app.run(host='0.0.0.0', port=5001, debug=False)