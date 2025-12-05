<!--<template>-->
<!--  <div class="task-container fade-in">-->
<!--    <div class="header-row">-->
<!--      <div class="title-box">-->
<!--        <h2 class="gufeng-title">古籍命名实体识别</h2>-->
<!--        <span class="sub-tip" v-if="selectedCorpus">-->
<!--          <el-icon><CollectionTag /></el-icon> {{ selectedCorpus.category }} · {{ selectedCorpus.sentenceCount }}句-->
<!--        </span>-->
<!--      </div>-->
<!--      <div class="header-actions">-->
<!--        <div class="current-corpus" v-if="selectedCorpus">-->
<!--          当前案卷：<span class="highlight">《{{ selectedCorpus.title }}》</span>-->
<!--        </div>-->
<!--        <el-button type="primary" class="gufeng-btn" @click="dialogVisible = true">-->
<!--          <el-icon style="margin-right: 5px"><Document /></el-icon> 调取案卷-->
<!--        </el-button>-->
<!--        <el-button-->
<!--            v-if="selectedCorpus"-->
<!--            type="warning"-->
<!--            class="gufeng-btn action-btn"-->
<!--            @click="startAnalysis"-->
<!--            :disabled="isProcessing"-->
<!--        >-->
<!--          <el-icon style="margin-right: 5px"><VideoPlay /></el-icon> 逐句识别-->
<!--        </el-button>-->
<!--      </div>-->
<!--    </div>-->

<!--    <div class="progress-bar-box" v-if="isProcessing || processPercent > 0">-->
<!--      <el-progress-->
<!--          :percentage="processPercent"-->
<!--          :stroke-width="15"-->
<!--          striped-->
<!--          striped-flow-->
<!--          status="success"-->
<!--      />-->
<!--      <div class="progress-text">{{ processTip }}</div>-->
<!--    </div>-->

<!--    <div class="workspace-box">-->
<!--      <div v-if="!analysisList.length && !isProcessing" class="empty-state">-->
<!--        <div class="empty-icon-bg"><el-icon :size="50" color="#dcc8a6"><Search /></el-icon></div>-->
<!--        <p class="empty-text">请调取案卷并启动分析</p>-->
<!--      </div>-->

<!--      <div v-else class="ner-layout">-->

<!--        <div class="text-section paper-texture">-->
<!--          <div class="section-header">-->
<!--            <span class="label">识别结果 (逐句)</span>-->
<!--            <div class="legend">-->
<!--              <span class="dot person"></span>人名 (PER)-->
<!--              <span class="dot location"></span>地名 (LOC)-->
<!--              <span class="dot office"></span>职官 (ORG)-->
<!--            </div>-->
<!--          </div>-->

<!--          <div class="text-content custom-scrollbar">-->
<!--            <div v-if="analysisList.length === 0" class="processing-tip">正在逐句分析中，请稍候...</div>-->
<!--            <div v-else v-for="(item, index) in analysisList" :key="index" class="sent-row">-->
<!--              <div class="sent-idx">{{ item.index || index + 1 }}</div>-->
<!--              <div class="sent-body" v-html="highlightSentence(item.content, item.entities)"></div>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->

<!--        <div class="viz-section">-->
<!--          <div class="stats-row">-->
<!--            <div class="stat-card">-->
<!--              <div class="stat-val">{{ stats.total }}</div>-->
<!--              <div class="stat-label">实体总数</div>-->
<!--            </div>-->
<!--            <div class="stat-card">-->
<!--              <div class="stat-val">{{ stats.perCount }}</div>-->
<!--              <div class="stat-label">人物总数</div>-->
<!--            </div>-->
<!--          </div>-->

<!--          <div class="chart-box">-->
<!--            <div class="section-header"><span class="label">实体分布</span></div>-->
<!--            <div ref="chartRef" class="chart-container"></div>-->
<!--          </div>-->

<!--          <div class="entity-list-box paper-texture">-->
<!--            <div class="section-header"><span class="label">高频实体榜</span></div>-->
<!--            <div class="list-content custom-scrollbar">-->
<!--              <el-table :data="topEntities" style="width: 100%; background: transparent;" :show-header="false" size="small">-->
<!--                <el-table-column prop="word" label="实体" />-->
<!--                <el-table-column prop="type" label="类型" width="80">-->
<!--                  <template #default="scope">-->
<!--                    <el-tag :class="'tag-' + scope.row.type" effect="dark" size="small" style="border:none">-->
<!--                      {{ typeNameMap[scope.row.type] || scope.row.type }}-->
<!--                    </el-tag>-->
<!--                  </template>-->
<!--                </el-table-column>-->
<!--                <el-table-column prop="count" label="频次" width="60" align="right" />-->
<!--              </el-table>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->

<!--    <el-dialog v-model="dialogVisible" title="从语料库中选取" width="800px" class="ancient-dialog">-->
<!--      <el-table :data="libraryList" v-loading="loading" style="width: 100%" height="400px" stripe @row-click="handleSelect" highlight-current-row>-->
<!--        <el-table-column prop="title" label="篇名" width="250" />-->
<!--        <el-table-column prop="category" label="类型" width="100" />-->
<!--        <el-table-column prop="sentenceCount" label="句数" width="100" />-->
<!--        <el-table-column prop="createTime" label="入库时间" />-->
<!--      </el-table>-->
<!--    </el-dialog>-->
<!--  </div>-->
<!--</template>-->

