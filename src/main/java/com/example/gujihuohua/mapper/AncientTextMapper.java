package com.example.gujihuohua.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.gujihuohua.entity.AncientText;
import org.apache.ibatis.annotations.Mapper;

@Mapper // 虽然加了 MapperScan 这个注解其实可以省，但建议保留
public interface AncientTextMapper extends BaseMapper<AncientText> {
}