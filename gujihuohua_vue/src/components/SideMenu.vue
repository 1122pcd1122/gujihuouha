<template>
  <div class="sidebar">
    <div class="logo-area">
      <div class="logo-seal">古籍</div>
      <div class="logo-text">
        <div class="main-title">智·析</div>
        <div class="sub-title">知识图谱平台</div>
      </div>
    </div>

    <ul class="nav-menu custom-scrollbar">
      <li class="menu-group-title">数据层</li>
      <li :class="{ active: activeView === 'process' }" @click="$emit('change-view', 'process')">
        <el-icon class="menu-icon"><EditPen /></el-icon> 文本清洗工作台
      </li>
      <li :class="{ active: activeView === 'library' }" @click="$emit('change-view', 'library')">
        <el-icon class="menu-icon"><Collection /></el-icon> 珍藏语料库
      </li>

      <li class="menu-group-title">分析层</li>
      <li :class="{ active: activeView === 'ner' }" @click="$emit('change-view', 'ner')">
        <el-icon class="menu-icon"><PriceTag /></el-icon> 命名实体识别
      </li>
      <li :class="{ active: activeView === 'relation' }" @click="$emit('change-view', 'relation')">
        <el-icon class="menu-icon"><Connection /></el-icon> 人物关系抽取
      </li>
      <li :class="{ active: activeView === 'event' }" @click="$emit('change-view', 'event')">
        <el-icon class="menu-icon"><Timer /></el-icon> 事件脉络抽取
      </li>
      <li :class="{ active: activeView === 'portrait' }" @click="$emit('change-view', 'portrait')">
        <el-icon class="menu-icon"><User /></el-icon> 人物画像生成
      </li>
    </ul>

    <ul class="nav-menu custom-scrollbar">
      <li class="menu-group-title">典籍工具</li>

      <li :class="{ active: activeView === 'dict' }" @click="$emit('change-view', 'dict')">
        <el-icon class="menu-icon"><Reading /></el-icon> 中华词典检索
      </li>

      <li :class="{ active: activeView === 'dict_table' }" @click="$emit('change-view', 'dict_table')">
        <el-icon class="menu-icon"><List /></el-icon> 典籍数据总览
      </li>

    </ul>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
// 1. 在这里补充引入 'Reading' 图标
import { EditPen, Collection, PriceTag, Connection, Timer, User, Reading ,List} from '@element-plus/icons-vue'

defineProps(['activeView'])
defineEmits(['change-view'])
</script>

<style scoped>
/* 保持原有的 sidebar 样式，新增一点样式 */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #2b303b 0%, #1a1d24 100%);
  color: #e0d6c3;
  display: flex; flex-direction: column; z-index: 10;
}
.logo-area { height: 100px; display: flex; align-items: center; padding: 0 20px; background: rgba(0,0,0,0.1); border-bottom: 1px solid #3d4450; }
.logo-seal { width: 48px; height: 48px; background-color: #a83b3b; color: #fff; font-size: 24px; font-weight: bold; border: 2px solid #852b2b; margin-right: 15px; display: flex; justify-content: center; align-items: center; border-radius: 4px; font-family: "KaiTi"; }
.logo-text .main-title { font-size: 22px; color: #cdab84; letter-spacing: 2px; }
.logo-text .sub-title { font-size: 12px; color: #8a96a3; }

.nav-menu { list-style: none; padding: 20px 0; margin: 0; overflow-y: auto; flex: 1; }
.menu-group-title { padding: 15px 20px 5px; font-size: 12px; color: #5c6b7f; letter-spacing: 1px; }
.nav-menu li:not(.menu-group-title) { padding: 15px 30px; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; font-size: 15px; color: #909399; }
.nav-menu li:hover { color: #e0d6c3; background: rgba(255,255,255,0.03); }
.nav-menu li.active { color: #cdab84; background: linear-gradient(90deg, rgba(205,171,132,0.1) 0%, transparent 100%); border-right: 3px solid #cdab84; }
.menu-icon { margin-right: 10px; font-size: 16px; }
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #3d4450; }
</style>