<!--<script setup>-->
<!--/* eslint-disable no-undef */-->
<!--import { ref ,onMounted, nextTick } from 'vue'-->
<!--import { CollectionTag, Document, VideoPlay, Search } from '@element-plus/icons-vue'-->
<!--import { ElMessage } from 'element-plus'-->
<!--import axios from 'axios'-->
<!--import * as echarts from 'echarts'-->

<!--const dialogVisible = ref(false)-->
<!--const loading = ref(false)-->
<!--const libraryList = ref([])-->
<!--const selectedCorpus = ref(null)-->

<!--// 进度条与数据状态-->
<!--const isProcessing = ref(false)-->
<!--const processPercent = ref(0)-->
<!--const processTip = ref('')-->
<!--let pollTimer = null-->

<!--const analysisList = ref([])-->
<!--const stats = ref({ total: 0, perCount: 0 })-->
<!--const topEntities = ref([])-->
<!--const chartRef = ref(null)-->
<!--let myChart = null-->

<!--const typeNameMap = { PER: '人名', LOC: '地名', OFI: '官职', TIME: '时间' }-->

<!--// 高亮函数-->
<!--const highlightSentence = (text, entitiesMap) => {-->
<!--  if (!text) return ''-->
<!--  if (!entitiesMap) return text-->
<!--  let result = text-->
<!--  const flat = []-->
<!--  for (const [type, words] of Object.entries(entitiesMap)) {-->
<!--    if(Array.isArray(words)) words.forEach(w => flat.push({ word: w, type }))-->
<!--  }-->
<!--  flat.sort((a, b) => b.word.length - a.word.length)-->
<!--  flat.forEach(({ word, type }) => {-->
<!--    const safeWord = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')-->
<!--    const reg = new RegExp(safeWord + '(?![^<]*>)', 'g')-->
<!--    const cls = `ner-${type.toLowerCase()}`-->
<!--    result = result.replace(reg, `<span class="${cls}">${word}</span>`)-->
<!--  })-->
<!--  return result-->
<!--}-->

<!--// 统计函数-->
<!--const calculateStats = (list) => {-->
<!--  let total = 0-->
<!--  let per = 0-->
<!--  const countMap = {}-->
<!--  list.forEach(item => {-->
<!--    if(!item.entities) return-->
<!--    for (const [type, words] of Object.entries(item.entities)) {-->
<!--      if(!Array.isArray(words)) return-->
<!--      total += words.length-->
<!--      if(type === 'PER') per += words.length-->
<!--      words.forEach(w => {-->
<!--        const key = `${w}-${type}`-->
<!--        if(!countMap[key]) countMap[key] = { word: w, type, count: 0 }-->
<!--        countMap[key].count++-->
<!--      })-->
<!--    }-->
<!--  })-->
<!--  stats.value.total = total-->
<!--  stats.value.perCount = per-->
<!--  topEntities.value = Object.values(countMap).sort((a, b) => b.count - a.count).slice(0, 50)-->

<!--  const chartData = []-->
<!--  const typeCounts = { PER:0, LOC:0, ORG:0 }-->
<!--  Object.values(countMap).forEach(v => {-->
<!--    if(typeCounts[v.type] !== undefined) typeCounts[v.type] += v.count-->
<!--    else typeCounts['其他'] = (typeCounts['其他']||0) + v.count-->
<!--  })-->
<!--  for(const k in typeCounts) if(typeCounts[k] > 0) chartData.push({ name: typeNameMap[k]||k, value: typeCounts[k] })-->

<!--  nextTick(() => initChart(chartData))-->
<!--}-->

<!--// === 核心逻辑：异步启动 + 轮询 ===-->
<!--const startAnalysis = async () => {-->
<!--  if (!selectedCorpus.value) return-->
<!--  isProcessing.value = true-->
<!--  processPercent.value = 0-->
<!--  processTip.value = '正在启动 NER 引擎...'-->
<!--  analysisList.value = [] // 清空旧数据-->

<!--  try {-->
<!--    // 1. 启动任务-->
<!--    await axios.post('http://localhost:8080/api/analysis/ner/run_async', {-->
<!--      id: selectedCorpus.value.id-->
<!--    })-->

<!--    // 2. 开始轮询-->
<!--    pollTimer = setInterval(checkProgress, 1000)-->

<!--  } catch (e) {-->
<!--    console.error(e)-->
<!--    isProcessing.value = false-->
<!--    ElMessage.error('任务启动失败')-->
<!--  }-->
<!--}-->

<!--const checkProgress = async () => {-->
<!--  try {-->
<!--    const res = await axios.get(`http://localhost:8080/api/analysis/ner/progress/${selectedCorpus.value.id}`)-->
<!--    const p = res.data-->
<!--    processPercent.value = p-->
<!--    processTip.value = `正在深度解析... ${p}%`-->

<!--    if (p >= 100) {-->
<!--      clearInterval(pollTimer)-->
<!--      isProcessing.value = false-->
<!--      processTip.value = '分析完成，正在渲染结果'-->
<!--      loadResult() // 拉取全量结果-->
<!--    }-->
<!--  } catch (e) {-->
<!--    clearInterval(pollTimer)-->
<!--    isProcessing.value = false-->
<!--    ElMessage.error('进度查询中断')-->
<!--  }-->
<!--}-->

