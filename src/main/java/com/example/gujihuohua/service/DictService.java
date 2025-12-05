package com.example.gujihuohua.service;

import com.alibaba.fastjson.JSON;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.gujihuohua.entity.*;
import com.example.gujihuohua.mapper.*;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.util.FileCopyUtils;

import java.nio.charset.StandardCharsets;
import java.util.List;

@Service
@RequiredArgsConstructor
public class DictService {

    private final XinhuaIdiomMapper idiomMapper;
    private final XinhuaWordMapper wordMapper;
    private final XinhuaCiMapper ciMapper;
    private final XinhuaXiehouyuMapper xiehouyuMapper;

    // 通用导入方法
    public String importAll() {
        StringBuilder sb = new StringBuilder();
        sb.append(importJson("rawData/idiom.json", XinhuaIdiom.class, idiomMapper));
        sb.append(importJson("rawData/word.json", XinhuaWord.class, wordMapper));
        sb.append(importJson("rawData/xiehouyu.json", XinhuaXiehouyu.class, xiehouyuMapper));
        // 词语数据量大，慎重导入
        sb.append(importJson("rawData/ci.json", XinhuaCi.class, ciMapper));
        return sb.toString();
    }

    private <T> String importJson(String fileName, Class<T> clazz, com.baomidou.mybatisplus.core.mapper.BaseMapper<T> mapper) {
        if (mapper.selectCount(null) > 0) return fileName + " 已存在; ";
        try {
            ClassPathResource resource = new ClassPathResource(fileName);
            byte[] bytes = FileCopyUtils.copyToByteArray(resource.getInputStream());
            String json = new String(bytes, StandardCharsets.UTF_8);
            List<T> list = JSON.parseArray(json, clazz);
            // 分批插入防止内存溢出
            int batchSize = 1000;
            for (int i = 0; i < list.size(); i += batchSize) {
                int end = Math.min(i + batchSize, list.size());
                List<T> subList = list.subList(i, end);
                subList.forEach(mapper::insert); // 简化写法，实际项目建议用 saveBatch
            }
            return fileName + " 导入 " + list.size() + " 条; ";
        } catch (Exception e) {
            e.printStackTrace();
            return fileName + " 失败; ";
        }
    }
}