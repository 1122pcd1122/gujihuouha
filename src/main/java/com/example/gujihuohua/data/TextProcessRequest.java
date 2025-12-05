package com.example.gujihuohua.data;

import lombok.Data;

@Data
public class TextProcessRequest {
    // === 基础输入 ===
    private String inputType;   // "paste" 或 "file"
    private String content;     // 文本内容
    private String textCategory;// 史书/志书等

    // === 核心功能开关 ===

    // 1. 繁简转换
    private boolean convertToSimplified;

    // 2. 分句规则
    private boolean splitByPeriod;   // 按句号 (。)
    private boolean splitByNewline;  // 按换行 (\n)
    private boolean splitByComma;    // 【新增】按逗号 (，)
    private String customSeparator;  // 自定义分隔符

    // 3. 清洗规则
    private boolean removeBrackets;     // 去除括号及注释
    private boolean clearModernPunctuation; // 清理现代标点
    private boolean standardizeSpaces;  // 【重点】去空规整

    // 4. 是否预览 (true则只返回前20条)
    private boolean isPreview;
}