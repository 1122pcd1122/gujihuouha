import json
import os
import torch
from torch.utils.data import DataLoader
import warnings


from EPERR import EPERR
import preprocess as process

# 设置环境变量
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# 忽略警告
warnings.filterwarnings('ignore')


def get_configs():
    """
    硬编码配置参数，替代原有的 yaml 读取
    """
    return {
        # 数据路径 (预测模式下其实只用到 r2id_path)
        'r2id_path': 'relation2id.json',

        # 模型参数
        'pretrain_model_path': '../GuWen-Bert',  # 确保此文件夹存在
        'max_len': 128,
        'hidden_size': 768,
        'dropout': 0.1,
        'num_relations': 15,  # 对应 type_mapping 的长度

        # 训练参数 (预测模式下主要用到 seed)
        'seed': 42,
        'batch_size': 1,  # 单句预测设为1

        # 模型保存路径
        'model_save_dir': '../new_model',

        # 最好指定具体的模型文件名，例如 'best_model.pth' 或 'EPERR-sem+rel+pos.pth'
        'model_filename': 'EPERR-sem+pos+rel.pth'
    }


def get_model(configs, device):
    """初始化并加载模型权重"""
    print(f"正在初始化模型 (Device: {device})...")

    # 初始化模型结构
    model = EPERR(
        model_path=configs['pretrain_model_path'],
        hidden_size=configs['hidden_size'],
        dropout=configs['dropout'],
        num_relations=configs['num_relations']
    )

    # 拼接模型路径
    model_path = os.path.join(configs['model_save_dir'], configs['model_filename'])

    # 如果找不到指定文件名，尝试找 best_model.pth
    if not os.path.exists(model_path):
        fallback_path = os.path.join(configs['model_save_dir'], "best_model.pth")
        if os.path.exists(fallback_path):
            print(f"⚠️ 指定模型 {model_path} 不存在，尝试加载 {fallback_path}")
            model_path = fallback_path

    if os.path.exists(model_path):
        # 加载权重
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval()
        print(f"✅ 成功加载模型权重: {model_path}")
    else:
        raise FileNotFoundError(f"❌ 未找到模型文件: {model_path}")

    return model


def predict_single_sentence(model, input_data, configs, device, predicate2id, id2type):
    """
    对单句进行预测
    """
    # 1. 数据预处理准备
    # 为数据添加一个假的 relation 标签，防止 preprocess.Dataset 报错
    input_data['predicate'] = "父子"

    # === 关键修正 ===
    # preprocess.Dataset 读取文件时使用的是 line.strip()，期望是字符串。
    # 这里我们将字典转换为 json 字符串，放入列表，模拟文件读取的效果。
    json_str = json.dumps(input_data, ensure_ascii=False)
    data_list = [json_str]

    print("正在处理输入文本...")

    try:
        # 调用 preprocess.Dataset
        dataset = process.Dataset(
            data_list,
            predicate2id,
            device,
            configs['pretrain_model_path'],
            configs['max_len']
        )
        dataloader = DataLoader(dataset, batch_size=1, shuffle=False, collate_fn=dataset.collate_fn)
    except Exception as e:
        print(f"❌ 数据预处理失败: {e}")
        return None

    # 2. 模型推理
    with torch.no_grad():
        for batch in dataloader:
            # 将数据移动到设备
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            e1_mask = batch["e1_mask"].to(device)
            e2_mask = batch["e2_mask"].to(device)
            e1_pos = batch["e1_pos"].to(device)
            e2_pos = batch["e2_pos"].to(device)

            # 前向计算
            relation_logits = model(
                input_ids, attention_mask,
                e1_mask, e2_mask,
                e1_pos, e2_pos
            )

            # 获取最大概率的类别索引
            pred_id = torch.argmax(relation_logits, dim=-1).item()

            # 映射回中文
            pred_relation = id2type.get(pred_id, "未知关系")

            return pred_relation


def main():
    # 1. 获取配置
    configs = get_configs()

    # 2. 设置设备和随机种子
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(configs['seed'])
    if torch.cuda.is_available():
        torch.cuda.manual_seed(configs['seed'])

    # 3. 准备映射关系 (Relation Mapping)
    # 优先读取文件，如果文件不存在则使用硬编码
    if os.path.exists(configs['r2id_path']):
        predicate2id = process.read_id(configs['r2id_path'])
    else:
        print(f"⚠️ 未找到 {configs['r2id_path']}，使用内置映射表。")
        # 必须确保这里的 default_mapping 与你训练时的 ID 对应关系一致！
        predicate2id = {
            "为官": 0, "依附": 1, "父子": 2, "同名于": 3, "军事对抗": 4,
            "杀害": 5, "兄弟": 6, "出生地": 7, "葬地": 8, "朋友": 9,
            "隶属于": 10, "去往": 11, "作": 12, "位于": 13, "升迁": 14
        }

    # 创建 id 转文字的映射
    id2type = {v: k for k, v in predicate2id.items()}

    # 4. 加载模型
    try:
        model = get_model(configs, device)
    except Exception as e:
        print(e)
        return

    # ==========================================
    # 5. 定义待预测数据 (在此处修改输入)
    # ==========================================
    target_data = {
        "text": "辛巳，立皇子冏为清河王。吴将诸葛瑾、张霸等寇襄阳，抚军大将军司马宣王讨破之，斩霸，征东大将军曹休又破其别将於寻阳",
        "subject_word": "曹休",
        "subject_pos": "nh",
        "object_word": "征东大将军",
        "object_pos": "ns"
    }

    # 6. 执行预测
    print("\n" + "=" * 60)
    print(">>> 正在进行关系抽取预测...")
    print(f"文本: {target_data['text']}")
    print(f"主体: {target_data['subject_word']} ({target_data['subject_pos']})")
    print(f"客体: {target_data['object_word']} ({target_data['object_pos']})")

    result = predict_single_sentence(model, target_data, configs, device, predicate2id, id2type)

    print("-" * 60)
    print(f">>> 预测结果: 【{result}】")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()