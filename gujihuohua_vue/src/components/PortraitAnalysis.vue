<template>
  <div class="analysis-container fade-in">
    <h2 class="gufeng-title">古籍人物画像生成</h2>

    <div class="portrait-workspace">
      <div class="control-panel">
        <h3>特征提取</h3>
        <el-form label-position="top">
          <el-form-item label="选取人物文本描述">
            <el-input type="textarea" :rows="6" v-model="desc" class="ancient-input"></el-input>
          </el-form-item>
          <div class="tags-box">
            <el-tag class="tag-item">隆准</el-tag>
            <el-tag class="tag-item">龙颜</el-tag>
            <el-tag class="tag-item">美须髯</el-tag>
            <el-tag class="tag-item">左股有七十二黑子</el-tag>
          </div>
          <el-button type="primary" class="generate-btn" @click="generate" :loading="loading">
            <el-icon><Brush /></el-icon> 丹青绘制
          </el-button>
        </el-form>
      </div>

      <div class="canvas-panel">
        <div class="painting-frame">
          <div v-if="!generated" class="placeholder-canvas">
            <span>画师准备中...</span>
          </div>
          <div v-else class="image-result fade-in">
            <img src="https://img.js.design/assets/img/64dc68c634075a09e7308747.jpg" class="real-img" />
            <div class="img-caption">高祖刘邦像</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref } from 'vue'
import { Brush } from '@element-plus/icons-vue'

const desc = ref('高祖为人，隆准而龙颜，美须髯，左股有七十二黑子。')
const loading = ref(false)
const generated = ref(false)

const generate = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    generated.value = true
  }, 2000)
}
</script>

<style scoped>
.analysis-container { height: 100%; display: flex; flex-direction: column; }
.gufeng-title { color: #5e482d; border-left: 4px solid #8e3e3e; padding-left: 15px; margin-bottom: 20px; }
.portrait-workspace { flex: 1; display: flex; gap: 30px; }
.control-panel { width: 350px; background: #fff; padding: 20px; border: 1px solid #e6dcc8; border-radius: 4px; }
.canvas-panel { flex: 1; display: flex; justify-content: center; align-items: center; background: #2b303b; border-radius: 4px; padding: 40px; }

.painting-frame {
  width: 400px; height: 600px; background: #fffdf6; border: 10px solid #5e482d;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5); position: relative;
  display: flex; flex-direction: column;
}
.placeholder-canvas { flex: 1; display: flex; justify-content: center; align-items: center; color: #999; }
.image-result { width: 100%; height: 100%; display: flex; flex-direction: column; }
.real-img { width: 100%; flex: 1; object-fit: cover; filter: sepia(0.3); }
.img-caption { height: 60px; line-height: 60px; text-align: center; font-family: "KaiTi"; font-size: 24px; color: #333; border-top: 1px solid #ccc; }

.ancient-input :deep(.el-textarea__inner) { font-family: "KaiTi"; font-size: 16px; background: #fafafa; }
.tags-box { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
.tag-item { background: #f4f4f5; color: #555; border-color: #e9e9eb; }
.generate-btn { width: 100%; background: #8e3e3e; border-color: #8e3e3e; height: 45px; font-size: 16px; font-family: "KaiTi"; letter-spacing: 4px; }
.fade-in { animation: fadeIn 1s; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>