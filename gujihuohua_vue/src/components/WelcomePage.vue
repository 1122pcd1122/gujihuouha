<template>
  <div class="welcome-container">
    <div class="bg-layer"></div>
    <div class="content-layer">
      <div class="vertical-text-box fade-in-up">
        <div class="seal">古籍</div>
        <h1 class="main-title">大数据驱动</h1>
        <h1 class="main-title indent">知识图谱构建</h1>
        <div class="sub-title">暨智能分析平台</div>
      </div>

      <div class="enter-btn-box fade-in-delay">
        <div class="enter-btn" @click="$emit('enter')">
          <span class="btn-text">进入系统</span>
          <div class="btn-border"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
defineEmits(['enter'])
</script>


<style scoped>
.welcome-container {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background-color: #2b303b;
  overflow: hidden;
  z-index: 9999;
  font-family: "KaiTi", serif;
}

.bg-layer {
  position: absolute;
  width: 100%; height: 100%;
  background-image: url("https://img.js.design/assets/img/64dc68c634075a09e7308747.jpg"); /* 示例古风水墨背景 */
  background-size: cover;
  background-position: center;
  opacity: 0.4;
  filter: grayscale(30%);
}

.content-layer {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.vertical-text-box {
  display: flex;
  flex-direction: row-reverse; /* 竖排文字从右向左 */
  gap: 40px;
  color: #e0d6c3;
  margin-bottom: 80px;
}

.main-title {
  writing-mode: vertical-rl;
  font-size: 64px;
  letter-spacing: 10px;
  margin: 0;
  text-shadow: 4px 4px 10px rgba(0,0,0,0.8);
}

.indent { margin-top: 80px; } /* 第二行错落感 */

.sub-title {
  writing-mode: vertical-rl;
  font-size: 24px;
  color: #cdab84;
  letter-spacing: 4px;
  margin-right: 20px;
  border-left: 1px solid #8e3e3e;
  padding-left: 10px;
}

.seal {
  width: 60px; height: 60px;
  background: #8e3e3e;
  color: #fff;
  font-size: 28px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 4px;
  border: 2px solid #682b2b;
  align-self: flex-start;
  box-shadow: 0 4px 10px rgba(0,0,0,0.5);
}

.enter-btn {
  position: relative;
  width: 180px; height: 60px;
  display: flex; justify-content: center; align-items: center;
  cursor: pointer;
  transition: all 0.5s;
}

.btn-text {
  font-size: 20px; color: #cdab84; letter-spacing: 5px; z-index: 2;
}

.btn-border {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  border: 1px solid #cdab84;
  transform: scale(0.9);
  transition: all 0.5s;
}

.enter-btn:hover .btn-border {
  transform: scale(1);
  background: rgba(205,171,132,0.1);
  box-shadow: 0 0 20px rgba(205,171,132,0.3);
}

.fade-in-up { animation: fadeInUp 1.5s ease-out; }
.fade-in-delay { animation: fadeIn 2s ease-out 0.5s backwards; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(50px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>