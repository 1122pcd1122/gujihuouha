import json
import os
import torch
from torch.utils.data import DataLoader
from flask import Flask, request, jsonify
import warnings

# === 导入你的自定义模块 ===
from EPERR import EPERR
import preprocess as process

# 设置环境变量
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# 忽略警告
warnings.filterwarnings('ignore')

# === 初始化 Flask 应用 ===
app = Flask(__name__)

# === 全局变量 ===
# 这些变量将在服务启动时加载，避免每次请求都重新加载模型
MODEL = None
CONFIGS = None
DEVICE = None
PREDICATE2ID = None
ID2TYPE = None


def get_configs():
    """配置参数"""
    return {
        'r2id_path': 'relation2id.json',
        'pretrain_model_path': '../GuWen-Bert',
        'max_len': 128,
        'hidden_size': 768,
        'dropout': 0.1,
        'num_relations': 15,
        'seed': 42,
        'batch_size': 1,
        'model_save_dir': '../new_model',
        'model_filename': 'EPERR-sem+pos+rel.pth'
    }


def load_resources():
    """加载模型和资源的辅助函数"""
    global MODEL, CONFIGS, DEVICE, PREDICATE2ID, ID2TYPE

    print(">>> 正在初始化服务资源...")
    CONFIGS = get_configs()

    # 1. 设置设备
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(CONFIGS['seed'])
    if torch.cuda.is_available():
        torch.cuda.manual_seed(CONFIGS['seed'])

    # 2. 准备映射关系
    if os.path.exists(CONFIGS['r2id_path']):
        PREDICATE2ID = process.read_id(CONFIGS['r2id_path'])
    else:
        print(f"⚠️ 未找到 {CONFIGS['r2id_path']}，使用内置映射表。")
        PREDICATE2ID = {
            "为官": 0, "依附": 1, "父子": 2, "同名于": 3, "军事对抗": 4,
            "杀害": 5, "兄弟": 6, "出生地": 7, "葬地": 8, "朋友": 9,
            "隶属于": 10, "去往": 11, "作": 12, "位于": 13, "升迁": 14
        }
    ID2TYPE = {v: k for k, v in PREDICATE2ID.items()}

    # 3. 初始化模型结构
    MODEL = EPERR(
        model_path=CONFIGS['pretrain_model_path'],
        hidden_size=CONFIGS['hidden_size'],
        dropout=CONFIGS['dropout'],
        num_relations=CONFIGS['num_relations']
    )

    # 4. 加载权重
    model_path = os.path.join(CONFIGS['model_save_dir'], CONFIGS['model_filename'])
    if not os.path.exists(model_path):
        # 尝试回退到 best_model.pth
        fallback_path = os.path.join(CONFIGS['model_save_dir'], "best_model.pth")
        if os.path.exists(fallback_path):
            model_path = fallback_path
        else:
            raise FileNotFoundError(f"❌ 无法找到模型文件: {model_path} 或 {fallback_path}")

    MODEL.load_state_dict(torch.load(model_path, map_location=DEVICE))
    MODEL.to(DEVICE)
    MODEL.eval()
    print(f"✅ 模型已加载完毕: {model_path}")


# === 推理逻辑 ===
def run_inference(input_data):
    """执行单次推理"""
    # 1. 占位符处理：为数据添加一个假的 predicate 标签，防止 preprocess 报错
    # 这里我们取映射表里的第一个键作为占位符
    dummy_key = list(PREDICATE2ID.keys())[0]
    input_data['predicate'] = dummy_key

    # 如果 preprocess 需要 relation 字段而不是 predicate，请取消下面这行的注释
    input_data['relation'] = dummy_key

    # 2. 转为 JSON 字符串列表 (模拟文件读取)
    json_str = json.dumps(input_data, ensure_ascii=False)
    data_list = [json_str]

    try:
        # 调用 preprocess.Dataset
        # 注意：每次请求都创建 Dataset 可能会有轻微的性能开销(Tokenizer加载)，
        # 但这是为了不修改原始 preprocess.py 代码的最稳妥方式。
        dataset = process.Dataset(
            data_list,
            PREDICATE2ID,
            DEVICE,
            CONFIGS['pretrain_model_path'],
            CONFIGS['max_len']
        )

        if len(dataset) == 0:
            return None, "数据预处理后为空，请检查输入长度或格式"

        dataloader = DataLoader(dataset, batch_size=1, shuffle=False, collate_fn=dataset.collate_fn)
    except Exception as e:
        return None, f"数据预处理失败: {str(e)}"

    # 3. 模型前向传播
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            e1_mask = batch["e1_mask"].to(DEVICE)
            e2_mask = batch["e2_mask"].to(DEVICE)
            e1_pos = batch["e1_pos"].to(DEVICE)
            e2_pos = batch["e2_pos"].to(DEVICE)

            relation_logits = MODEL(
                input_ids, attention_mask,
                e1_mask, e2_mask,
                e1_pos, e2_pos
            )

            pred_id = torch.argmax(relation_logits, dim=-1).item()
            pred_relation = ID2TYPE.get(pred_id, "未知关系")

            return pred_relation, None

    return None, "未执行推理循环"


# === 路由定义 ===

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "healthy", "model_loaded": MODEL is not None})


@app.route('/predict', methods=['POST'])
def predict():
    """
    预测接口
    接受 JSON 格式:
    {
        "text": "...",
        "subject_word": "...",
        "subject_pos": "...",
        "object_word": "...",
        "object_pos": "..."
    }
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.json

    # 简单的参数校验
    required_fields = ["text", "subject_word", "subject_pos", "object_word", "object_pos"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({"error": f"Missing fields: {missing_fields}"}), 400

    try:
        # 执行预测
        result, error = run_inference(data)

        if error:
            return jsonify({"status": "error", "message": error}), 500

        return jsonify({
            "status": "success",
            "data": {
                "text": data["text"],
                "subject": data["subject_word"],
                "object": data["object_word"],
                "predicted_relation": result
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# === 启动入口 ===
if __name__ == '__main__':
    # 先加载模型
    try:
        load_resources()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        exit(1)

    # 启动 Flask
    # host='0.0.0.0' 允许外部访问，port=5000 是端口号
    print("🚀 服务已启动，监听端口 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)