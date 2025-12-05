<template>
  <div class="analysis-container fade-in">
    <h2 class="gufeng-title">古籍人物关系识别</h2>

    <div class="tab-wrapper">
      <el-tabs v-model="activeTab" type="border-card" class="custom-tabs" @tab-change="handleTabChange">

        <el-tab-pane label="单句精研" name="single">
          <div class="single-layout">
            <div class="input-col">
              <el-card shadow="never" class="form-card">
                <template #header>
                  <div class="card-header">
                    <div class="header-left">
                      <span>文本录入</span>
                      <el-button type="primary" link @click="fillExample" style="margin-left: 10px;">(填入示例)</el-button>
                    </div>
                    <el-radio-group v-model="singleMode" size="small" fill="#8e3e3e">
                      <el-radio-button label="auto">全自动</el-radio-button>
                      <el-radio-button label="manual">手动</el-radio-button>
                    </el-radio-group>
                  </div>
                </template>
                <el-form :model="singleForm" label-position="top">
                  <el-form-item label="原句">
                    <el-input v-model="singleForm.text" type="textarea" :rows="4" class="ancient-input" placeholder="请输入古籍原句..." />
                  </el-form-item>

                  <div v-if="singleMode === 'manual'" class="manual-box fade-in">
                    <div class="entity-row">
                      <el-form-item label="主体" style="flex:1"><el-input v-model="singleForm.subject_word" placeholder="如：项羽"/></el-form-item>
                      <el-form-item label="词性" style="width:100px">
                        <el-select v-model="singleForm.subject_type"><el-option label="nh" value="nh"/><el-option label="n" value="n"/></el-select>
                      </el-form-item>
                    </div>
                    <div class="entity-row">
                      <el-form-item label="客体" style="flex:1"><el-input v-model="singleForm.object_word" placeholder="如：刘邦"/></el-form-item>
                      <el-form-item label="词性" style="width:100px">
                        <el-select v-model="singleForm.object_type"><el-option label="nh" value="nh"/><el-option label="n" value="n"/></el-select>
                      </el-form-item>
                    </div>
                  </div>
                  <div v-else class="auto-tip"><el-alert title="系统将自动识别实体并推断关系" type="info" :closable="false" show-icon /></div>

                  <el-button type="primary" class="gufeng-btn run-btn" @click="runSingleAnalysis" :loading="singleLoading">
                    <el-icon style="margin-right:5px"><Connection /></el-icon> 立即识别
                  </el-button>
                </el-form>
              </el-card>

              <div class="result-list-box custom-scrollbar" v-if="singleResults.length > 0">
                <div v-for="(res, idx) in singleResults" :key="idx" class="mini-res-item">
                  <div class="entity-wrapper sub-wrapper">
                    <div class="role-badge">主</div><div class="entity-info"><span class="word">{{ res.subjectWord }}</span></div>
                  </div>
                  <div class="relation-middle"><span class="rel-name">{{ res.predicate }}</span><div class="rel-line"><el-icon><Right /></el-icon></div></div>
                  <div class="entity-wrapper obj-wrapper">
                    <div class="role-badge">客</div><div class="entity-info"><span class="word">{{ res.objectWord }}</span></div>
                  </div>
                </div>
              </div>
              <div class="result-box" v-else-if="singleMode === 'manual' && singleResultStr">
                <div class="res-title">识别结果</div><div class="res-val">{{ singleResultStr }}</div>
              </div>
            </div>
            <div class="graph-col paper-texture">
              <div ref="singleGraphRef" class="full-chart"></div>
              <div v-if="!singleResultStr && singleResults.length===0" class="empty-tip">等待分析...</div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="全卷通览" name="batch">
          <div class="batch-layout">
            <div class="batch-header-fixed">
              <div class="left-info">
                <el-tag v-if="selectedCorpusTitle" effect="dark" color="#8e3e3e" style="border:none; font-size: 14px; padding: 15px;">
                  当前案卷：《{{ selectedCorpusTitle }}》
                </el-tag>
                <span v-else class="placeholder">请先选择语料库以进行分析</span>
              </div>
              <div class="right-tools">
                <el-button @click="dialogVisible=true" type="primary" plain size="small">
                  <el-icon style="margin-right:5px"><Collection /></el-icon> 选取语料
                </el-button>
                <el-button @click="startBatchTask" type="warning" plain size="small" :disabled="!currentCorpusId || isProcessing">
                  <el-icon style="margin-right:5px"><VideoPlay /></el-icon> 启动分析引擎
                </el-button>
              </div>
            </div>

            <div class="progress-fixed" v-if="isProcessing || processPercent > 0">
              <div class="progress-info">
                <span class="progress-label">AI 分析进度：</span>
                <el-progress :percentage="processPercent" :stroke-width="12" :striped="isProcessing" :striped-flow="isProcessing" :status="processPercent === 100 ? 'success' : ''" style="width: 300px" />
                <span class="progress-tip">{{ processTip }}</span>
              </div>
            </div>

            <div class="batch-content-fixed">
              <div class="list-wrapper">
                <div class="list-header">
                  <span>关系清单</span>
                  <span v-if="total > 0" class="count">本页 {{ batchRelations.length }} / 共 {{ total }}</span>
                </div>

                <div class="list-scroll custom-scrollbar">
                  <div v-if="batchRelations.length === 0" class="empty-list-guide">
                    <p v-if="!currentCorpusId">请先选取语料</p>
                    <p v-else-if="isProcessing">正在智能筛选有效关系...</p>
                    <p v-else>本页暂无数据 (无关系句已自动过滤)</p>
                  </div>

                  <div
                      v-else
                      v-for="(item, index) in batchRelations"
                      :key="index"
                      class="relation-item"
                      @mouseenter="highlightBatchLink(item)"
                      @mouseleave="resetBatchHighlight"
                  >
                    <div class="mini-res-item no-border">
                      <div class="entity-wrapper sub-wrapper small">
                        <div class="role-badge">主</div>
                        <div class="entity-info"><span class="word" :title="item.subjectWord">{{ item.subjectWord }}</span></div>
                      </div>

                      <div class="relation-middle">
                        <span class="rel-name">{{ item.predicate }}</span>
                        <div class="rel-line"><el-icon><Right /></el-icon></div>
                      </div>

                      <div class="entity-wrapper obj-wrapper small">
                        <div class="role-badge">客</div>
                        <div class="entity-info"><span class="word" :title="item.objectWord">{{ item.objectWord }}</span></div>
                      </div>
                    </div>

                    <div class="rel-text" :title="item.text">{{ item.text }}</div>
                  </div>
                </div>

                <div class="pagination-footer">
                  <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="total" layout="prev, pager, next" small background :disabled="isProcessing" @current-change="handlePageChange" />
                </div>
              </div>

              <div class="graph-wrapper paper-texture">
                <div ref="batchGraphRef" class="full-chart"></div>
                <div v-if="batchRelations.length === 0" class="empty-tip">
                  <el-icon :size="40"><Connection /></el-icon>
                  <p>图谱展示区</p>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
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
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Connection, Collection, VideoPlay, Right } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'

