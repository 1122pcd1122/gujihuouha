package com.example.gujihuohua.entity;
import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

@Data
@TableName("xinhua_word")
public class XinhuaWord {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String word;
    private String oldword;
    private String strokes;
    private String pinyin;
    private String radicals;
    private String explanation;
    private String more;
}