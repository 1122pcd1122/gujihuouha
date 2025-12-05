
from transformers import AutoModel
from preprocess import *

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

import torch
import torch.nn as nn



class POSEmbedding(nn.Module):
    def __init__(self, num_pos_tags=50, embedding_dim=64):
        super().__init__()
        # num_pos_tags: 词性标签的总数
        # embedding_dim: 词性向量的维度
        self.embedding = nn.Embedding(num_pos_tags, embedding_dim)

    def forward(self, pos_ids):
        # pos_ids: [batch_size, seq_len] 或 [seq_len]
        return self.embedding(pos_ids)  # 输出: [*, seq_len, embedding_dim]


class FixedCrossAttention(nn.Module):
    def __init__(self, d_model=768, d_entity=1664, nhead=8):
        super().__init__()
        # 投影entity_features到与cls相同的维度空间
        self.entity_proj = nn.Linear(d_entity, d_model)

        # 多头注意力层
        self.multihead_attn = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=nhead,
            batch_first=True  # 使用batch_first=True更直观
        )

    def forward(self, cls_embedding, entity_features):
        """
        Args:
            cls_embedding: [batch_size, d_model] (16, 768)
            entity_features: [batch_size, d_entity] (16, 1536)
        Returns:
            attended_cls: [batch_size, d_model]
        """
        # 投影entity_features
        entity_projected = self.entity_proj(entity_features)  # [16, 768]

        # 确保正确的维度:
        # query: [batch_size, seq_len, d_model] (seq_len=1 for cls token)
        # key/value: [batch_size, seq_len, d_model]
        query = cls_embedding.unsqueeze(1)  # [16, 1, 768]
        key = value = entity_projected.unsqueeze(1)  # [16, 1, 768]

        # 计算交叉注意力
        attended, _ = self.multihead_attn(
            query=query,
            key=key,
            value=value
        )

        return attended.squeeze(1)  # 移除seq_len维度 [16, 768]

class FeatureFusion(nn.Module):
    def __init__(self, hidden_size, pos_dim):
        super(FeatureFusion, self).__init__()

        # 1. 词性特征投影层（增强版）
        self.pos_projection = nn.Sequential(
            nn.Linear(pos_dim, hidden_size),  # 线性映射
            nn.LayerNorm(hidden_size),  # 层归一化：稳定训练
            nn.GELU()  # 激活函数：引入非线性
        )

        # 2. 动态权重（取代单一标量alpha）
        # 为实体特征和词性特征分别学习独立的通道级权重
        self.alpha = nn.Parameter(torch.randn(hidden_size))  # 实体特征权重
        self.beta = nn.Parameter(torch.randn(hidden_size))  # 词性特征权重

        # 3. 可选：门控机制（动态特征选择）
        self.gate = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size),  # 输入拼接后的特征
            nn.Sigmoid()  # 输出0-1的门控值
        )

        # 4. 可选：残差连接（保留原始实体性特征）
        self.residual = nn.Linear(hidden_size, hidden_size)

    def forward(self, text_features, pos_features):
        # 步骤1：投影词性特征（对齐维度+归一化）
        pos_features = self.pos_projection(pos_features)

        # 步骤2：通道级加权融合（比单一alpha更灵活）
        # 对alpha和beta做sigmoid，限制权重在[0,1]范围内
        fused = (torch.sigmoid(self.alpha) * text_features +
                 torch.sigmoid(self.beta) * pos_features)

        # 步骤3：门控机制（抑制无关特征）
        gate_values = self.gate(torch.cat([text_features, pos_features], dim=-1))
        fused = fused * gate_values

        # 步骤4：残差连接（缓解梯度消失）
        fused = fused + self.residual(text_features)

        return fused

class FCLayer(nn.Module):
    def __init__(self, input_dim, output_dim, dropout_rate=0., use_activation=True):
        super(FCLayer, self).__init__()
        self.use_activation = use_activation
        self.dropout = nn.Dropout(dropout_rate)
        self.linear = nn.Linear(input_dim, output_dim)
        self.tanh = nn.Tanh()

    def forward(self, x):
        x = self.dropout(x)
        if self.use_activation:
            x = self.tanh(x)
        return self.linear(x)

