package com.example.gujihuohua.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.example.gujihuohua.entity.*;
import com.example.gujihuohua.mapper.*;
import com.example.gujihuohua.service.DictService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Collections; // 必须引入这个
import java.util.List;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;

@RestController
@RequestMapping("/api/dict")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class DictController {

    private final DictService dictService;
    private final XinhuaIdiomMapper idiomMapper;
    private final XinhuaWordMapper wordMapper;
    private final XinhuaCiMapper ciMapper;
    private final XinhuaXiehouyuMapper xiehouyuMapper;

    @PostMapping("/init")
    public ResponseEntity<String> init() {
        return ResponseEntity.ok(dictService.importAll());
    }

    @GetMapping("/search")
    public ResponseEntity<?> search(@RequestParam String type, @RequestParam String keyword) {
        if (keyword == null || keyword.trim().isEmpty()) {
            return ResponseEntity.ok(Collections.emptyList());
        }

        // 限制返回 50 条
        String lastLimit = "LIMIT 50";

        switch (type) {
            case "word": // 查汉字
                return ResponseEntity.ok(wordMapper.selectList(new QueryWrapper<XinhuaWord>().eq("word", keyword).or().like("word", keyword).last(lastLimit)));
            case "ci": // 查词语
                return ResponseEntity.ok(ciMapper.selectList(new QueryWrapper<XinhuaCi>().like("ci", keyword).last(lastLimit)));
            case "xiehouyu": // 查歇后语
                return ResponseEntity.ok(xiehouyuMapper.selectList(new QueryWrapper<XinhuaXiehouyu>().like("riddle", keyword).or().like("answer", keyword).last(lastLimit)));
            case "idiom": // 查成语
            default:
                return ResponseEntity.ok(idiomMapper.selectList(new QueryWrapper<XinhuaIdiom>().like("word", keyword).last(lastLimit)));
        }
    }


    // 3. 分页查询接口 (用于表格页)
    @GetMapping("/page")
    public ResponseEntity<IPage<?>> getPage(
            @RequestParam String type,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        // 创建分页对象
        Page p = new Page<>(page, size);

        switch (type) {
            case "word":
                return ResponseEntity.ok(wordMapper.selectPage(p, null));
            case "ci":
                return ResponseEntity.ok(ciMapper.selectPage(p, null));
            case "xiehouyu":
                return ResponseEntity.ok(xiehouyuMapper.selectPage(p, null));
            case "idiom":
            default:
                return ResponseEntity.ok(idiomMapper.selectPage(p, null));
        }
    }
}