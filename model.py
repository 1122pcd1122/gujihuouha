import torch
import torch.nn as nn
from torch.nn.utils.rnn import pad_sequence
from transformers import AutoModel
from torchcrf import CRF
from roformer import RoFormerForMaskedLM

# 参数设置
roformer_model_name = "roformer_v2_chinese_char_base"

class GuWenBERTEmbedding(nn.Module):
    def __init__(self, guwenbert_base_path):
        super(GuWenBERTEmbedding, self).__init__()
        # 使用BERT的预训练模型作为基础
        self.bert = AutoModel.from_pretrained(guwenbert_base_path)

    def forward(self, input_ids, attention_mask):
        # 获取BERT的输出
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        # 取最后一层隐藏状态作为嵌入表示
        embeddings = outputs.last_hidden_state
        return embeddings


class EncoderWithMHSA(nn.Module):
    def __init__(self, embedding_dim, num_heads):
        super(EncoderWithMHSA, self).__init__()
        # 使用Multi-Head Self Attention
        self.mhsa = nn.MultiheadAttention(embed_dim=embedding_dim, num_heads=num_heads, batch_first=True)
        self.layer_norm_1 = nn.LayerNorm(embedding_dim)
        self.ffn = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim * 4),
            nn.ReLU(),
            nn.Linear(embedding_dim * 4, embedding_dim)
        )
        self.layer_norm_2 = nn.LayerNorm(embedding_dim)

    def forward(self, embeddings):
        # Multi-Head Self Attention
        attn_output, _ = self.mhsa(embeddings, embeddings, embeddings)
        # Add & Norm
        attn_output = self.layer_norm_1(embeddings + attn_output)
        # Feed Forward Layer
        ffn_output = self.ffn(attn_output)
        # Add & Norm
        output = self.layer_norm_2(attn_output + ffn_output)
        return output

# RoFormer模块
class RoFormerModule(nn.Module):
    def __init__(self, roformer_model_name, embedding_dim, num_heads, dropout=0.3):
        super(RoFormerModule, self).__init__()
        # 加载RoFormer模型
        self.roformer = RoFormerForMaskedLM.from_pretrained(roformer_model_name, output_hidden_states=True)

        # Multi-Head Attention (Cross Attention)
        self.mha = nn.MultiheadAttention(embed_dim=embedding_dim, num_heads=num_heads, batch_first=True)

        # Add & Norm layer
        self.layer_norm = nn.LayerNorm(embedding_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, embeddings, input_token_starts):
        roformer_output = self.roformer(inputs_embeds=embeddings)
        # 获取最后一层的隐藏状态
        roformer_last_hidden_state = roformer_output.hidden_states[-1]

        # 去除[CLS]标签，假设CLS位置是第0个token
        origin_sequence_output = [
            layer[starts.nonzero().squeeze(1)] for layer, starts in zip(roformer_last_hidden_state, input_token_starts)
        ]
        # 去除Encoder输出的[CLS]标签，假设CLS位置是第0个token
        origin_sequence_output_encoder = [
            layer[starts.nonzero().squeeze(1)] for layer, starts in zip(embeddings, input_token_starts)
        ]

        # 将去除CLS后的sequence_output的维度padding到最大长度
        padded_sequence_output = pad_sequence(origin_sequence_output, batch_first=True)
        padded_encoder_output = pad_sequence(origin_sequence_output_encoder, batch_first=True)

        # 交叉注意力机制 (Cross-Attention)，Query来自embedding，Key和Value来自RoFormer输出
        attn_output, _ = self.mha(padded_encoder_output, padded_sequence_output, padded_sequence_output)

        # Add & Norm
        attn_output = self.layer_norm(attn_output + padded_encoder_output)
        attn_output = self.dropout(attn_output)

        return attn_output


