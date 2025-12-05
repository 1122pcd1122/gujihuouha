package com.example.gujihuohua.data;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class SentenceResult {
    private int index;          // 行号/句序
    private String content;     // 句子内容
    private int textLength;     // 字数
}