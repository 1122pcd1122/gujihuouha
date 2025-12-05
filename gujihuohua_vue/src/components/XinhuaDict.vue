<template>
  <div class="dict-container fade-in">
    <div class="header-row">
      <h2 class="gufeng-title">中华新华典藏</h2>
      <div class="header-actions">
        <div class="dict-tabs">
          <span :class="{active: currentType==='idiom'}" @click="switchType('idiom')">成语</span>
          <span :class="{active: currentType==='word'}" @click="switchType('word')">汉字</span>
          <span :class="{active: currentType==='ci'}" @click="switchType('ci')">词语</span>
          <span :class="{active: currentType==='xiehouyu'}" @click="switchType('xiehouyu')">歇后语</span>
        </div>
        <el-button type="info" link @click="initDatabase" size="small">全库初始化</el-button>
      </div>
    </div>

    <div class="dict-workspace">
      <div class="search-panel">
        <div class="search-box">
          <el-input
              v-model="keyword"
              :placeholder="placeholderText"
              class="ancient-search"
              clearable
              @input="handleInput"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>

        <div class="result-list custom-scrollbar" v-loading="loading">
          <div v-if="resultList.length === 0" class="empty-list">
            {{ keyword ? '未寻得相关条目' : '请输入关键词检索' }}
          </div>

          <div
              v-for="item in resultList"
              :key="item.id"
              class="list-item"
              :class="{ active: currentItem && currentItem.id === item.id }"
              @click="currentItem = item"
          >
            <span class="word" v-if="currentType==='idiom'">{{ item.word }}</span>
            <span class="word" v-if="currentType==='word'">{{ item.word }} <span class="sub-py">{{ item.pinyin }}</span></span>
            <span class="word" v-if="currentType==='ci'">{{ item.ci }}</span>
            <span class="word" v-if="currentType==='xiehouyu'">{{ item.riddle }}</span>

            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <div class="detail-panel">
        <div class="book-page">
          <div class="page-texture">
            <div v-if="!currentItem" class="empty-book">
              <div class="seal-bg">{{ typeSeal }}</div>
              <p>查阅古今 · {{ typeName }}篇</p>
            </div>

            <div v-else class="entry-content custom-scrollbar">

              <template v-if="currentType === 'idiom'">
                <div class="entry-header">
                  <h1 class="entry-word">{{ currentItem.word }}</h1>
                  <div class="entry-pinyin">[{{ currentItem.pinyin }}]</div>
                </div>
                <div class="entry-section">
                  <div class="section-title"><span class="mark">▍</span>释义</div>
                  <p class="section-text">{{ currentItem.explanation }}</p>
                </div>
                <div class="entry-section" v-if="currentItem.derivation">
                  <div class="section-title"><span class="mark">▍</span>出处</div>
                  <p class="section-text derivation">{{ currentItem.derivation }}</p>
                </div>
                <div class="entry-section" v-if="currentItem.example">
                  <div class="section-title"><span class="mark">▍</span>例句</div>
                  <p class="section-text">{{ currentItem.example }}</p>
                </div>
              </template>

              <template v-if="currentType === 'word'">
                <div class="word-header-box">
                  <div class="big-word">{{ currentItem.word }}</div>
                  <div class="word-meta">
                    <p>拼音：{{ currentItem.pinyin }}</p>
                    <p>部首：{{ currentItem.radicals }} | 笔画：{{ currentItem.strokes }}</p>
                    <p v-if="currentItem.oldword">繁体/旧字：{{ currentItem.oldword }}</p>
                  </div>
                </div>
                <div class="entry-section">
                  <div class="section-title"><span class="mark">▍</span>基本释义</div>
                  <p class="section-text" style="white-space: pre-wrap;">{{ currentItem.explanation }}</p>
                </div>
              </template>

              <template v-if="currentType === 'ci'">
                <div class="entry-header">
                  <h1 class="entry-word">{{ currentItem.ci }}</h1>
                </div>
                <div class="entry-section">
                  <div class="section-title"><span class="mark">▍</span>解释</div>
                  <p class="section-text">{{ currentItem.explanation }}</p>
                </div>
              </template>

              <template v-if="currentType === 'xiehouyu'">
                <div class="xiehouyu-box">
                  <div class="riddle-box">
                    <div class="label">谜面</div>
                    <div class="content">{{ currentItem.riddle }}</div>
                  </div>
                  <div class="answer-box">
                    <div class="label">谜底</div>
                    <div class="content">{{ currentItem.answer }}</div>
                  </div>
                </div>
              </template>

            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, computed } from 'vue'
import { Search, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const currentType = ref('idiom')
const keyword = ref('')
const loading = ref(false)
const resultList = ref([])
const currentItem = ref(null)

const typeMap = {
  idiom: { name: '成语', seal: '典', place: '搜成语（如：卧薪尝胆）' },
  word: { name: '汉字', seal: '字', place: '搜汉字（如：秦）' },
  ci: { name: '词语', seal: '辞', place: '搜词语（如：须髯）' },
  xiehouyu: { name: '歇后语', seal: '趣', place: '搜歇后语（如：诸葛亮）' }
}

const typeName = computed(() => typeMap[currentType.value].name)
const typeSeal = computed(() => typeMap[currentType.value].seal)
const placeholderText = computed(() => typeMap[currentType.value].place)

const switchType = (type) => {
  currentType.value = type
  keyword.value = ''
  resultList.value = []
  currentItem.value = null
}

let timer = null
const handleInput = () => {
  if (timer) clearTimeout(timer)
  timer = setTimeout(handleSearch, 500)
}

const handleSearch = async () => {
  if (!keyword.value) { resultList.value = []; return }
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8080/api/dict/search', {
      params: { type: currentType.value, keyword: keyword.value }
    })
    resultList.value = res.data
    if (resultList.value.length > 0) currentItem.value = resultList.value[0]
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const initDatabase = async () => {
  // 1. 使用 ElMessage 直接调用，设置 type: 'info', duration: 0 (不自动关闭)
  const loadingMsg = ElMessage({
    message: '正在导入全量数据（约30万条），请耐心等待...',
    type: 'info',
    duration: 0, // 设置为0则不会自动关闭
    showClose: false,
    grouping: true
  })

  try {
    const res = await axios.post('http://localhost:8080/api/dict/init')

    // 2. 手动关闭之前的 loading 消息
    loadingMsg.close()

    ElMessage.success(res.data)
  } catch (e) {
    // 3. 发生错误也要关闭
    loadingMsg.close()

    // 打印错误详情以便调试
    console.error(e)
    const errorMsg = e.response?.data?.error || '导入超时或失败，请查看后台日志'
    ElMessage.error(errorMsg)
  }
}
</script>

