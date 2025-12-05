<template>
  <div class="main-layout">
    <div class="sidebar">
      <div class="logo-area">
        <div class="logo-text">古籍智能</div>
        <div class="logo-sub">处理与分析平台</div>
      </div>
      <ul class="nav-menu">
        <li :class="{ active: activeView === 'process' }" @click="activeView = 'process'">
          <el-icon><EditPen /></el-icon> 文本清洗工作台
        </li>
        <li :class="{ active: activeView === 'library' }" @click="activeView = 'library'">
          <el-icon><Collection /></el-icon> 已处理语料库
        </li>
      </ul>
    </div>

    <div class="content-area">
      <div v-show="activeView === 'process'" class="fade-in">
        <div class="page-header">
          <h2>文本预处理中心</h2>
          <span class="subtitle">上传原始文本 -> 实时清洗预览 -> 保存至语料库</span>
        </div>

        <el-row :gutter="20" style="height: calc(100vh - 100px);">
          <el-col :span="10" class="h-100">
            <el-card class="control-panel h-100" shadow="hover">
              <el-form :model="form" label-position="top">

                <el-form-item label="古籍来源">
                  <el-tabs v-model="inputType" class="custom-tabs">
                    <el-tab-pane label="直接粘贴" name="paste">
                      <el-input
                          v-model="form.content"
                          type="textarea"
                          :rows="8"
                          placeholder="请在此输入或粘贴古籍文本..."
                          resize="none"
                          class="ancient-input"
                      />
                    </el-tab-pane>
                    <el-tab-pane label="文件导入" name="file">
                      <el-upload
                          class="upload-box"
                          drag
                          action="#"
                          :auto-upload="false"
                          :on-change="handleFileChange"
                          :limit="1"
                          :show-file-list="false">
                        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                        <div class="el-upload__text">拖拽 txt 文件至此，自动识别编码</div>
                        <div v-if="fileName" class="file-name-tip">已加载: {{ fileName }}</div>
                      </el-upload>
                    </el-tab-pane>
                  </el-tabs>
                </el-form-item>

                <div class="config-grid">
                  <el-form-item label="文本类型">
                    <el-select v-model="form.textCategory" placeholder="选择类别">
                      <el-option label="史书" value="史书" />
                      <el-option label="志书" value="志书" />
                      <el-option label="笔记" value="笔记" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="智能转换">
                    <el-switch v-model="form.convertToSimplified" active-text="繁转简" />
                  </el-form-item>
                </div>

                <el-divider content-position="left" class="custom-divider">清洗规则 (实时生效)</el-divider>

                <div class="checkbox-group">
                  <el-checkbox v-model="form.splitByPeriod" label="按句号切分" border size="small" />
                  <el-checkbox v-model="form.splitByNewline" label="按换行切分" border size="small" />
                  <el-checkbox v-model="form.removeBrackets" label="去除注释" border size="small" />
                  <el-checkbox v-model="form.standardizeSpaces" label="规范空格" border size="small" />
                </div>

                <div class="footer-actions">
                  <el-button type="primary" color="#626aef" size="large" class="save-btn" @click="saveToLibrary" :disabled="!hasData">
                    <el-icon><FolderAdd /></el-icon> 保存处理结果
                  </el-button>
                  <div class="status-text">
                    <span v-if="previewLoading"><el-icon class="is-loading"><Loading /></el-icon> 正在实时分析...</span>
                    <span v-else-if="hasData">预览已更新 | 共 {{ resultCount }} 句</span>
                    <span v-else>等待输入...</span>
                  </div>
                </div>
              </el-form>
            </el-card>
          </el-col>

          <el-col :span="14" class="h-100">
            <div class="paper-container">
              <div class="paper-header">
                <span>预览视图</span>
                <div class="paper-actions">
                  <el-tag type="info" size="small" effect="plain">{{ form.textCategory || '未分类' }}</el-tag>
                </div>
              </div>
              <div class="paper-content custom-scrollbar" v-loading="previewLoading" element-loading-text="古籍解析中...">
                <div v-if="!hasData" class="empty-paper">
                  <el-icon :size="40" color="#dcdfe6"><Document /></el-icon>
                  <p>左侧输入文本，此处即刻预览</p>
                </div>
                <div v-else>
                  <div v-for="item in previewLines" :key="item.index" class="ancient-line">
                    <span class="line-index">{{ item.index }}</span>
                    <span class="line-text">{{ item.content }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <div v-show="activeView === 'library'" class="fade-in">
        <div class="page-header">
          <h2>已处理语料库管理</h2>
          <span class="subtitle">管理已清洗的文本，并选择用于下游任务（关系抽取/画像生成）</span>
        </div>

        <el-card shadow="never" class="library-card">
          <el-table :data="savedLibrary" style="width: 100%" height="500" stripe>
            <el-table-column prop="title" label="文本摘要/文件名" width="250" />
            <el-table-column prop="category" label="类型" width="100">
              <template #default="scope">
                <el-tag>{{ scope.row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="句数" width="100" />
            <el-table-column prop="time" label="处理时间" width="180" />
            <el-table-column label="操作" align="right">
              <template #default="scope">
                <el-button size="small" type="success" plain @click="useText(scope.row)">
                  选取进行分析
                </el-button>
                <el-button size="small" type="danger" :icon="Delete" circle @click="deleteText(scope.$index)" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { UploadFilled, EditPen, Collection, FolderAdd, Loading, Document, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 状态管理
const activeView = ref('process') // process | library
const inputType = ref('paste')
const fileName = ref('')
const previewLoading = ref(false)
const previewLines = ref([])
const fileBytes = ref(null)

// 模拟的本地语料库（实际开发应从后端 API 获取列表）
const savedLibrary = ref([
  { title: '史记·五帝本纪(示例)', category: '史书', count: 120, time: '2025-11-20 10:00', data: [] }
])

const form = reactive({
  content: '',
  textCategory: '史书',
  convertToSimplified: true,
  splitByPeriod: true,
  splitByNewline: true,
  splitByComma: false,
  removeBrackets: false,
  standardizeSpaces: true,
  customSeparator: ''
})

// 计算属性
const hasData = computed(() => previewLines.value.length > 0)
const resultCount = computed(() => previewLines.value.length)

// 防抖函数：防止打字时频繁请求
let debounceTimer = null
const debouncePreview = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  previewLoading.value = true
  debounceTimer = setTimeout(() => {
    fetchPreview()
  }, 500) // 500ms 无操作后触发
}

// 监听表单所有变化，自动触发预览
watch(form, () => {
  if (form.content || fileBytes.value) {
    debouncePreview()
  }
}, { deep: true })

// 文件处理
const handleFileChange = (file) => {
  fileName.value = file.name
  const reader = new FileReader()
  // 修复点2：移除了参数 e
  reader.onload = () => {
    // 这里不直接赋值给 form.content，避免大文件卡顿
    // 我们用一个标记位或者直接触发 fetch
    fileBytes.value = file.raw
    debouncePreview()
  }
  reader.readAsArrayBuffer(file.raw)
}

// 核心：请求后端预览
const fetchPreview = async () => {
  if (!form.content && !fileBytes.value) {
    previewLoading.value = false
    return
  }

  const formData = new FormData()
  const config = { ...form, isPreview: true } // 仍然叫 isPreview，后端全量返回也没关系，前端展示限制即可

  // 如果是文件模式
  if (inputType.value === 'file' && fileBytes.value) {
    formData.append('file', fileBytes.value)
  }

  const jsonBlob = new Blob([JSON.stringify(config)], { type: 'application/json' })
  formData.append('config', jsonBlob)

  try {
    const res = await axios.post('http://localhost:8080/api/text/process', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    previewLines.value = res.data.lines
  } catch (e) {
    console.error(e)
    ElMessage.error('预览服务连接失败')
  } finally {
    previewLoading.value = false
  }
}

// 保存到语料库
const saveToLibrary = () => {
  if (!hasData.value) return

  // 模拟保存
  const title = inputType.value === 'file' ? fileName.value : (form.content.substring(0, 10) + '...')
  const newRecord = {
    title: title,
    category: form.textCategory,
    count: resultCount.value,
    time: new Date().toLocaleString(),
    data: [...previewLines.value] // 深度复制当前结果
  }

  savedLibrary.value.unshift(newRecord) // 加到最前面
  ElMessage.success('已保存至语料库')
  activeView.value = 'library' // 自动跳到库页面查看
}

// 删除
const deleteText = (index) => {
  savedLibrary.value.splice(index, 1)
  ElMessage.success('已删除')
}

// 选取文本（后续对接其他功能）
const useText = (row) => {
  ElMessageBox.confirm(
      `确认选取 "${row.title}" 进行后续分析吗？`,
      '系统提示',
      { confirmButtonText: '进入关系抽取', cancelButtonText: '取消', type: 'info' }
  ).then(() => {
    ElMessage.success('已加载数据，正在跳转至关系抽取模块...')
    // 这里以后写 router.push('/relation-extraction')
  })
}
</script>

<style scoped>
/* 全局布局变量 */
:root {
  --sidebar-width: 240px;
  --sidebar-bg: #2b303b;
  --accent-color: #cdab84; /* 古籍金 */
  --bg-color: #f7f7f5; /* 宣纸白 */
  --text-main: #2c3e50;
}

.main-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #f7f7f5;
  overflow: hidden;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}

/* 侧边栏样式 */
.sidebar {
  width: 240px;
  background-color: #2b303b;
  color: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 10px rgba(0,0,0,0.1);
}

.logo-area {
  height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #22262e;
  border-bottom: 1px solid #3d4450;
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
  color: #cdab84; /* 古意金色 */
  font-family: "KaiTi", serif;
}
.logo-sub {
  font-size: 12px;
  color: #8996a5;
  margin-top: 4px;
}

.nav-menu {
  list-style: none;
  padding: 0;
  margin: 20px 0;
}

.nav-menu li {
  padding: 15px 25px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  color: #a0aab6;
}

.nav-menu li:hover {
  background-color: #353b48;
  color: #fff;
}

.nav-menu li.active {
  background-color: #353b48;
  color: #cdab84;
  border-right: 3px solid #cdab84;
}

/* 内容区通用 */
.content-area {
  flex: 1;
  padding: 20px 30px;
  overflow: hidden;
}

.page-header {
  margin-bottom: 20px;
}
.page-header h2 { margin: 0 0 5px 0; color: #2c3e50; }
.subtitle { color: #909399; font-size: 13px; }

.h-100 { height: 100%; }
.control-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  border: none;
}

.ancient-input :deep(.el-textarea__inner) {
  background-color: #fafafa;
  border-color: #e4e7ed;
  font-size: 14px;
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 10px;
}

.custom-divider { margin: 20px 0; }

.checkbox-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 20px;
}

.footer-actions {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.save-btn { width: 100%; font-weight: bold; letter-spacing: 1px; }
.status-text {
  text-align: center;
  font-size: 12px;
  color: #909399;
}

/* 纸张预览效果 */
.paper-container {
  background: #fffdf6; /* 仿纸张背景 */
  height: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  border: 1px solid #eaddc5;
}

.paper-header {
  height: 50px;
  padding: 0 20px;
  border-bottom: 1px solid #eaddc5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #5e482d;
  background: rgba(205, 171, 132, 0.1);
}

.paper-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  font-family: "KaiTi", "STKaiti", "BiauKai", serif; /* 楷体核心 */
}

.ancient-line {
  display: flex;
  margin-bottom: 12px;
  line-height: 1.8;
  font-size: 16px;
  color: #2b2b2b;
}

.line-index {
  color: #cdab84;
  width: 35px;
  font-size: 12px;
  user-select: none;
  padding-top: 4px;
}

.line-text {
  border-bottom: 1px dashed rgba(0,0,0,0.05);
  width: 100%;
}

.empty-paper {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #c0c4cc;
}

.fade-in {
  animation: fadeIn 0.5s ease-in-out;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #eaddc5; border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }

.file-name-tip { font-size: 12px; color: #67c23a; margin-top: 5px; }

/* --- 新增/修改的样式 --- */

/* 1. 强制 Tabs 占满容器宽度 */
.custom-tabs {
  width: 100%;
}

/* 2. 强制上传组件占满宽度 (核心修改) */
.upload-box {
  width: 100%;
}

/* 使用 :deep 穿透 Element Plus 内部样式，强制拖拽框 100% 宽 */
.upload-box :deep(.el-upload) {
  width: 100%;
}
.upload-box :deep(.el-upload-dragger) {
  width: 100% !important; /* 强制覆盖默认宽度 */
  background-color: #fafafa; /* 与文本输入框背景一致 */
}

/* 3. 确保文本域也是 100% */
.ancient-input {
  width: 100%;
}

/* 4. 如果需要，微调一下 Tab 的内容区边距 */
:deep(.el-tabs__content) {
  padding: 10px 0; /* 上下给点间距 */
}
</style>