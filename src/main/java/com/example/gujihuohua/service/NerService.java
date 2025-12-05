package com.example.gujihuohua.service;

import com.alibaba.fastjson.JSONObject;
import lombok.RequiredArgsConstructor;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;

/**
 * NER 业务服务
 * 职责：处理全卷分析逻辑、管理异步进度、缓存结果
 */
@Service
@RequiredArgsConstructor
public class NerService {

    private final AiModelService aiModelService;

    // 进度缓存: Key=CorpusId, Value=进度(0-100)
    private final ConcurrentHashMap<Long, Integer> progressMap = new ConcurrentHashMap<>();

    // 结果缓存: Key=CorpusId, Value=结果列表
    private final ConcurrentHashMap<Long, List<JSONObject>> resultMap = new ConcurrentHashMap<>();

    /**
     * 【异步】执行全量 NER 分析
     */
    @Async
    public void runAnalysisAsync(Long corpusId, List<JSONObject> sentenceList) {
        // 1. 初始化
        progressMap.put(corpusId, 0);
        List<JSONObject> processedList = new ArrayList<>();
        int total = sentenceList.size();

        if (total == 0) {
            progressMap.put(corpusId, 100);
            return;
        }

        // 2. 循环处理
        for (int i = 0; i < total; i++) {
            JSONObject item = sentenceList.get(i);

            // 获取文本内容 (兼容 content 或 text 字段)
            String sentText = item.getString("content");
            if (sentText == null) sentText = item.getString("text");

            if (sentText != null && !sentText.isEmpty()) {
                // 调用 AIModelService
                JSONObject result = aiModelService.predictNer(sentText);

                // 解析回填结果
                if (result != null && result.getInteger("code") == 200) {
                    JSONObject data = result.getJSONObject("data");
                    item.put("entities", data.getJSONObject("entities"));
                } else {
                    item.put("entities", new HashMap<>());
                }
            }
            processedList.add(item);

            // 3. 更新进度
            int percent = (int) (((double) (i + 1) / total) * 100);
            progressMap.put(corpusId, percent);
        }

        // 4. 任务完成，存入结果
        resultMap.put(corpusId, processedList);
        progressMap.put(corpusId, 100);
    }

    /**
     * 获取进度
     */
    public Integer getProgress(Long corpusId) {
        return progressMap.getOrDefault(corpusId, 0);
    }

    /**
     * 获取结果
     */
    public List<JSONObject> getResult(Long corpusId) {
        return resultMap.get(corpusId);
    }
}