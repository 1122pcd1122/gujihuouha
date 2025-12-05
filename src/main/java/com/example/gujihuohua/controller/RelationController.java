package com.example.gujihuohua.controller;

import com.alibaba.fastjson.JSONObject;
import com.example.gujihuohua.entity.RelationFact;
import com.example.gujihuohua.service.AiModelService;
import com.example.gujihuohua.service.RelationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/analysis/relation")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class RelationController {

    private final RelationService relationService;
    private final AiModelService aiModelService;

    // ================== 单句分析 (保持不变) ==================
    @PostMapping("/predict")
    public ResponseEntity<?> predictRelation(@RequestBody Map<String, Object> params) {
        RelationFact fact = new RelationFact();
        if (params.get("text") != null) fact.setText((String) params.get("text"));
        if (params.get("subject_word") != null) fact.setSubjectWord((String) params.get("subject_word"));
        if (params.get("subject_pos") != null) fact.setSubjectPos(String.valueOf(params.get("subject_pos")));
        if (params.get("object_word") != null) fact.setObjectWord((String) params.get("object_word"));
        if (params.get("object_pos") != null) fact.setObjectPos(String.valueOf(params.get("object_pos")));

        JSONObject result = aiModelService.predictRelationForSingle(fact);
        if (result != null && "success".equals(result.getString("status"))) {
            return ResponseEntity.ok(result);
        } else {
            return ResponseEntity.internalServerError().body(result);
        }
    }

    @PostMapping("/auto_predict")
    public ResponseEntity<?> autoPredictRelation(@RequestBody Map<String, String> params) {
        return ResponseEntity.ok(aiModelService.autoExtractPipeline(params.get("text")));
    }

    // ================== 批量分析 (内存版) ==================

    /**
     * 1. 启动分析 (调用内存版 Service)
     */
    @PostMapping("/run_async")
    public ResponseEntity<?> runAnalysisAsync(@RequestBody Map<String, Long> params) {
        Long id = params.get("id");
        relationService.runAnalysisInMemory(id); // 改调内存版方法
        return ResponseEntity.ok("Task Started");
    }

    /**
     * 2. 查询进度
     */
    @GetMapping("/progress/{id}")
    public ResponseEntity<?> getProgress(@PathVariable Long id) {
        return ResponseEntity.ok(relationService.getProgress(id));
    }

    /**
     * 3. 获取结果 (内存分页)
     * 因为数据在 List 里，我们需要手动 subList
     */
    @GetMapping("/result/{id}")
    public ResponseEntity<Map<String, Object>> getResultPage(
            @PathVariable Long id,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "50") int size
    ) {
        // 1. 获取全量数据
        List<RelationFact> allFacts = relationService.getResultFromMemory(id);

        // 2. 手动分页
        int total = allFacts.size();
        int fromIndex = (page - 1) * size;
        int toIndex = Math.min(fromIndex + size, total);

        List<RelationFact> pageRecords = new ArrayList<>();
        if (fromIndex < total && fromIndex >= 0) {
            pageRecords = allFacts.subList(fromIndex, toIndex);
        }

        // 3. 构造返回结构 (模拟 MyBatis Plus 的 Page 结构)
        Map<String, Object> result = new HashMap<>();
        result.put("records", pageRecords);
        result.put("total", total);
        result.put("size", size);
        result.put("current", page);

        return ResponseEntity.ok(result);
    }

}