const activeTab = ref('single')
const singleMode = ref('auto')

// 变量
const singleLoading = ref(false)
const singleResultStr = ref('')
const singleResults = ref([])
const singleGraphRef = ref(null)
const singleForm = reactive({ text: '', subject_word: '', subject_type: 'nh', object_word: '', object_type: 'nh' })
let singleChart = null

const dialogVisible = ref(false)
const libraryList = ref([])
const currentCorpusId = ref(null)
const selectedCorpusTitle = ref('')
const batchRelations = ref([])
const hasBatchData = ref(false)
const batchGraphRef = ref(null)
let batchChart = null

const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)
const isProcessing = ref(false)
const processPercent = ref(0)
const processTip = ref('')
let pollTimer = null

const handleTabChange = (tab) => {
  nextTick(() => {
    if (tab === 'single' && singleChart) singleChart.resize()
    if (tab === 'batch' && batchChart) batchChart.resize()
  })
}
const isValidRelation = (pred) => pred && pred !== '无关系' && pred !== '未知' && pred !== 'unknown' && pred !== '无有效关系'

// src/components/RelationAnalysis.vue
const drawEcharts = (domRef, dataList) => {
  if (!domRef) return

  const existingChart = echarts.getInstanceByDom(domRef)
  if (existingChart) existingChart.dispose()

  const myChart = echarts.init(domRef)

  const nodesMap = new Map()
  const linksMap = new Map()

  dataList.forEach(item => {
    const sub = item.subjectWord || '?'
    const obj = item.objectWord || '?'
    const pred = item.predicate || ''

    // 1. 过滤无效关系
    if (!isValidRelation(pred)) return

    // 2. 【核心】去掉自环 (自己指向自己)
    if (sub === obj) return

    // 3. 节点处理 (0:主体-红, 1:客体-蓝)
    if(!nodesMap.has(sub)) nodesMap.set(sub, {name:sub, category:0, value:1, symbolSize:40, draggable:true})
    else nodesMap.get(sub).value++

    if(!nodesMap.has(obj)) nodesMap.set(obj, {name:obj, category:1, value:1, symbolSize:40, draggable:true})
    else nodesMap.get(obj).value++

    // 4. 连线样式逻辑
    const isPersonSubject = item.subjectPos === 'nh' || item.subjectPos === 0
    const isPersonObject  = item.objectPos === 'nh' || item.objectPos === 0

    // 生成唯一Key (排序去重，保证 A->B 和 B->A 是同一条线)
    const linkKey = [sub, obj].sort().join('-') + '-' + pred;
    if (linksMap.has(linkKey)) return;

    let currentSymbol = ['none', 'arrow'] // 默认：单向箭头 (人->物)
    let currentCurveness = 0.2            // 默认：曲线

    if (isPersonSubject && isPersonObject) {
      // 【人 vs 人】:
      // 1. 直线 (0 曲率)
      // 2. 双向箭头 ['arrow', 'arrow'] (两头都有)
      currentSymbol = ['arrow', 'arrow']
      currentCurveness = 0
    } else {
      // 【人 vs 物/地】:
      // 1. 曲线
      // 2. 单向箭头 ['none', 'arrow']
      currentSymbol = ['none', 'arrow']
      currentCurveness = 0.2
    }

    const linkObj = {
      source: sub,
      target: obj,
      label: {
        show: true,
        formatter: pred,
        fontSize: 12,
        color: '#b8860b', // 金色文字
        fontFamily: 'KaiTi',
        backgroundColor: '#fffdf6', // 遮挡线条背景
        padding: [2, 4],
        borderRadius: 2
      },
      lineStyle: {
        curveness: currentCurveness,
        color: '#b8860b', // 古铜色线条
        width: 1.5,
        opacity: 0.8
      },
      edgeSymbol: currentSymbol,
      edgeSymbolSize: [8, 10] // [起始箭头大小, 结束箭头大小]
    };

    linksMap.set(linkKey, linkObj);
  })

  const nodes = Array.from(nodesMap.values()).map(n => {
    n.symbolSize = Math.min(40 + n.value * 3, 80)
    return n
  })

  const option = {
    title: { text: '关系图谱', left: 'center', top: 10, textStyle: { fontFamily: 'KaiTi' } },
    tooltip: { trigger: 'item' },
    color: ['#8e3e3e', '#2b4b64'],
    categories: [{ name: '主体' }, { name: '客体' }],
    legend: { bottom: 10 },
    series: [{
      type: 'graph',
      layout: 'force',
      data: nodes,
      links: Array.from(linksMap.values()),
      categories: [{ name: '主体' }, { name: '客体' }],
      roam: true,
      draggable: true,
      label: { show: true, position: 'right', fontWeight: 'bold', color: '#333' },
      force: {
        repulsion: 2000,
        edgeLength: [150, 300],
        friction: 0.6
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 3, color: '#8e3e3e', opacity: 1 }
      }
    }]
  }

  myChart.setOption(option)

  // 拖拽固定逻辑
  myChart.on('mouseup', function (params) {
    if (params.dataType === 'node') {
      const opt = myChart.getOption();
      opt.series[0].data[params.dataIndex].fixed = true;
      opt.series[0].data[params.dataIndex].x = params.event.target.x;
      opt.series[0].data[params.dataIndex].y = params.event.target.y;
      myChart.setOption(opt);
    }
  });

  return myChart
}
// --- 单句逻辑 ---
const fillExample = () => { singleForm.text = "项羽大怒，欲击刘邦。" }
const runSingleAnalysis = () => { singleMode.value === 'auto' ? predictAuto() : predictManual() }