<!--const loadResult = async () => {-->
<!--  try {-->
<!--    const res = await axios.get(`http://localhost:8080/api/analysis/ner/result/${selectedCorpus.value.id}`)-->
<!--    analysisList.value = res.data-->
<!--    calculateStats(res.data)-->
<!--    ElMessage.success(`分析完成，共识别 ${res.data.length} 句`)-->
<!--  } catch (e) {-->
<!--    ElMessage.error('获取结果失败')-->
<!--  }-->
<!--}-->

<!--const initChart = (data) => {-->
<!--  if (!chartRef.value) return-->
<!--  if (myChart) myChart.dispose()-->
<!--  myChart = echarts.init(chartRef.value)-->
<!--  const colors = ['#8e3e3e', '#2b4b64', '#b8860b', '#555']-->
<!--  myChart.setOption({-->
<!--    tooltip: { trigger: 'item' },-->
<!--    color: colors,-->
<!--    series: [{ type: 'pie', radius: ['40%', '70%'], data: data, label: { show: true, formatter: '{b}\n{c}' } }]-->
<!--  })-->
<!--}-->

<!--const fetchLibrary = async () => {-->
<!--  loading.value = true-->
<!--  try {-->
<!--    const res = await axios.get('http://localhost:8080/api/library/list')-->
<!--    libraryList.value = res.data-->
<!--  } catch (e) {-->
<!--    // -&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45; 错误处理逻辑开始 -&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;-->

<!--    // 1. 在控制台打印完整错误，方便开发者调试-->
<!--    console.error('获取语料库失败:', e)-->

<!--    // 2. 尝试提取具体的错误信息-->
<!--    // 优先级：后端返回的 msg -> HTTP 状态码信息 -> 网络错误信息-->
<!--    let errorMessage = '加载失败，请检查网络或后端服务'-->

<!--    if (e.response) {-->
<!--      // 请求已发出，服务器返回了状态码（但不是 2xx）-->
<!--      // 这里的 .data 是后端 Spring Boot 返回的错误 JSON (如果有的话)-->
<!--      // e.response.status 是状态码 (如 500, 404)-->
<!--      errorMessage = e.response.data?.message || e.response.data || `服务器错误 (${e.response.status})`-->
<!--    } else if (e.request) {-->
<!--      // 请求已发出，但没有收到响应 (通常是后端没启动，或跨域问题)-->
<!--      errorMessage = '无法连接到服务器，请检查后端是否启动'-->
<!--    } else {-->
<!--      // 发送请求时出了点问题-->
<!--      errorMessage = e.message-->
<!--    }-->

<!--    // 3. 向用户展示错误提示-->
<!--    ElMessage.error(errorMessage)-->

<!--    // -&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45; 错误处理逻辑结束 -&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;&#45;-->
<!--  } finally { loading.value = false }-->
<!--}-->
<!--const handleSelect = (row) => {-->
<!--  selectedCorpus.value = row-->
<!--  dialogVisible.value = false-->
<!--  analysisList.value = []-->
<!--  if(myChart) myChart.clear()-->
<!--}-->

<!--onMounted(() => {-->
<!--  fetchLibrary()-->
<!--  window.addEventListener('resize', () => myChart && myChart.resize())-->
<!--})-->
<!--</script>-->

