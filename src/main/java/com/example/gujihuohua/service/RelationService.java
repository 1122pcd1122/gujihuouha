package com.example.gujihuohua.service;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.gujihuohua.entity.AncientText;
import com.example.gujihuohua.entity.RelationFact;
import com.example.gujihuohua.mapper.AncientTextMapper;
import com.example.gujihuohua.mapper.RelationFactMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;

@Service
@RequiredArgsConstructor
public class RelationService extends ServiceImpl<RelationFactMapper, RelationFact> {

    private final AncientTextMapper ancientTextMapper;
    private final AiModelService aiModelService;

    @Value("${app.storage.root-path}")
    private String storageRoot;

    // 1. 进度缓存
    private final ConcurrentHashMap<Long, Integer> progressMap = new ConcurrentHashMap<>();

    // 2. 【核心】结果缓存 (内存存储，不走数据库)
    private final ConcurrentHashMap<Long, List<RelationFact>> resultMap = new ConcurrentHashMap<>();

    /**
     * 【重构】异步全量分析 (内存版)
     * 逻辑：读源文件 -> 拆分句子 -> AI流水线 -> 结果存内存
     */
    @Async
    public void runAnalysisInMemory(Long corpusId) {
        progressMap.put(corpusId, 0);
        resultMap.remove(corpusId); // 清除旧缓存

        // 1. 获取语料信息
        AncientText textInfo = ancientTextMapper.selectById(corpusId);
        if (textInfo == null) {
            progressMap.put(corpusId, 100);
            return;
        }

        try {
            // 2. 读取文件 (优先读 jsonPath, 没有则读 rawPath)
            String targetPath = (textInfo.getJsonPath() != null && !textInfo.getJsonPath().isEmpty())
                    ? textInfo.getJsonPath() : textInfo.getRawPath();
            Path filePath = Paths.get(storageRoot, targetPath);

            // 容错回退
            if (!Files.exists(filePath)) filePath = Paths.get(storageRoot, textInfo.getRawPath());

            if (!Files.exists(filePath)) {
                System.err.println("文件不存在");
                progressMap.put(corpusId, 100);
                return;
            }

            // 读取内容
            String content = new String(Files.readAllBytes(filePath), StandardCharsets.UTF_8).trim();
            List<String> sentences = parseSentences(content);

            int total = sentences.size();
            List<RelationFact> analysisResults = new ArrayList<>();

            // 3. 逐句分析
            for (int i = 0; i < total; i++) {
                String sent = sentences.get(i);
                if (sent.length() < 2) continue; // 跳过过短的

                // 调用核心流水线 (NER -> Relation)
                List<RelationFact> facts = aiModelService.autoExtractPipeline(sent);

                if (!facts.isEmpty()) {
                    analysisResults.addAll(facts);
                }

                // 更新进度
                int percent = (int) (((double) (i + 1) / total) * 100);
                progressMap.put(corpusId, percent);
            }

            // 4. 存入内存
            resultMap.put(corpusId, analysisResults);

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            progressMap.put(corpusId, 100);
        }
    }

    /**
     * 辅助：解析句子 (兼容 JSON数组 和 纯文本)
     */
    private List<String> parseSentences(String content) {
        List<String> list = new ArrayList<>();
        if (content.startsWith("[")) {
            try {
                List<JSONObject> jsonList = JSON.parseArray(content, JSONObject.class);
                for (JSONObject obj : jsonList) {
                    // 兼容 content 或 text 字段
                    String s = obj.containsKey("content") ? obj.getString("content") : obj.getString("text");
                    if (s != null && !s.isEmpty()) list.add(s);
                }
            } catch (Exception e) {
                // 解析失败当纯文本处理
                String[] lines = content.split("\n");
                for (String s : lines) if (!s.trim().isEmpty()) list.add(s.trim());
            }
        } else {
            String[] lines = content.split("\n");
            for (String s : lines) if (!s.trim().isEmpty()) list.add(s.trim());
        }
        return list;
    }

    public Integer getProgress(Long corpusId) {
        return progressMap.getOrDefault(corpusId, 0);
    }

    // 获取内存中的结果
    public List<RelationFact> getResultFromMemory(Long corpusId) {
        return resultMap.getOrDefault(corpusId, Collections.emptyList());
    }

    // 废弃的方法占位，防止编译报错
    public Long importJsonDataset(MultipartFile file, String title) { return 0L; }
}