class RadicalCNNEncoder(nn.Module):
    def __init__(self, input_dim=256, output_dim=768, conv_channels=512, kernel_size=3, num_heads=8, dropout=0.3):
        super(RadicalCNNEncoder, self).__init__()
        # 一维卷积：在序列维上捕捉上下文，input_dim=256作为输入通道数
        self.conv = nn.Conv1d(in_channels=input_dim,
                              out_channels=conv_channels,
                              kernel_size=kernel_size,
                              padding=(kernel_size - 1) // 2)

        # 池化：在保持序列长度不变的情况下进行最大池化
        self.pool = nn.MaxPool1d(kernel_size=3, stride=1, padding=1)

        # 全连接层：将卷积后的通道维度映射到768
        self.fc = nn.Linear(conv_channels, output_dim)
        # 激活函数
        self.relu = nn.ReLU()
        self.mha = nn.MultiheadAttention(embed_dim=output_dim, num_heads=num_heads, batch_first=True, dropout=dropout)
        # LayerNorm 和 Dropout
        self.layer_norm = nn.LayerNorm(output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, padded_sequence_output):
        # x: (B, L, 256)
        B, L, C = x.size()
        # 调整维度适应 Conv1d: (B, C, L)
        x = x.permute(0, 2, 1)  # (B, 256, L)
        # 卷积 + ReLU
        x = self.relu(self.conv(x))  # (B, 512, L)
        # 最大池化（不改变L的长度）：(B, 512, L)
        x = self.pool(x)
        # 调回 (B, L, 512)
        x = x.permute(0, 2, 1)
        # 全连接层映射到768维度: (B, L, 768)
        x = self.fc(x)
        # Multi-Head Cross-Attention
        attn_output, attn_weights = self.mha(padded_sequence_output, x, x)
        # Add & Norm（残差连接）
        attn_output = self.layer_norm(padded_sequence_output + self.dropout(attn_output))

        return attn_output

class PosCNNEncoder(nn.Module):
    def __init__(self, input_dim=256, output_dim=768, conv_channels=512, kernel_size=3, num_heads=8, dropout=0.3):
        super(PosCNNEncoder, self).__init__()
        # 一维卷积：在序列维上捕捉上下文，input_dim=256作为输入通道数
        self.conv = nn.Conv1d(in_channels=input_dim,
                              out_channels=conv_channels,
                              kernel_size=kernel_size,
                              padding=(kernel_size - 1) // 2)

        # 池化：在保持序列长度不变的情况下进行最大池化
        self.pool = nn.MaxPool1d(kernel_size=3, stride=1, padding=1)

        # 全连接层：将卷积后的通道维度映射到768
        self.fc = nn.Linear(conv_channels, output_dim)
        # 激活函数
        self.relu = nn.ReLU()
        self.mha = nn.MultiheadAttention(embed_dim=output_dim, num_heads=num_heads, batch_first=True, dropout=dropout)
        # LayerNorm 和 Dropout
        self.layer_norm = nn.LayerNorm(output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, padded_sequence_output):
        # x: (B, L, 256)
        B, L, C = x.size()
        # 调整维度适应 Conv1d: (B, C, L)
        x = x.permute(0, 2, 1)  # (B, 256, L)
        # 卷积 + ReLU
        x = self.relu(self.conv(x))  # (B, 512, L)
        # 最大池化（不改变L的长度）：(B, 512, L)
        x = self.pool(x)
        # 调回 (B, L, 512)
        x = x.permute(0, 2, 1)
        # 全连接层映射到768维度: (B, L, 768)
        x = self.fc(x)
        # Multi-Head Cross-Attention
        attn_output, attn_weights = self.mha(padded_sequence_output, x, x)
        # Add & Norm（残差连接）
        attn_output = self.layer_norm(padded_sequence_output + self.dropout(attn_output))

        return attn_output

class GuWenBERTModel(nn.Module):
    def __init__(self, guwenbert_base_path, embedding_dim=768, num_heads=8, num_labels=9, dropout=0.5):
        super(GuWenBERTModel, self).__init__()
        # 初始化GuWenBERT的嵌入层
        self.embedding_layer = GuWenBERTEmbedding(guwenbert_base_path)
        # 初始化Encoder模块，包括Multi-Head Self Attention和前馈网络
        self.encoder = EncoderWithMHSA(embedding_dim, num_heads)
        # Dropout层
        self.dropout = nn.Dropout(dropout)
        # roformer 模块
        self.roformer = RoFormerModule(roformer_model_name, embedding_dim, num_heads, dropout)
        # radical 模块
        self.radical = RadicalCNNEncoder(input_dim=256, output_dim=768, conv_channels=512, kernel_size=3)
        # pos模块
        self.pos = PosCNNEncoder(input_dim=256, output_dim=768, conv_channels=512, kernel_size=3)
        # 融合层的权重参数
        self.alpha = nn.Parameter(torch.tensor(0.33))  # roformer_output 的权重
        self.beta = nn.Parameter(torch.tensor(0.33))   # radical_output 的权重
        self.gamma = nn.Parameter(torch.tensor(0.34))  # pos_output 的权重
        # 全连接层，用于生成标签得分
        self.fc = nn.Linear(embedding_dim * 2, num_labels)
        # CRF层，用于序列标注
        self.crf = CRF(num_labels, batch_first=True)

    def forward(self, input_data, token_type_ids=None, attention_mask=None, labels=None,
                position_ids=None, inputs_embeds=None, head_mask=None):
        input_ids, input_token_starts, radical_emebdding, pos_embedding = input_data
        # 获取嵌入表示
        embeddings = self.embedding_layer(input_ids, attention_mask)

        # 使用Encoder进行处理
        encoded_output = self.encoder(embeddings)

        # 去除[CLS]标签等位置，获得与label对齐的表示
        origin_sequence_output = [layer[starts.nonzero().squeeze(1)] for layer, starts in
                                  zip(encoded_output, input_token_starts)]
        # 将sequence_output的维度padding到最大长度
        padded_sequence_output = pad_sequence(origin_sequence_output, batch_first=True)
        # dropout部分特征
        padded_sequence_output = self.dropout(padded_sequence_output)

        # roformer模块输出
        roformer_output = self.roformer(embeddings, input_token_starts)

        # radical模块输出
        radical_output = self.radical(radical_emebdding,padded_sequence_output)

        # pos，模块输出
        pos_output = self.pos(pos_embedding,padded_sequence_output)

        # fusion融合 roformer_output、radical_output 和 pos_output
        total_weight = self.alpha + self.beta + self.gamma
        alpha_norm = self.alpha / total_weight
        beta_norm = self.beta / total_weight
        gamma_norm = self.gamma / total_weight

        # fusion融合输出
        fused_output = alpha_norm * roformer_output + beta_norm * radical_output + gamma_norm * pos_output

        # concatenate向量
        concatenated_output = torch.cat((padded_sequence_output, fused_output), dim=-1)  # 拼接在最后一个维度
        # 全连接层生成标签得分
        logits = self.fc(concatenated_output)
        outputs = (logits,)

        if labels is not None:
            # 计算损失
            loss_mask = labels.gt(-1)
            loss = -self.crf(logits, labels, mask=loss_mask, reduction='mean')
            outputs = (loss,) + outputs

        # 返回 (loss), scores
        return outputs