const predictAuto = async () => {
  if(!singleForm.text) return ElMessage.warning('请输入文本')
  singleLoading.value = true; singleResults.value = []; singleResultStr.value = ''
  try {
    const res = await axios.post('http://localhost:8080/api/analysis/relation/auto_predict', { text: singleForm.text })
    singleResults.value = res.data
    if(res.data.length>0) {
      singleChart = drawEcharts(singleGraphRef.value, res.data) // 使用通用绘图
      ElMessage.success(`识别出 ${res.data.length} 条关系`)
    }
    else { ElMessage.info('未识别出有效关系'); if(singleChart) singleChart.clear() }
  } catch(e) { ElMessage.error('分析失败') } finally { singleLoading.value = false }
}

const predictManual = async () => {
  if(!singleForm.text || !singleForm.subject_word || !singleForm.object_word) return ElMessage.warning('请填写完整')
  singleLoading.value = true; singleResults.value = []
  try {
    const payload = { text: singleForm.text, subject_word: singleForm.subject_word, object_word: singleForm.object_word, subject_pos: singleForm.subject_type, object_pos: singleForm.object_type }
    const res = await axios.post('http://localhost:8080/api/analysis/relation/predict', payload)
    if(res.data.status === 'success') {
      const data = res.data.data
      singleResultStr.value = data.predicted_relation
      // 构造列表调用绘图
      const mockList = [{ subjectWord: data.subject, objectWord: data.object, predicate: data.predicted_relation }]
      singleChart = drawEcharts(singleGraphRef.value, mockList)
    }
  } catch(e) { ElMessage.error('分析失败') } finally { singleLoading.value = false }
}

