package com.example.gujihuohua.entity;
import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

@Data
@TableName("xinhua_ci")
public class XinhuaCi {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String ci;
    private String explanation;
}