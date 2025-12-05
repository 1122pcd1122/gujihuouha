package com.example.gujihuohua.controller;

import com.example.gujihuohua.data.SentenceResult;
import com.example.gujihuohua.data.TextProcessRequest;
import com.example.gujihuohua.service.TextProcessService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/text")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class TextProcessController {

    private final TextProcessService textProcessService;

    // 处理接口
    @PostMapping("/process")
    public ResponseEntity<Map<String, Object>> processText(
            @RequestPart(value = "file", required = false) MultipartFile file,
            @RequestPart("config") TextProcessRequest config) {

        try {
            byte[] fileBytes = null;

            // 1. 优先处理文件上传
            if (file != null && !file.isEmpty()) {
                fileBytes = file.getBytes();
            }
            // 2. 处理直接粘贴 (假设前端传的是UTF-8字符串)
            else if (config.getContent() != null) {
                fileBytes = config.getContent().getBytes(StandardCharsets.UTF_8);
            }

            if (fileBytes == null || fileBytes.length == 0) {
                Map<String, Object> error = new HashMap<>();
                error.put("error", "无有效内容");
                return ResponseEntity.badRequest().body(error);
            }

            // 3. 调用 Service
            List<SentenceResult> results = textProcessService.processText(config, fileBytes);

            Map<String, Object> response = new HashMap<>();
            response.put("totalSentences", results.size());
            response.put("lines", results);

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Object> error = new HashMap<>();
            error.put("error", "处理失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(error);
        }
    }

    // 类型自动探测接口
    @PostMapping("/detect-type")
    public ResponseEntity<String> detectType(@RequestBody Map<String, String> body) {
        return ResponseEntity.ok(textProcessService.autoDetectType(body.get("content")));
    }
}