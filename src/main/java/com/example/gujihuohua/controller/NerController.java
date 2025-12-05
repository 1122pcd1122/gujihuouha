package com.example.gujihuohua.controller;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.example.gujihuohua.entity.AncientText;
import com.example.gujihuohua.service.LibraryService;
import com.example.gujihuohua.service.NerService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/analysis/ner") // 路由前缀改为 /api/analysis/ner
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class NerController {

    private final NerService nerService;
    private final LibraryService libraryService;

    @Value("${app.storage.root-path}")
    private String storageRoot;

    /**
     * 1. 启动 NER 异步分析
     * 逻辑：读取文件 -> 解析句子 -> 交给 NerService 异步跑
     */
    @PostMapping("/run_async")
    public ResponseEntity<?> runNerAsync(@RequestBody Map<String, Long> params) {
        Long id = params.get("id");
        AncientText text = libraryService.getById(id);
        if (text == null) return ResponseEntity.notFound().build();

        try {
            // 1. 确定文件路径 (优先读 jsonPath, 其次 rawPath)
            String targetPath = (text.getJsonPath() != null && !text.getJsonPath().isEmpty())
                    ? text.getJsonPath() : text.getRawPath();
            Path filePath = Paths.get(storageRoot, targetPath);

            if (!Files.exists(filePath)) {
                // 回退机制
                filePath = Paths.get(storageRoot, text.getRawPath());
                if (!Files.exists(filePath)) return ResponseEntity.internalServerError().body("找不到语料文件");
            }

            // 2. 读取并解析
            byte[] bytes = Files.readAllBytes(filePath);
            String fileContent = new String(bytes, StandardCharsets.UTF_8).trim();
            List<JSONObject> sentenceList;

            if (fileContent.startsWith("[")) {
                sentenceList = JSON.parseArray(fileContent, JSONObject.class);
            } else {
                sentenceList = new ArrayList<>();
                String[] lines = fileContent.split("\n");
                for (int i = 0; i < lines.length; i++) {
                    if (lines[i].trim().isEmpty()) continue;
                    JSONObject obj = new JSONObject();
                    obj.put("index", i + 1);
                    obj.put("content", lines[i]);
                    sentenceList.add(obj);
                }
            }

            // 3. 启动异步任务
            nerService.runAnalysisAsync(id, sentenceList);
            return ResponseEntity.ok("Task Started");

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError().body("启动失败: " + e.getMessage());
        }
    }

    /**
     * 2. 查询进度
     */
    @GetMapping("/progress/{id}")
    public ResponseEntity<?> getNerProgress(@PathVariable Long id) {
        return ResponseEntity.ok(nerService.getProgress(id));
    }

    /**
     * 3. 获取结果
     */
    @GetMapping("/result/{id}")
    public ResponseEntity<?> getNerResult(@PathVariable Long id) {
        List<JSONObject> result = nerService.getResult(id);
        if (result == null) {
            return ResponseEntity.status(404).body("结果未准备好");
        }
        return ResponseEntity.ok(result);
    }
}