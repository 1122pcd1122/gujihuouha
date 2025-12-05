package com.example.gujihuohua.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.gujihuohua.entity.AncientText;
import com.example.gujihuohua.service.LibraryService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import com.alibaba.fastjson.JSON;

@RestController
@RequestMapping("/api/library")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class LibraryController {

    private final LibraryService libraryService;

    @Value("${app.storage.root-path}")
    private String storageRoot;

    // 1. 获取列表接口 (前端全卷通览就是调用的这个)
    @GetMapping("/list")
    public ResponseEntity<List<AncientText>> getList() {
        List<AncientText> list = libraryService.list(new LambdaQueryWrapper<AncientText>()
                .select(AncientText::getId, AncientText::getTitle, AncientText::getCategory,
                        AncientText::getSentenceCount, AncientText::getCreateTime)
                .orderByDesc(AncientText::getCreateTime));
        return ResponseEntity.ok(list);
    }

    // 2. 保存接口 (来自文本清洗工作台)
    @PostMapping("/save")
    public ResponseEntity<?> saveText(@RequestBody Map<String, Object> payload) {
        try {
            String customTitle = (String) payload.get("title");
            String category = (String) payload.get("category");
            String rawContent = (String) payload.get("rawContent");
            List<?> jsonData = (List<?>) payload.get("data");

            // 构建文件保存逻辑
            String timeStr = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
            String fileNameBase = customTitle + "_" + timeStr;
            String dateFolder = new SimpleDateFormat("yyyy-MM-dd").format(new Date());

            Path dirPath = Paths.get(storageRoot, dateFolder);
            if (!Files.exists(dirPath)) Files.createDirectories(dirPath);

            // 保存 JSON
            String jsonFileName = fileNameBase + ".json";
            Path jsonPath = dirPath.resolve(jsonFileName);
            String jsonString = JSON.toJSONString(jsonData);
            Files.write(jsonPath, jsonString.getBytes(StandardCharsets.UTF_8));

            // 保存 TXT (可选)
            String txtFileName = fileNameBase + ".txt";
            Path txtPath = dirPath.resolve(txtFileName);
            if (rawContent != null) {
                Files.write(txtPath, rawContent.getBytes(StandardCharsets.UTF_8));
            }

            // 入库
            AncientText text = new AncientText();
            text.setTitle(customTitle);
            text.setCategory(category);
            text.setSentenceCount((Integer) payload.get("count"));
            text.setCreateTime(LocalDateTime.now());
            text.setJsonPath(dateFolder + "/" + jsonFileName); // 存相对路径
            text.setRawPath(dateFolder + "/" + txtFileName);

            libraryService.save(text);
            return ResponseEntity.ok("保存成功");

        } catch (IOException e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError().body("存储失败: " + e.getMessage());
        }
    }

    // 3. 获取详情接口 (用于预览)
    @GetMapping("/detail/{id}")
    public ResponseEntity<Map<String, Object>> getDetail(@PathVariable Long id) {
        AncientText text = libraryService.getById(id);
        if (text == null) return ResponseEntity.notFound().build();

        Map<String, Object> response = new HashMap<>();
        response.put("info", text);

        try {
            // 优先读 JSON，没有则读 TXT
            String targetPath = (text.getJsonPath() != null) ? text.getJsonPath() : text.getRawPath();
            Path fullPath = Paths.get(storageRoot, targetPath);

            if (Files.exists(fullPath)) {
                String content = new String(Files.readAllBytes(fullPath), StandardCharsets.UTF_8);
                response.put("processedJson", content);
            } else {
                response.put("processedJson", "[]");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return ResponseEntity.ok(response);
    }

    // 4. 删除接口
    @DeleteMapping("/{id}")
    public ResponseEntity<?> delete(@PathVariable Long id) {
        libraryService.removeById(id);
        return ResponseEntity.ok("已删除");
    }
}