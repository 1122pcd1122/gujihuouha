package com.example.gujihuohua.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("xinhua_idiom")
public class XinhuaIdiom {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String word;
    private String pinyin;
    private String abbreviation;
    private String derivation;
    private String explanation;
    private String example;
}