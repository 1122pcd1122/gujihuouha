package com.example.gujihuohua.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("relation_fact")
public class RelationFact {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long corpusId;      // 关联 ID
    private String text;
    private String subjectWord;
    private String subjectPos;
    private String objectWord;
    private String objectPos;
    private String predicate;   // 这个字段初始可能为空，分析后更新
    private Boolean isProcessed;
    private LocalDateTime createTime;
}