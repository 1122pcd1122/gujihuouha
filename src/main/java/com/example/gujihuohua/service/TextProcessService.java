package com.example.gujihuohua.service;

import com.example.gujihuohua.data.SentenceResult;
import com.example.gujihuohua.data.TextProcessRequest;
import com.github.houbb.opencc4j.util.ZhConverterUtil;
import org.mozilla.universalchardet.UniversalDetector;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
public class TextProcessService {

    /**
     * 主处理流程
     */
    public List<SentenceResult> processText(TextProcessRequest request, byte[] fileBytes) {
        String processingText;

        // ================= 1. 智能编码识别与解码 =================
        if (fileBytes != null && fileBytes.length > 0) {
            String detectedCharset = detectCharset(fileBytes);
            Charset charset = detectedCharset != null ? Charset.forName(detectedCharset) : StandardCharsets.UTF_8;
            processingText = new String(fileBytes, charset);
        } else {
            processingText = request.getContent();
        }

        if (processingText == null) processingText = "";

        // ================= 2. 去空规整 (优先执行) =================
        if (request.isStandardizeSpaces()) {
            // 正则解释：[ \t\u3000\u00A0]+ 匹配 空格、Tab、中文全角空格、不间断空格
            // 注意：这里故意不匹配 \n (换行符)，是为了保留“按换行切分”的能力
            processingText = processingText.replaceAll("[ \\t\\u3000\\u00A0]+", "");

            // 如果用户没有选择“按换行切分”，我们可以考虑把换行符也去掉，变成一整段
            // 但为了逻辑安全，通常建议保留段落结构，由分句规则决定是否断开
        }

        // ================= 3. 繁简转换 =================
        if (request.isConvertToSimplified()) {
            processingText = ZhConverterUtil.toSimple(processingText);
        }

        // ================= 4. 深度清洗 (去括号) =================
        if (request.isRemoveBrackets()) {
            // 去除 (abc) 和 （中文） 及其内部内容
            processingText = processingText.replaceAll("（.*?）", "").replaceAll("\\(.*?\\)", "");
        }

        // 清理现代标点 (可选)
        if (request.isClearModernPunctuation()) {
            processingText = processingText.replaceAll("[《》“”‘’]", "");
        }

        // ================= 5. 执行分句 =================
        List<String> rawSentences = splitSentences(request, processingText);

        // ================= 6. 封装结果 =================
        List<SentenceResult> results = new ArrayList<>();
        // 预览模式下限制返回条数，防止前端卡顿
        int limit = request.isPreview() && rawSentences.size() > 50 ? 50 : rawSentences.size();

        for (int i = 0; i < limit; i++) {
            results.add(new SentenceResult(i + 1, rawSentences.get(i), rawSentences.get(i).length()));
        }

        return results;
    }

    /**
     * 分句逻辑核心
     */
    private List<String> splitSentences(TextProcessRequest request, String text) {
        StringBuilder splitPattern = new StringBuilder();

        // 1. 按换行切分
        if (request.isSplitByNewline()) {
            splitPattern.append("\n|\r\n|");
        }

        // 2. 按句号切分
        if (request.isSplitByPeriod()) {
            splitPattern.append("。|\\.|！|!|？|\\?|"); // 加上感叹号和问号更合理
        }

        // 3. 按逗号切分 (新增)
        if (request.isSplitByComma()) {
            // 包括：中文逗号，英文逗号，中文分号，英文分号，顿号
            splitPattern.append("，|,|；|;|、|");
        }

        // 4. 自定义分隔符
        if (StringUtils.hasText(request.getCustomSeparator())) {
            splitPattern.append(Pattern.quote(request.getCustomSeparator())).append("|");
        }

        String regex = splitPattern.toString();

        // 如果没有选任何分句规则，直接把整个文本作为一句返回（去除首尾空白）
        if (regex.isEmpty()) {
            List<String> list = new ArrayList<>();
            String trimmed = text.trim();
            if (!trimmed.isEmpty()) {
                list.add(trimmed);
            }
            return list;
        } else {
            // 去掉正则字符串末尾多余的 "|"
            if (regex.endsWith("|")) {
                regex = regex.substring(0, regex.length() - 1);
            }

            // 执行切分
            return Arrays.stream(text.split(regex))
                    .map(String::trim)        // 去除切分后每句前后的残留空白
                    .filter(s -> !s.isEmpty()) // 过滤空行
                    .collect(Collectors.toList());
        }
    }

    /**
     * 辅助方法：编码探测
     */
    private String detectCharset(byte[] bytes) {
        UniversalDetector detector = new UniversalDetector(null);
        detector.handleData(bytes, 0, bytes.length);
        detector.dataEnd();
        String encoding = detector.getDetectedCharset();
        detector.reset();
        return encoding;
    }

    /**
     * 辅助方法：类型推断 (供前端自动识别使用)
     */
    public String autoDetectType(String content) {
        if (content == null) return "未识别";
        if (content.contains("纪") || content.contains("传") || content.contains("本纪")) return "史书";
        if (content.contains("州") || content.contains("县") || content.contains("里")) return "志书";
        if (content.contains("诗") || content.contains("曰") || content.contains("云")) return "笔记";
        return "史书"; // 默认
    }
}