<style scoped>
/* 复用之前的古风样式框架 */
.dict-container { height: 100%; display: flex; flex-direction: column; font-family: "KaiTi", serif; }
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #e6dcc8; padding-bottom: 10px; }
.gufeng-title { color: #5e482d; border-left: 4px solid #8e3e3e; padding-left: 15px; margin: 0; }

/* 顶部 Tab 样式 */
.dict-tabs { display: flex; gap: 20px; font-size: 16px; color: #909399; }
.dict-tabs span { cursor: pointer; padding-bottom: 5px; transition: all 0.3s; }
.dict-tabs span.active { color: #8e3e3e; font-weight: bold; border-bottom: 2px solid #8e3e3e; }
.dict-tabs span:hover { color: #5e482d; }

.dict-workspace { flex: 1; display: flex; gap: 20px; overflow: hidden; }
.search-panel { width: 300px; display: flex; flex-direction: column; background: #fff; border-radius: 4px; border: 1px solid #e6dcc8; }
.search-box { padding: 15px; background: #fcf9f2; border-bottom: 1px solid #e6dcc8; }
.ancient-search :deep(.el-input__wrapper) { background-color: #fff; box-shadow: 0 0 0 1px #dcc8a6 inset; }
.result-list { flex: 1; overflow-y: auto; padding: 10px 0; }
.list-item { padding: 12px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s; border-bottom: 1px dashed #f5f5f5; }
.list-item:hover, .list-item.active { background-color: #fdf6ec; color: #8e3e3e; }
.sub-py { font-size: 12px; color: #999; margin-left: 8px; }
.empty-list { text-align: center; color: #999; margin-top: 50px; font-size: 14px; }

/* 右侧详情 - 样式增强 */
.detail-panel {
  flex: 1;
  background: #2b303b;
  padding: 20px;
  border-radius: 4px;
  display: flex;
  /* 删掉了 justify-content: center; 让它自然撑开 */
}

/* 书页主体 */
.book-page {
  width: 100%;
  /* 删掉了 max-width: 800px; 让它横向撑满 */
  background: #fffdf6;
  border-radius: 4px;
  box-shadow: 0 0 20px rgba(0,0,0,0.3);
  display: flex;
  flex-direction: column;
}
.page-texture { flex: 1; margin: 20px; border: 1px solid #dcc8a6; padding: 40px; background-image: linear-gradient(90deg, transparent 95%, rgba(220, 200, 166, 0.2) 95%); background-size: 40px 100%; display: flex; flex-direction: column; }

.empty-book { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #c0c4cc; }
.seal-bg { width: 80px; height: 80px; background: #f4f4f5; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 32px; color: #dcdfe6; margin-bottom: 15px; font-family: "KaiTi"; border: 2px solid #e4e7ed; }

/* 汉字专属样式 */
.word-header-box { display: flex; align-items: center; border-bottom: 1px solid #8e3e3e; padding-bottom: 20px; margin-bottom: 20px; }
.big-word { font-size: 80px; font-weight: bold; color: #333; margin-right: 30px; line-height: 1; }
.word-meta p { margin: 5px 0; font-size: 16px; color: #666; }

/* 歇后语专属样式 */
.xiehouyu-box { display: flex; flex-direction: column; gap: 30px; margin-top: 20px; }
.riddle-box, .answer-box { background: rgba(205, 171, 132, 0.1); padding: 20px; border-radius: 8px; border: 1px dashed #dcc8a6; }
.riddle-box .label, .answer-box .label { font-size: 14px; color: #8e3e3e; margin-bottom: 10px; font-weight: bold; }
.riddle-box .content { font-size: 24px; color: #333; font-weight: bold; }
.answer-box .content { font-size: 24px; color: #b8860b; font-weight: bold; }

/* 通用条目 */
.entry-content { flex: 1; overflow-y: auto; }
.entry-header { border-bottom: 1px solid #8e3e3e; padding-bottom: 15px; margin-bottom: 25px; text-align: center; }
.entry-word { font-size: 36px; color: #333; margin: 0; letter-spacing: 5px; }
.entry-pinyin { font-size: 18px; color: #888; margin-top: 10px; font-family: Arial, sans-serif; }
.entry-section { margin-bottom: 30px; }
.section-title { font-size: 16px; color: #8e3e3e; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; }
.mark { margin-right: 5px; font-size: 12px; }
.section-text { font-size: 18px; line-height: 1.8; color: #2c3e50; text-align: justify; margin: 0; }
.derivation { color: #555; font-style: italic; }

.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #dcc8a6; border-radius: 3px; }
.fade-in { animation: fadeIn 0.6s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>