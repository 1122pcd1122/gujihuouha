package com.example.gujihuohua.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("ancient_text")
public class AncientText {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String title;
    private String category;

    private String rawPath;   // 变更：存储 TXT 路径
    private String jsonPath;  // 变更：存储 JSON 路径

    private Integer sentenceCount;
    private LocalDateTime createTime;
}