<!--<style scoped>-->
<!--/* CSS 复用之前的，增加进度条样式 */-->
<!--.task-container { height: 100%; display: flex; flex-direction: column; font-family: "KaiTi", serif; }-->
<!--.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #e6dcc8; padding-bottom: 10px; flex-shrink: 0; }-->
<!--.title-box { display: flex; flex-direction: column; }-->
<!--.gufeng-title { margin: 0; color: #5e482d; font-size: 24px; border-left: 4px solid #8e3e3e; padding-left: 15px; letter-spacing: 2px; }-->
<!--.sub-tip { font-size: 12px; color: #909399; margin-left: 20px; margin-top: 5px; display: flex; align-items: center; gap: 5px; }-->
<!--.header-actions { display: flex; align-items: center; gap: 15px; }-->
<!--.current-corpus { font-size: 14px; color: #666; }-->
<!--.highlight { color: #8e3e3e; font-weight: bold; }-->
<!--.gufeng-btn { background-color: #8e3e3e; border-color: #8e3e3e; font-family: "KaiTi"; letter-spacing: 1px; transition: all 0.3s; }-->
<!--.action-btn { background-color: #b8860b; border-color: #b8860b; }-->

<!--/* 进度条 */-->
<!--.progress-bar-box { margin-bottom: 15px; flex-shrink: 0; }-->
<!--.progress-text { text-align: center; font-size: 12px; color: #666; margin-top: 5px; }-->

<!--.workspace-box { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: #fff; border-radius: 4px; border: 1px solid #e6dcc8; padding: 20px; min-height: 0; }-->
<!--.ner-layout { display: flex; height: 100%; gap: 20px; overflow: hidden; }-->

<!--/* 左侧文本区 */-->
<!--.text-section { flex: 2; display: flex; flex-direction: column; border: 1px solid #dcc8a6; border-radius: 4px; background: #fffdf6; overflow: hidden; }-->
<!--.paper-texture { background-image: linear-gradient(90deg, transparent 95%, rgba(220, 200, 166, 0.2) 95%); background-size: 40px 100%; }-->
<!--.section-header { height: 40px; border-bottom: 1px dashed #dcc8a6; display: flex; justify-content: space-between; align-items: center; padding: 0 15px; background: rgba(205, 171, 132, 0.1); flex-shrink: 0; }-->
<!--.legend { font-size: 12px; display: flex; gap: 10px; }-->
<!--.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 3px; }-->
<!--.dot.person { background: #8e3e3e; } .dot.location { background: #2b4b64; } .dot.office { background: #b8860b; }-->

<!--.text-content { flex: 1; padding: 15px; overflow-y: auto; font-size: 18px; line-height: 2; color: #333; }-->
<!--.processing-tip { text-align: center; color: #999; margin-top: 50px; }-->
<!--.sent-row { display: flex; margin-bottom: 12px; line-height: 1.8; font-size: 18px; color: #333; }-->
<!--.sent-idx { width: 30px; font-size: 12px; color: #cdab84; user-select: none; margin-top: 4px; }-->
<!--.sent-body { flex: 1; text-align: justify; }-->

<!--/* 右侧分析区 */-->
<!--.viz-section { flex: 1; display: flex; flex-direction: column; gap: 15px; min-width: 300px; height: 100%; overflow: hidden; }-->
<!--.stats-row { display: flex; gap: 10px; flex-shrink: 0; }-->
<!--.stat-card { flex: 1; background: #fcf9f2; border: 1px solid #e6dcc8; padding: 15px 0; text-align: center; border-radius: 4px; }-->
<!--.stat-val { font-size: 20px; font-weight: bold; color: #8e3e3e; }-->
<!--.stat-label { font-size: 12px; color: #8c8272; }-->

<!--.chart-box { height: 200px; border: 1px solid #e6dcc8; background: #fff; border-radius: 4px; display: flex; flex-direction: column; flex-shrink: 0; }-->
<!--.chart-container { flex: 1; }-->

<!--.entity-list-box { flex: 1; border: 1px solid #e6dcc8; display: flex; flex-direction: column; background: #fff; min-height: 0; }-->
<!--.list-content { flex: 1; overflow-y: auto; padding: 5px; }-->

<!--/* 高亮样式 */-->
<!--:deep(.ner-per) { color: #8e3e3e; border-bottom: 2px solid #8e3e3e; font-weight: bold; padding-bottom: 1px; }-->
<!--:deep(.ner-loc) { color: #2b4b64; border-bottom: 2px solid #2b4b64; font-weight: bold; padding-bottom: 1px; }-->
<!--:deep(.ner-org) { color: #b8860b; border-bottom: 2px solid #b8860b; font-weight: bold; padding-bottom: 1px; }-->
<!--.tag-PER { background-color: #8e3e3e !important; color: #fff !important; }-->
<!--.tag-LOC { background-color: #2b4b64 !important; color: #fff !important; }-->
<!--.tag-ORG { background-color: #b8860b !important; color: #fff !important; }-->

<!--.custom-scrollbar::-webkit-scrollbar { width: 6px; }-->
<!--.custom-scrollbar::-webkit-scrollbar-thumb { background: #dcc8a6; border-radius: 3px; }-->
<!--.fade-in { animation: fadeIn 0.6s ease; }-->
<!--@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }-->
<!--.empty-state { height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #909399; }-->
<!--</style>-->

<template>
  <div class="task-container fade-in">
    <div class="header-row">
      <div class="title-box">
        <h2 class="gufeng-title">古籍命名实体识别</h2>
        <span class="sub-tip" v-if="selectedCorpus">
          <el-icon><CollectionTag /></el-icon> {{ selectedCorpus.category }} · {{ selectedCorpus.sentenceCount }}句
        </span>
      </div>

      <div class="header-actions">
        <div class="current-corpus" v-if="selectedCorpus">
          当前案卷：<span class="highlight">《{{ selectedCorpus.title }}》</span>
        </div>
        <el-button type="primary" class="gufeng-btn" @click="dialogVisible = true">
          <el-icon style="margin-right: 5px"><Document /></el-icon>
          {{ selectedCorpus ? '更换案卷' : '调取案卷' }}
        </el-button>
        <el-button
            v-if="selectedCorpus"
            type="warning"
            class="gufeng-btn action-btn"
            @click="startAnalysis"
            :disabled="isProcessing"
        >
          <el-icon style="margin-right: 5px"><VideoPlay /></el-icon> 逐句识别
        </el-button>
      </div>
    </div>

    <div class="progress-bar-box" v-if="isProcessing || processPercent > 0">
      <el-progress :percentage="processPercent" :stroke-width="15" striped striped-flow status="success" />
      <div class="progress-text">{{ processTip }}</div>
    </div>

    <div class="workspace-box">
      <div v-if="!analysisList.length && !isProcessing" class="empty-state">
        <div class="empty-icon-bg"><el-icon :size="50" color="#dcc8a6"><Search /></el-icon></div>
        <p class="empty-text">请调取案卷并启动分析</p>
      </div>

      <div v-else class="ner-layout">

        <div class="text-section paper-texture">
          <div class="section-header">
            <span class="label">识别结果 (逐句)</span>
            <div class="legend">
              <span class="dot person"></span>人名
              <span class="dot official"></span>官职
              <span class="dot location"></span>地名
              <span class="dot time"></span>时间
            </div>
          </div>

          <div class="text-content custom-scrollbar">
            <div v-if="analysisList.length === 0" class="processing-tip">正在逐句分析中，请稍候...</div>
            <div v-else v-for="(item, index) in analysisList" :key="index" class="sent-row">
              <div class="sent-idx">{{ item.index || index + 1 }}</div>
              <div class="sent-body" v-html="highlightSentence(item.content, item.entities)"></div>
            </div>
          </div>
        </div>

        <div class="viz-section">

          <div class="stats-grid">
            <div class="stat-card total">
              <div class="stat-val">{{ stats.total }}</div>
              <div class="stat-label">实体总数</div>
            </div>

            <div class="stat-card type-card">
              <div class="row">
                <div class="col">
                  <span class="dot person"></span>
                  <span class="lbl">人名 PER</span>
                </div>
                <span class="val">{{ stats.perCount }}</span>
              </div>
              <div class="row">
                <div class="col">
                  <span class="dot official"></span>
                  <span class="lbl">官职 OFI</span>
                </div>
                <span class="val">{{ stats.ofiCount }}</span>
              </div>
            </div>

            <div class="stat-card type-card">
              <div class="row">
                <div class="col">
                  <span class="dot location"></span>
                  <span class="lbl">地名 LOC</span>
                </div>
                <span class="val">{{ stats.locCount }}</span>
              </div>
              <div class="row">
                <div class="col">
                  <span class="dot time"></span>
                  <span class="lbl">时间 TIME</span>
                </div>
                <span class="val">{{ stats.timeCount }}</span>
              </div>
            </div>
          </div>

          <div class="chart-box">
            <div class="section-header"><span class="label">全卷实体分布</span></div>
            <div ref="chartRef" class="chart-container"></div>
          </div>

          <div class="entity-list-box paper-texture">
            <div class="section-header"><span class="label">高频实体榜</span></div>
            <div class="list-content custom-scrollbar">
              <el-table :data="topEntities" style="width: 100%; background: transparent;" :show-header="false" size="small">
                <el-table-column prop="word" label="实体" show-overflow-tooltip />
                <el-table-column prop="type" label="类型" width="80">
                  <template #default="scope">
                    <el-tag :class="'tag-' + (scope.row.type || 'OTHER')" effect="dark" size="small" style="border:none">
                      {{ typeNameMap[scope.row.type] || scope.row.type }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="count" label="频次" width="50" align="right" />
              </el-table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog
        v-model="dialogVisible"
        title="选取古籍语料"
        width="800px"
        class="ancient-dialog"
        align-center
        :before-close="handleDialogClose"
    >
      <template #header="{ close, titleId, titleClass }">
        <div class="my-header">
          <span :id="titleId" :class="titleClass">选取古籍语料</span>
          <el-icon class="close-btn" @click="close"><Close /></el-icon>
        </div>
      </template>

      <div class="dialog-content">
        <div class="table-wrapper">
          <el-table
              :data="libraryList"
              v-loading="tableLoading"
              style="width: 100%"
              height="400px"
              highlight-current-row
              @row-click="onRowClick"
              @row-dblclick="confirmSelect"
              :header-cell-style="{background:'rgba(205,171,132,0.1)', color:'#5e482d', fontWeight:'bold'}"
          >
            <el-table-column prop="title" label="篇名" min-width="200">
              <template #default="scope">
                <span class="book-title">《{{ scope.row.title }}》</span>
              </template>
            </el-table-column>

            <el-table-column prop="category" label="类型" width="100" align="center">
              <template #default="scope">
                <el-tag effect="plain" color="#fdf6ec" style="color: #b8860b; border-color: #e6dcc8">
                  {{ scope.row.category }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="sentenceCount" label="句数" width="100" align="center" />
            <el-table-column prop="createTime" label="入库时间" width="180" align="center">
              <template #default="scope">{{ scope.row.createTime?.substring(0,10) }}</template>
            </el-table-column>

            <el-table-column width="100" align="center" label="操作">
              <template #default="scope">
                <el-button
                    v-if="tempSelectedRow && tempSelectedRow.id === scope.row.id"
                    type="primary"
                    size="small"
                    link
                    class="row-btn-active"
                >
                  已选中
                </el-button>
                <el-button
                    v-else
                    link
                    size="small"
                    class="row-btn"
                >
                  选取
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <div class="selected-tip">
            <span v-if="tempSelectedRow">
              已选择：<span class="highlight">《{{ tempSelectedRow.title }}》</span>
            </span>
            <span v-else class="placeholder">请点击列表选择一份语料</span>
          </div>
          <div class="footer-btns">
            <el-button @click="handleDialogClose">取 消</el-button>
            <el-button type="primary" class="gufeng-btn" @click="confirmSelect" :disabled="!tempSelectedRow">
              确 定 导 入
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, onMounted, nextTick } from 'vue'
import { CollectionTag, Document, VideoPlay, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'

const dialogVisible = ref(false)
const loading = ref(false)
const libraryList = ref([])
const selectedCorpus = ref(null)

// 进度与状态
const isProcessing = ref(false)
const processPercent = ref(0)
const processTip = ref('')
let pollTimer = null

const analysisList = ref([])
// 修改点：stats 对象扩展
const stats = ref({ total: 0, perCount: 0, ofiCount: 0, locCount: 0, timeCount: 0 })
const topEntities = ref([])
const chartRef = ref(null)
let myChart = null

// 修改点：映射表，增加 OFI
const typeNameMap = {
  'PER': '人名',
  'OFI': '官职',
  'LOC': '地名',
  'TIME': '时间'
}

// 颜色映射 (古风色系)
const colorMap = {
  PER: '#8e3e3e', // 朱砂 (红)
  OFI: '#b8860b', // 赭石 (金/褐)
  LOC: '#2b4b64', // 青黛 (蓝)
  TIME: '#4a6b5c', // 松花 (绿)
  OTHER: '#909399'
}

// 1. 高亮逻辑
const highlightSentence = (text, entitiesMap) => {
  if (!text) return ''
  if (!entitiesMap || Object.keys(entitiesMap).length === 0) return text
  let result = text
  const flat = []

  for (const key in entitiesMap) {
    const words = entitiesMap[key]
    if (Array.isArray(words)) words.forEach(w => flat.push({ word: w, type: key }))
  }

  flat.sort((a, b) => b.word.length - a.word.length)
  flat.forEach(({ word, type }) => {
    const safeWord = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const reg = new RegExp(safeWord + '(?![^<]*>)', 'g')
    const cls = `ner-${type.toLowerCase()}`
    const label = typeNameMap[type] || type
    result = result.replace(reg, `<span class="${cls}" data-label="${label}">${word}</span>`)
  })
  return result
}

// 2. 统计逻辑 (核心修改)
const calculateStats = (list) => {
  let total = 0
  let per = 0, ofi = 0, loc = 0, time = 0
  const countMap = {}

  if (!list) return

  list.forEach(item => {
    if (!item.entities) return

    for (const key in item.entities) {
      const words = item.entities[key]
      if (!Array.isArray(words)) continue

      total += words.length
      // 分类统计
      if (key === 'PER') per += words.length
      else if (key === 'OFI' || key === 'ORG') ofi += words.length // 兼容 ORG/OFI
      else if (key === 'LOC') loc += words.length
      else if (key === 'TIME') time += words.length

      words.forEach(w => {
        // 使用 "实体-类型" 作为唯一键
        const uniqueKey = `${w}-${key}`
        if (!countMap[uniqueKey]) countMap[uniqueKey] = { word: w, type: key, count: 0 }
        countMap[uniqueKey].count++
      })
    }
  })

  // 更新响应式数据
  stats.value = {
    total,
    perCount: per,
    ofiCount: ofi,
    locCount: loc,
    timeCount: time
  }

  // 榜单
  topEntities.value = Object.values(countMap)
      .sort((a, b) => b.count - a.count)
      .slice(0, 50)

  // 准备图表数据
  const chartData = []
  // 确保这四类都在图表里，即使是0
  if (per > 0) chartData.push({ name: '人名', value: per, itemStyle: { color: colorMap.PER } })
  if (ofi > 0) chartData.push({ name: '官职', value: ofi, itemStyle: { color: colorMap.OFI } })
  if (loc > 0) chartData.push({ name: '地名', value: loc, itemStyle: { color: colorMap.LOC } })
  if (time > 0) chartData.push({ name: '时间', value: time, itemStyle: { color: colorMap.TIME } })

  nextTick(() => initChart(chartData))
}

const startAnalysis = async () => {
  if (!selectedCorpus.value) return
  isProcessing.value = true
  processPercent.value = 0
  processTip.value = '正在启动 NER 引擎...'
  analysisList.value = []

  try {
    await axios.post('http://localhost:8080/api/analysis/ner/run_async', { id: selectedCorpus.value.id })
    pollTimer = setInterval(checkProgress, 1000)
  } catch (e) {
    isProcessing.value = false
    ElMessage.error('启动失败')
  }
}

const checkProgress = async () => {
  try {
    const res = await axios.get(`http://localhost:8080/api/analysis/ner/progress/${selectedCorpus.value.id}`)
    const p = res.data
    processPercent.value = p
    processTip.value = `正在深度解析... ${p}%`

    if (p >= 100) {
      clearInterval(pollTimer)
      isProcessing.value = false
      processTip.value = '分析完成'
      loadResult()
    }
  } catch (e) {
    clearInterval(pollTimer)
    isProcessing.value = false
  }
}

const loadResult = async () => {
  try {
    const res = await axios.get(`http://localhost:8080/api/analysis/ner/result/${selectedCorpus.value.id}`)
    analysisList.value = res.data
    calculateStats(res.data)
    ElMessage.success(`共识别 ${res.data.length} 句`)
  } catch (e) { ElMessage.error('获取结果失败') }
}

const initChart = (data) => {
  if (!chartRef.value) return
  if (myChart) myChart.dispose()
  myChart = echarts.init(chartRef.value)

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 10 } },
    series: [{
      type: 'pie',
      radius: ['35%', '60%'],
      center: ['50%', '45%'],
      data: data,
      label: { show: true, formatter: '{b}\n{c}', color: '#555' },
      labelLine: { length: 10, length2: 10 }
    }]
  }
  myChart.setOption(option)
}

const fetchLibrary = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8080/api/library/list')
    libraryList.value = res.data
  } catch (e) { ElMessage.error('获取语料库失败') } finally { loading.value = false }
}
const handleSelect = (row) => {
  selectedCorpus.value = row
  dialogVisible.value = false
  analysisList.value = []
  if (myChart) myChart.clear()
}

onMounted(() => {
  fetchLibrary()
  window.addEventListener('resize', () => myChart && myChart.resize())
})

// src/components/RelationAnalysis.vue

// ... 其他变量 ...
const tempSelectedRow = ref(null) // 【新增】临时选中的行

// ...

// 1. 【修改】点击行只是选中，不触发加载
const onRowClick = (row) => {
  tempSelectedRow.value = row
}

// 2. 【新增】点击"确定"按钮，或者双击行时触发
const confirmSelect = () => {
  if (!tempSelectedRow.value) {
    ElMessage.warning('请先选择一份语料')
    return
  }

  // 执行原来的选择逻辑
  handleSelect(tempSelectedRow.value)
}


// 3. 【新增】弹窗关闭时清理状态
const handleDialogClose = () => {
  tempSelectedRow.value = null
  dialogVisible.value = false
}

</script>

<style scoped>
/* 保持原有布局，增加新的统计卡片样式 */
.task-container { height: 100%; display: flex; flex-direction: column; font-family: "KaiTi", serif; }
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #e6dcc8; padding-bottom: 10px; flex-shrink: 0; }
.title-box { display: flex; flex-direction: column; }
.gufeng-title { margin: 0; color: #5e482d; font-size: 24px; border-left: 4px solid #8e3e3e; padding-left: 15px; letter-spacing: 2px; }
.sub-tip { font-size: 12px; color: #909399; margin-left: 20px; margin-top: 5px; display: flex; align-items: center; gap: 5px; }
.header-actions { display: flex; align-items: center; gap: 15px; }
.current-corpus { font-size: 14px; color: #666; }
.highlight { color: #8e3e3e; font-weight: bold; }
.gufeng-btn { background-color: #8e3e3e; border-color: #8e3e3e; font-family: "KaiTi"; letter-spacing: 1px; transition: all 0.3s; }
.action-btn { background-color: #b8860b; border-color: #b8860b; }

.progress-bar-box { margin-bottom: 15px; flex-shrink: 0; }
.progress-text { text-align: center; font-size: 12px; color: #666; margin-top: 5px; }

.workspace-box { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: #fff; border-radius: 4px; border: 1px solid #e6dcc8; padding: 20px; min-height: 0; }
.ner-layout { display: flex; height: 100%; gap: 20px; overflow: hidden; }

/* 左侧 */
.text-section { flex: 2; display: flex; flex-direction: column; border: 1px solid #dcc8a6; border-radius: 4px; background: #fffdf6; overflow: hidden; }
.paper-texture { background-image: linear-gradient(90deg, transparent 95%, rgba(220, 200, 166, 0.2) 95%); background-size: 40px 100%; }
.section-header { height: 40px; border-bottom: 1px dashed #dcc8a6; display: flex; justify-content: space-between; align-items: center; padding: 0 15px; background: rgba(205, 171, 132, 0.1); flex-shrink: 0; }
.legend { font-size: 12px; display: flex; gap: 12px; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 3px; }
.dot.person { background: #8e3e3e; }
.dot.official { background: #b8860b; }
.dot.location { background: #2b4b64; }
.dot.time { background: #4a6b5c; }

.text-content { flex: 1; padding: 15px; overflow-y: auto; font-size: 18px; line-height: 2; color: #333; }
.sent-row { display: flex; margin-bottom: 12px; line-height: 1.8; font-size: 18px; color: #333; }
.sent-idx { width: 30px; font-size: 12px; color: #cdab84; user-select: none; margin-top: 4px; }
.sent-body { flex: 1; text-align: justify; }

/* 右侧 */
.viz-section { flex: 1; display: flex; flex-direction: column; gap: 15px; min-width: 320px; height: 100%; overflow: hidden; }

/* 统计卡片组 */
.stats-grid { display: flex; gap: 10px; flex-shrink: 0; height: 100px; }
.stat-card { flex: 1; background: #fcf9f2; border: 1px solid #e6dcc8; border-radius: 4px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.stat-card.total .stat-val { font-size: 28px; color: #8e3e3e; font-weight: bold; }
.stat-card.total .stat-label { font-size: 12px; color: #909399; margin-top: 5px; }

.type-card { align-items: flex-start; padding: 0 15px; justify-content: space-evenly; }
.type-card .row { display: flex; width: 100%; justify-content: space-between; align-items: center; }
.type-card .col { display: flex; align-items: center; gap: 6px; }
.type-card .lbl { font-size: 13px; color: #555; }
.type-card .val { font-weight: bold; font-size: 15px; color: #333; }

.chart-box { height: 240px; border: 1px solid #e6dcc8; background: #fff; border-radius: 4px; display: flex; flex-direction: column; flex-shrink: 0; }
.chart-container { flex: 1; }

.entity-list-box { flex: 1; border: 1px solid #e6dcc8; display: flex; flex-direction: column; background: #fff; min-height: 0; }
.list-content { flex: 1; overflow-y: auto; padding: 5px; }

/* Highlight styles */
:deep(.ner-per) { color: #8e3e3e; border-bottom: 2px solid #8e3e3e; font-weight: bold; padding-bottom: 1px; position: relative; cursor: pointer; }
:deep(.ner-ofi), :deep(.ner-org) { color: #b8860b; border-bottom: 2px solid #b8860b; font-weight: bold; padding-bottom: 1px; position: relative; cursor: pointer; }
:deep(.ner-loc) { color: #2b4b64; border-bottom: 2px solid #2b4b64; font-weight: bold; padding-bottom: 1px; position: relative; cursor: pointer; }
:deep(.ner-time) { color: #4a6b5c; border-bottom: 2px solid #4a6b5c; font-weight: bold; padding-bottom: 1px; position: relative; cursor: pointer; }

/* Tooltip */
:deep([class^="ner-"]:hover)::after {
  content: attr(data-label);
  position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
  background-color: #2b303b; color: #cdab84; padding: 4px 8px; border-radius: 4px;
  font-size: 12px; font-family: "Microsoft YaHei", sans-serif; white-space: nowrap; z-index: 100;
  margin-bottom: 6px; pointer-events: none;
}
:deep([class^="ner-"]:hover)::before {
  content: ''; position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
  border: 5px solid transparent; border-top-color: #2b303b; margin-bottom: -4px; z-index: 100;
}

.tag-PER { background-color: #8e3e3e !important; color: #fff !important; }
.tag-OFI, .tag-ORG { background-color: #b8860b !important; color: #fff !important; }
.tag-LOC { background-color: #2b4b64 !important; color: #fff !important; }
.tag-TIME { background-color: #4a6b5c !important; color: #fff !important; }
.tag-OTHER { background-color: #909399 !important; color: #fff !important; }

.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #dcc8a6; border-radius: 3px; }
.fade-in { animation: fadeIn 0.6s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.empty-state { height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #909399; }

/* === 古风弹窗深度定制 === */

/* 1. 弹窗主体去白边，加米色背景 */
:deep(.ancient-dialog) {
  background-color: #fcf9f2;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  border: 1px solid #e6dcc8;
  overflow: hidden;
}

/* 2. 标题栏 */
:deep(.el-dialog__header) {
  padding: 0; /* 重置 padding */
  margin: 0;
  border-bottom: 1px solid #e6dcc8;
}

.my-header {
  height: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: #fffdf6;
}

.my-header span {
  font-family: "KaiTi";
  font-size: 20px;
  font-weight: bold;
  color: #5e482d;
  letter-spacing: 2px;
}

.close-btn {
  cursor: pointer;
  font-size: 20px;
  color: #999;
  transition: color 0.3s;
}
.close-btn:hover { color: #8e3e3e; }

/* 3. 内容区域 */
:deep(.el-dialog__body) {
  padding: 20px; /* 给表格留出呼吸感 */
}

.table-wrapper {
  border: 1px solid #dcc8a6; /* 外层加个细框 */
  border-radius: 4px;
  overflow: hidden;
  background: #fff;
}

/* 4. 表格行交互 */
:deep(.el-table__row) {
  cursor: pointer;
  transition: all 0.2s;
}

/* 悬停变色：淡雅的米黄色 */
:deep(.el-table--enable-row-hover .el-table__body tr:hover > td.el-table__cell) {
  background-color: #fdf6ec !important;
}

/* 选中高亮：深一点的米色，左侧加个红条指示 */
:deep(.el-table__body tr.current-row > td.el-table__cell) {
  background-color: #faecd8 !important;
}

/* 5. 细节字体 */
.book-title {
  font-weight: bold;
  color: #8e3e3e; /* 朱砂红标题 */
  font-size: 16px;
}

.count-num {
  font-family: Georgia, serif; /* 数字用衬线体 */
  font-weight: bold;
  color: #2b4b64;
}

.time-text {
  color: #999;
  font-size: 13px;
}
/* === 弹窗底部样式 === */
.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #fcf9f2;
  border-top: 1px solid #e6dcc8;
}

.selected-tip {
  font-size: 14px;
  color: #666;
}
.selected-tip .highlight {
  color: #8e3e3e;
  font-weight: bold;
}
.selected-tip .placeholder {
  color: #999;
  font-style: italic;
}

/* 表格操作按钮 */
.row-btn {
  color: #999;
  font-weight: normal;
}
/* 鼠标悬停整行时，按钮变色 */
.el-table__row:hover .row-btn {
  color: #b8860b;
  font-weight: bold;
}

.row-btn-active {
  color: #8e3e3e !important;
  font-weight: bold;
}

/* 弹窗头部复用之前的 */
.my-header {
  height: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: #fffdf6;
  border-bottom: 1px solid #dcc8a6;
}
.my-header span {
  font-family: "KaiTi";
  font-size: 18px;
  font-weight: bold;
  color: #5e482d;
}
.close-btn { cursor: pointer; }

:deep(.el-dialog__header) { padding: 0; margin: 0; }
:deep(.el-dialog__body) { padding: 0; }
:deep(.el-dialog__footer) { padding: 0; }
</style>