// --- 批量逻辑 ---
const fetchLibrary = async () => {
  try {
    const res = await axios.get('http://localhost:8080/api/library/list')
    libraryList.value = res.data
  } catch (e) { ElMessage.error('获取语料库失败') }
}
const handleSelect = (row) => { currentCorpusId.value = row.id; selectedCorpusTitle.value = row.title; dialogVisible.value = false; currentPage.value = 1; loadBatchResult() }
const handlePageChange = (page) => { currentPage.value = page; loadBatchResult() }

const startBatchTask = async () => {
  if (!currentCorpusId.value) return
  isProcessing.value = true; processPercent.value = 0; processTip.value = '正在启动...'
  try {
    await axios.post('http://localhost:8080/api/analysis/relation/run_async', { id: currentCorpusId.value })
    if(pollTimer) clearInterval(pollTimer)
    pollTimer = setInterval(checkProgress, 1000)
  } catch(e) { isProcessing.value = false; ElMessage.error('启动失败') }
}
const checkProgress = async () => {
  try {
    const res = await axios.get(`http://localhost:8080/api/analysis/relation/progress/${currentCorpusId.value}`)
    processPercent.value = res.data; processTip.value = `正在分析... ${res.data}%`
    if (res.data >= 100) { clearInterval(pollTimer); isProcessing.value = false; processTip.value = '分析完成'; currentPage.value = 1; loadBatchResult() }
  } catch(e) { clearInterval(pollTimer); isProcessing.value = false }
}
const loadBatchResult = async () => {
  if (!currentCorpusId.value) return
  try {
    const res = await axios.get(`http://localhost:8080/api/analysis/relation/result/${currentCorpusId.value}`, { params: { page: currentPage.value, size: pageSize.value } })
    batchRelations.value = res.data.records; total.value = res.data.total
    const validData = batchRelations.value.filter(i => isValidRelation(i.predicate))
    if (validData.length > 0) {
      hasBatchData.value = true
      batchChart = drawEcharts(batchGraphRef.value, validData) // 使用通用绘图
    } else { hasBatchData.value = false; if(batchChart) batchChart.clear() }
  } catch (e) { ElMessage.error('数据加载失败') }
}
const highlightBatchLink = (item) => { if(batchChart) batchChart.dispatchAction({ type: 'highlight', name: item.subjectWord }) }
const resetBatchHighlight = () => { if(batchChart) batchChart.dispatchAction({ type: 'downplay' }) }