class EPERR(nn.Module):
    def __init__(self, model_path, hidden_size, dropout, num_relations, max_relative_distance=100):
        """关系分类模型（含相对位置编码）
        参数:
            model_path: 预训练BERT路径
            hidden_size: 隐藏层维度
            dropout: dropout率
            num_relations: 关系类别数
            max_relative_distance: 最大相对距离（默认100）
        """
        super(EPERR, self).__init__()
        self.bert = AutoModel.from_pretrained(model_path)
        self.dropout = dropout
        self.hidden_size = hidden_size
        self.num_relations = num_relations
        self.max_relative_distance = max_relative_distance

        # 词性特征编码层
        self.posEmbedding = POSEmbedding(num_pos_tags=3)
        self.multiHeadCrossAttention = FixedCrossAttention(d_entity=768*2+128)

        # 相对位置编码层（关键新增部分）
        self.relative_position_embeddings = nn.Embedding(
            2 * max_relative_distance + 1,  # 编码范围[-max, max] → [0, 2*max]
            128
        )

        # 融合模块实例化
        self.feature_fusion = FeatureFusion(hidden_size, 64)

        # 全连接层定义（与原始代码一致）
        self.e1_fc_layer = FCLayer(hidden_size, hidden_size, dropout)
        self.e2_fc_layer = FCLayer(hidden_size, hidden_size, dropout)

        # 关系分类头
        self.relation_classifier = FCLayer(hidden_size, num_relations, dropout, use_activation=False)

    def get_relative_positions(self, e1_mask, e2_mask):
        """计算实体间的相对位置（核心新增方法）
        输入:
            e1_mask: [batch_size, seq_len]
            e2_mask: [batch_size, seq_len]
        返回:
            position_indices: [batch_size] 相对位置索引
        """
        # 获取实体起始位置（第一个mask=1的位置）
        e1_pos = e1_mask.float().argmax(dim=1)  # [batch_size]
        e2_pos = e2_mask.float().argmax(dim=1)  # [batch_size]

        # 计算相对距离（e2位置 - e1位置）
        relative_distances = e2_pos - e1_pos

        # 限制距离范围在[-max, max]之间
        clipped_distances = torch.clamp(
            relative_distances,
            -self.max_relative_distance,
            self.max_relative_distance
        )

        # 将距离映射到[0, 2*max]区间作为嵌入索引
        return (clipped_distances + self.max_relative_distance).long()

    def forward(self, input_ids, attention_mask, e1_mask, e2_mask, e1_pos, e2_pos):
        # BERT编码
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        sequence_output = outputs.last_hidden_state
        cls_embedding = sequence_output[:, 0, :]  # [CLS]向量

        # 相对位置编码
        position_indices = self.get_relative_positions(e1_mask, e2_mask)
        rel_pos_embeddings = self.relative_position_embeddings(position_indices)  # [batch_size, hidden_size]

        # 实体词性特征
        e1_pos_emb = self.posEmbedding(e1_pos)
        e2_pos_emb = self.posEmbedding(e2_pos)

        # # 实体文本特征
        e1_text = self.e1_fc_layer(self.entity_average(sequence_output, e1_mask))
        e2_text = self.e2_fc_layer(self.entity_average(sequence_output, e2_mask))


        # # 实体词向量融合词性特征
        e1_features = self.feature_fusion(e1_text, e1_pos_emb)
        e2_features = self.feature_fusion(e2_text, e2_pos_emb)
        # #
        # 实体词向量
        # e1_features = e1_text
        # e2_features = e2_text


        # 实体特征
        combined_features = torch.cat((e1_features, e2_features), dim=-1)

        # 添加位置编码
        combined_features = torch.cat((combined_features, rel_pos_embeddings), dim=-1)

        # 注意力机制与分类
        final_features = self.multiHeadCrossAttention(cls_embedding, combined_features)
        return self.relation_classifier(final_features)

    @staticmethod
    def entity_average(hidden_output, e_mask):
        """实体向量平均池化（与原始代码一致）"""
        e_mask_unsqueeze = e_mask.unsqueeze(1)
        length_tensor = (e_mask != 0).sum(dim=1).unsqueeze(1)
        sum_vector = torch.bmm(e_mask_unsqueeze.float(), hidden_output).squeeze(1)
        return sum_vector / length_tensor.float()
