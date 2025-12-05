package com.example.gujihuohua.entity;
import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

@Data
@TableName("xinhua_xiehouyu")
public class XinhuaXiehouyu {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String riddle;
    private String answer;
}