onMounted(() => {
  fetchLibrary()
  window.addEventListener('resize', () => { singleChart?.resize(); batchChart?.resize() })
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
/* CSS 样式完全复用之前的版本，确保布局固定 */
/* 为了节省篇幅，请务必保留之前提供的完整 CSS，特别是 .batch-layout 和 .list-wrapper 的样式 */
.analysis-container { height: 100%; display: flex; flex-direction: column; font-family: "KaiTi", serif; overflow: hidden; }
.gufeng-title { color: #5e482d; margin: 0 0 10px 0; border-left: 4px solid #8e3e3e; padding-left: 10px; flex-shrink: 0; }
.tab-wrapper { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.custom-tabs { height: 100%; display: flex; flex-direction: column; border: none; box-shadow: none; }
:deep(.el-tabs__content) { flex: 1; padding: 0; background: #fcf9f2; overflow: hidden; display: flex; flex-direction: column; }
:deep(.el-tabs__header) { margin: 0; background: #fff; border-bottom: 1px solid #dcc8a6; flex-shrink: 0; }
:deep(.el-tab-pane) { height: 100%; }

.single-layout { display: flex; height: 100%; padding: 20px; gap: 20px; box-sizing: border-box; }
.input-col { width: 450px; display: flex; flex-direction: column; gap: 20px; box-sizing: border-box; }
.form-card { border: 1px solid #e6dcc8; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; color: #5e482d; }
.header-left { display: flex; align-items: center; }
.result-box { flex: 1; border: 1px solid #e6dcc8; background: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; box-sizing: border-box; box-shadow: 0 2px 8px rgba(0,0,0,0.02); border-radius: 4px; position: relative; }
.result-box::before { content: ''; position: absolute; top: 10px; left: 10px; right: 10px; bottom: 10px; border: 1px dashed #e6dcc8; pointer-events: none; border-radius: 2px; }
.res-title { color: #999; margin-bottom: 15px; font-size: 14px; letter-spacing: 2px; }
.res-val { font-size: 36px; color: #b8860b; font-weight: bold; text-shadow: 0 2px 4px rgba(184, 134, 11, 0.1); }
.graph-col { flex: 1; border: 1px solid #dcc8a6; background: #fffdf6; position: relative; border-radius: 4px; box-sizing: border-box; height: 100%; box-shadow: inset 0 0 20px rgba(220, 200, 166, 0.3); }
.full-chart { width: 100%; height: 100%; }
.result-list-box { flex: 1; border: 1px solid #e6dcc8; background: #fff; padding: 10px; overflow-y: auto; border-radius: 4px; display: flex; flex-direction: column; gap: 8px; }
.mini-res-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border: 1px solid #eee; border-radius: 4px; background-color: #fcfcfc; transition: all 0.2s; }
.mini-res-item.no-border { border: none; padding: 0; background: transparent; }
.mini-res-item:hover { border-color: #dcc8a6; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.entity-wrapper { display: flex; align-items: center; gap: 8px; width: 35%; }
.entity-wrapper.small { gap: 4px; }
.role-badge { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #fff; flex-shrink: 0; font-family: "KaiTi"; }
.entity-info { display: flex; flex-direction: column; overflow: hidden; }
.entity-info .word { font-weight: bold; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.entity-info .pos-tag { font-size: 10px; color: #999; background: #f0f0f0; padding: 0 4px; border-radius: 2px; width: fit-content; margin-top: 2px; }
.sub-wrapper .role-badge { background-color: #8e3e3e; } .sub-wrapper .word { color: #8e3e3e; }
.obj-wrapper { flex-direction: row-reverse; text-align: right; } .obj-wrapper .entity-info { align-items: flex-end; }
.obj-wrapper .role-badge { background-color: #2b4b64; } .obj-wrapper .word { color: #2b4b64; }
.relation-middle { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #b8860b; }
.rel-name { font-size: 12px; font-weight: bold; margin-bottom: -2px; }
.rel-line { font-size: 14px; opacity: 0.6; }
.batch-layout { display: flex; flex-direction: column; height: 100%; padding: 15px; box-sizing: border-box; overflow: hidden; }
.batch-header-fixed { height: 50px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #dcc8a6; flex-shrink: 0; }
.placeholder { color: #999; font-size: 14px; }
.progress-fixed { margin-top: 10px; flex-shrink: 0; display: flex; justify-content: center; }
.progress-info { display: flex; align-items: center; gap: 10px; }
.progress-label { font-size: 12px; color: #666; }
.progress-tip { font-size: 12px; color: #8e3e3e; margin-left: 10px; }
.batch-content-fixed { flex: 1; display: flex; gap: 15px; margin-top: 15px; min-height: 0; overflow: hidden; }
.list-wrapper { width: 480px; display: flex; flex-direction: column; border: 1px solid #dcc8a6; background: #fff; border-radius: 4px; flex-shrink: 0; height: 100%; box-sizing: border-box; }
.list-header { height: 40px; background: rgba(205,171,132,0.1); border-bottom: 1px dashed #dcc8a6; display: flex; justify-content: space-between; align-items: center; padding: 0 15px; font-weight: bold; color: #5e482d; flex-shrink: 0; }
.list-scroll { flex: 1; overflow-y: auto; padding: 10px; }
.pagination-footer { height: 45px; border-top: 1px solid #eee; display: flex; align-items: center; justify-content: center; background: #f9f9f9; flex-shrink: 0; }
.relation-item { padding: 12px; border-bottom: 1px solid #eee; cursor: pointer; transition: all 0.2s; }
.relation-item:hover { background: #fdf6ec; transform: translateX(2px); }
.rel-text-only { font-size: 13px; color: #666; line-height: 1.6; }
.status-tag { background: #f0f0f0; color: #999; font-size: 10px; padding: 2px 5px; border-radius: 2px; margin-left: 5px; }
.empty-list-guide { height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #999; text-align: center; }
.graph-wrapper { flex: 1; border: 1px solid #dcc8a6; background: #fffdf6; position: relative; border-radius: 4px; height: 100%; box-sizing: border-box; }
.paper-texture { background-image: linear-gradient(90deg, transparent 95%, rgba(220, 200, 166, 0.2) 95%); background-size: 40px 100%; }
.empty-tip { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #ccc; text-align: center; }
.ancient-input :deep(.el-textarea__inner) { font-family: "KaiTi"; font-size: 16px; background: #fafafa; }
.form-card { border: 1px solid #e6dcc8; }
.entity-row { display: flex; gap: 8px; margin-bottom: 0; }
.run-btn { width: 100%; margin-top: 10px; background: #8e3e3e; border-color: #8e3e3e; font-size: 16px; letter-spacing: 2px; }
.gufeng-btn { font-family: "KaiTi"; }
.manual-box { animation: fadeIn 0.5s; }
.auto-tip { margin-bottom: 20px; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #dcc8a6; border-radius: 3px; }
.fade-in { animation: fadeIn 0.6s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.upload-inline { display: inline-block; }
.rel-text { font-size: 12px; color: #999; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 5px; border-top: 1px dashed #eee; padding-top: 5px;}
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