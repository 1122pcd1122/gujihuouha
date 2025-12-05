<template>
  <div class="process-container fade-in">
    <div class="header-box">
      <h2 class="gufeng-title">文本清洗工作台</h2>
      <div class="action-bar">
        <span class="status-tip" v-if="previewLoading">正在研墨分析...</span>
        <span class="status-tip" v-else>已生成 {{ resultCount }} 句</span>

        <el-button
            class="gufeng-btn-plain"
            @click="clearWorkspace"
            :disabled="!hasData"
        >
          <el-icon style="margin-right:5px"><Delete /></el-icon> 清空台面
        </el-button>

        <el-button type="primary" class="gufeng-btn" @click="openSaveDialog" :disabled="!hasData">
          <el-icon style="margin-right:5px"><FolderAdd /></el-icon> 保存
        </el-button>
      </div>
    </div>

    <el-row :gutter="24" class="workspace">
      <el-col :span="9" class="h-100">
        <div class="panel-box input-panel">
          <el-form :model="form" label-position="top">
            <div class="tabs-header">
              <span :class="{active: inputType==='paste'}" @click="inputType='paste'">手录</span>
              <span class="divider">|</span>
              <span :class="{active: inputType==='file'}" @click="inputType='file'">传书</span>
            </div>
            <div class="input-area">
              <el-input v-if="inputType==='paste'" v-model="form.content" type="textarea" :rows="10" class="gufeng-input" resize="none" placeholder="请在此誊写或粘贴古籍内容..." />
              <el-upload v-else class="upload-box" drag action="#" :auto-upload="false" :on-change="handleFileChange" :limit="1" :show-file-list="false">
                <div class="upload-inner">
                  <el-icon class="upload-icon"><UploadFilled /></el-icon>
                  <div class="upload-text">拖拽 .txt 文件至此</div>
                  <div class="file-name" v-if="fileName">{{ fileName }}</div>
                </div>
              </el-upload>
            </div>
            <div class="settings-area">
              <div class="setting-title"><span>规制设定</span></div>

              <div class="control-row">
                <el-tooltip content="不同体裁会影响后端模型的预训练权重选择" placement="top" :show-after="500">
                  <span class="label help-cursor">体裁：</span>
                </el-tooltip>
                <el-radio-group v-model="form.textCategory" size="small">
                  <el-radio-button label="史书" />
                  <el-radio-button label="志书" />
                  <el-radio-button label="笔记" />
                </el-radio-group>
              </div>

              <div class="control-row">
                <el-tooltip content="推荐开启。将古籍繁体统一转为简体，可大幅提升下游AI模型的实体识别准确率" placement="top">
                  <span class="label help-cursor">预处理：</span>
                </el-tooltip>
                <el-switch v-model="form.convertToSimplified" active-text="化繁为简" />
              </div>

              <div class="control-row">
                <el-tooltip content="决定了文本如何被切分成短句，直接影响分析粒度" placement="top">
                  <span class="label help-cursor">句读：</span>
                </el-tooltip>

                <div class="checkbox-wrap">
                  <el-tooltip content="在切分前，自动移除文中所有的空格、制表符，保持文本紧凑" placement="top">
                    <el-checkbox v-model="form.standardizeSpaces" label="去空清洗" />
                  </el-tooltip>

                  <el-tooltip content="按句号（。）进行切分，适用于大多数标准标点的古籍" placement="top">
                    <el-checkbox v-model="form.splitByPeriod" label="句号切分" />
                  </el-tooltip>

                  <el-tooltip content="保留原文的换行符结构，适用于诗词或已排版好的文本" placement="top">
                    <el-checkbox v-model="form.splitByNewline" label="换行切分" />
                  </el-tooltip>

                  <el-tooltip content="按逗号（，）切分，粒度极细。注意：可能导致句子语义破碎，请按需使用" placement="top">
                    <el-checkbox v-model="form.splitByComma" label="逗号切分" />
                  </el-tooltip>
                </div>
              </div>
            </div>
              <div class="manual-trigger-box">
                <el-button
                    type="primary"
                    class="start-btn"
                    :loading="previewLoading"
                    @click="fetchPreview"
                    :disabled="(!form.content && !fileBytes)"
                >
                  <el-icon class="icon-spin" v-if="previewLoading"><Loading /></el-icon>
                  <el-icon v-else><MagicStick /></el-icon>
                  <span style="margin-left: 6px">立即清洗</span>
                </el-button>
              </div>
          </el-form>
        </div>

      </el-col>
      <el-col :span="15" class="h-100">
        <div class="panel-box paper-panel" v-loading="previewLoading" element-loading-text="墨迹未干...">
          <div class="paper-bg">

            <div v-if="hasData" class="paper-toolbar">
              <span class="edit-tip"><el-icon><Edit /></el-icon> 提示：点击文字可直接修订</span>
            </div>

            <div v-if="!hasData" class="empty-state">
              <div class="circle-bg">书</div>
              <p>待输入文稿</p>
            </div>

            <div v-else class="text-scroll custom-scrollbar">
              <transition-group name="list">
                <div v-for="(item, index) in previewLines" :key="item.index" class="text-line group-item">
                  <span class="index-seal">{{ index + 1 }}</span>

                  <el-input
                      v-model="item.content"
                      type="textarea"
                      autosize
                      class="editable-input"
                      resize="none"
                      placeholder="（此处为空）"
                      :ref="(el) => setInputRef(el, index)"
                      @keydown.backspace="handleBackspace($event, index)"
                  />

                  <div class="line-actions">
                    <el-icon class="delete-icon" @click="removeLine(index)" title="剔除此行"><Close /></el-icon>
                  </div>
                </div>
              </transition-group>
            </div>

          </div>
        </div>
      </el-col>
    </el-row>

    <el-dialog
        v-model="saveDialogVisible"
        title="文稿入库"
        width="400px"
        class="ancient-dialog"
        align-center
    >
      <div style="padding: 10px">
        <el-form :model="saveForm">
          <el-form-item label="文稿题名">
            <el-input v-model="saveForm.title" placeholder="请输入自定义标题（如：史记·高祖本纪）" />
          </el-form-item>
          <el-form-item label="入库备注">
            <div class="save-tip">
              系统将自动生成：<br/>
              1. {{ saveForm.title }}_{{ timeStr }}.txt (原始文稿)<br/>
              2. {{ saveForm.title }}_{{ timeStr }}.json (结构化数据)
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="saveDialogVisible = false">取 消</el-button>
          <el-button type="primary" class="gufeng-btn" @click="confirmSave" :loading="saving">
            确 认 保 存
          </el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, reactive, watch, computed, nextTick } from 'vue'
import { UploadFilled, FolderAdd, Edit, Close, Delete, MagicStick } from '@element-plus/icons-vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import axios from 'axios'

const emit = defineEmits(['save-record'])

// ... 原有变量 ...
const inputType = ref('paste')
const fileName = ref('')
const fileBytes = ref(null)
const previewLines = ref([])
const previewLoading = ref(false)

const form = reactive({
  content: '',
  textCategory: '史书',
  convertToSimplified: true,
  splitByPeriod: true,
  splitByNewline: true,
  splitByComma: false,
  standardizeSpaces: true
})

// 新增变量
const saveDialogVisible = ref(false)
const saving = ref(false)
const saveForm = reactive({ title: '' })
const timeStr = computed(() => {
  const now = new Date();
  // 简单生成一个时间后缀用于展示
  return now.getHours() + "" + now.getMinutes();
})

const clearWorkspace = () => {
  ElMessageBox.confirm(
      '此操作将清空当前预览区的所有清洗结果，是否继续？',
      '重置台面',
      {
        confirmButtonText: '清空',
        cancelButtonText: '保留',
        type: 'warning',
      }
  )
      .then(() => {
        // 这里的逻辑看你的需求：
        // 如果只想清空右侧结果，保留左侧输入：
        previewLines.value = []

        // 如果想连左侧输入一起清空（彻底重置），解开下面这两行的注释：
        // form.content = ''
        // fileBytes.value = null

        ElMessage.success('台面已清理干净')
      })
      .catch(() => {
        // 取消操作，不做任何事
      })
}

// 1. 管理输入框的引用 (用于控制光标)
const inputRefs = ref({})
const setInputRef = (el, index) => {
  if (el) {
    inputRefs.value[index] = el
  }
}

// 2. 核心：退格键处理逻辑
const handleBackspace = async (e, index) => {
  // 如果是第一行，或者输入框没加载出来，直接忽略，走默认逻辑
  if (index === 0 || !inputRefs.value[index]) return

  // 获取原生 textarea DOM 元素 (Element Plus 的 el-input 包装了一层)
  // 兼容写法：有的版本在 .textarea，有的需要 querySelector
  const inputInstance = inputRefs.value[index]
  const nativeTextarea = inputInstance.textarea || inputInstance.$el.querySelector('textarea')

  if (!nativeTextarea) return

  const cursorPos = nativeTextarea.selectionStart

  // 【关键判断】：只有当光标在最开头 (0) 时，才触发合并逻辑
  if (cursorPos === 0) {
    e.preventDefault() // 阻止默认的删除行为（否则可能删掉上一行的最后一个字）

    const prevLine = previewLines.value[index - 1]
    const currLine = previewLines.value[index]

    // 记录上一行原本的长度（这是合并后光标应该在的位置）
    const originalPrevLength = prevLine.content.length

    // 1. 合并内容：把当前行拼接到上一行后面
    prevLine.content += currLine.content

    // 2. 删除当前行
    // (注意：这里直接操作数组，removeLine 是我们之前写的方法，如果没有可以用 splice)
    previewLines.value.splice(index, 1)

    // 3. 光标归位
    await nextTick() // 等待 Vue 重新渲染 DOM

    const prevInputInstance = inputRefs.value[index - 1]
    const prevNativeTextarea = prevInputInstance?.textarea || prevInputInstance?.$el.querySelector('textarea')

    if (prevNativeTextarea) {
      prevNativeTextarea.focus() // 聚焦上一行
      // 将光标移动到合并点
      prevNativeTextarea.setSelectionRange(originalPrevLength, originalPrevLength)
    }
  }
  // 其他情况（光标在中间或末尾），什么都不用做，浏览器会自动处理删除字符
}

// ... 原有的 watch, computed, debouncePreview, handleFileChange, fetchPreview ...
// (请保持这些逻辑不变，复制之前的代码)
const hasData = computed(() => previewLines.value.length > 0)
const resultCount = computed(() => previewLines.value.length)
let timer = null
const debouncePreview = () => {
  if (timer) clearTimeout(timer)
  previewLoading.value = true
  timer = setTimeout(() => fetchPreview(), 600)
}
watch(form, () => { if (form.content || fileBytes.value) debouncePreview() }, { deep: true })
const handleFileChange = (file) => {
  fileName.value = file.name
  // 如果是文件上传，自动填入文件名作为默认标题（去后缀）
  saveForm.title = file.name.replace(/\.[^/.]+$/, "")
  const reader = new FileReader()
  reader.onload = () => { fileBytes.value = file.raw; debouncePreview() }
  reader.readAsArrayBuffer(file.raw)
}
const fetchPreview = async () => {
  const formData = new FormData()
  const config = { ...form, isPreview: true }
  if (inputType.value === 'file' && fileBytes.value) { formData.append('file', fileBytes.value) }
  formData.append('config', new Blob([JSON.stringify(config)], { type: 'application/json' }))
  try {
    const res = await axios.post('http://localhost:8080/api/text/process', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    previewLines.value = res.data.lines
  } catch (e) { console.error(e) } finally { previewLoading.value = false }
}


// 修改：打开保存弹窗
const openSaveDialog = () => {
  // 如果还没填标题且是手录，尝试截取前几个字
  if (!saveForm.title && inputType.value === 'paste' && form.content) {
    saveForm.title = form.content.substring(0, 10).replace(/\s+/g, '')
  }
  saveDialogVisible.value = true
}

// 修改：确认保存
const confirmSave = async () => {
  if (!saveForm.title) return ElMessage.warning('请输入题名')

  saving.value = true

  const payload = {
    title: saveForm.title, // 用户输入的自定义标题
    category: form.textCategory,
    count: resultCount.value,
    rawContent: form.content,
    data: previewLines.value
  }

  try {
    await axios.post('http://localhost:8080/api/library/save', payload)
    ElMessage.success('文稿已归档至服务器文件系统')
    saveDialogVisible.value = false
    // 清空表单防止重复提交
    saveForm.title = ''
    emit('save-record')
  } catch (e) {
    console.error(e)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
const removeLine = (index) => {
  previewLines.value.splice(index, 1)
  // 删除后不需要重新 fetchPreview，因为这是用户的主动操作
  // 序号会自动重排（因为我们用了 index + 1）
}

</script>

<style scoped>
/* ... 保持之前的样式不变 ... */
.save-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
  background: #f4f4f5;
  padding: 8px;
  border-radius: 4px;
}
/* ... 其他样式 ... */
.process-container { height: 100%; display: flex; flex-direction: column; }
.header-box { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #e6dcc8; padding-bottom: 10px; }
.gufeng-title { margin: 0; color: #5e482d; font-weight: normal; font-size: 24px; letter-spacing: 4px; }
.action-bar { display: flex; align-items: center; gap: 15px; }
.status-tip { color: #8c8272; font-size: 14px; }
.gufeng-btn { background-color: #8e3e3e; border-color: #8e3e3e; font-family: "KaiTi"; letter-spacing: 2px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); transition: all 0.3s; }
.gufeng-btn:hover { background-color: #a64b4b; transform: translateY(-1px); }
.workspace { flex: 1; height: calc(100% - 60px); }
.h-100 { height: 100%; }
.panel-box { height: 100%; background: #fff; border-radius: 4px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); display: flex; flex-direction: column; }
.input-panel { background: #fcfcfc; border: 1px solid #ebeef5; padding: 15px; }
.tabs-header { display: flex; justify-content: center; align-items: center; margin-bottom: 15px; font-size: 16px; color: #909399; cursor: pointer; }
.tabs-header span.active { color: #5e482d; font-weight: bold; border-bottom: 2px solid #8e3e3e; }
.divider { margin: 0 15px; color: #dcdfe6; cursor: default; }
.input-area { flex: 1; display: flex; flex-direction: column; }
.upload-box { width: 100%; flex: 1; display: flex; flex-direction: column; }
.upload-box :deep(.el-upload), .upload-box :deep(.el-upload-dragger) { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; background: #f5f7fa; border: 2px dashed #dcdfe6; }
.upload-inner { text-align: center; color: #909399; }
.upload-icon { font-size: 40px; margin-bottom: 10px; }
.gufeng-input :deep(.el-textarea__inner) { background-color: #fafafa; border: 1px solid #e4e7ed; font-family: "KaiTi"; font-size: 16px; line-height: 1.8; padding: 15px; }
.settings-area { margin-top: 15px; background: #fdfbf6; border: 1px solid #f0e6d2; padding: 10px; border-radius: 4px; }
.setting-title { font-size: 14px; color: #8e3e3e; margin-bottom: 10px; font-weight: bold; border-bottom: 1px dashed #f0e6d2; padding-bottom: 5px; }
.control-row { display: flex; align-items: center; margin-bottom: 8px; font-size: 14px; }
.label { width: 60px; color: #606266; }
.paper-panel { background: #fffdf6; border: 1px solid #dcc8a6; position: relative; }
.paper-bg { flex: 1; padding: 30px 40px; overflow: hidden; display: flex; flex-direction: column; background-image: linear-gradient(90deg, transparent 95%, rgba(220, 200, 166, 0.3) 95%); background-size: 40px 100%; }
.empty-state { height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #c0c4cc; }
.circle-bg { width: 80px; height: 80px; border: 2px solid #e4e7ed; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; color: #dcdfe6; margin-bottom: 10px; }
.text-scroll { overflow-y: auto; height: 100%; padding-right: 10px; }
.text-line { display: flex; align-items: flex-start; margin-bottom: 16px; font-size: 18px; color: #2c3e50; line-height: 1.6; }
.index-seal { display: inline-block; min-width: 24px; height: 24px; line-height: 24px; text-align: center; background-color: #f3e8d3; color: #8f7d62; border-radius: 4px; font-size: 12px; margin-right: 12px; margin-top: 3px; }
.content-char { border-bottom: 1px solid rgba(0,0,0,0.05); width: 100%; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #dcc8a6; border-radius: 3px; }
/* 给带提示的文字增加虚线和问号鼠标，提示用户这里有玄机 */
.help-cursor {
  cursor: help;
  border-bottom: 1px dashed #c0c4cc;
}

/* 复选框组的间距 */
.checkbox-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 15px; /* 拉开一点间距，防止误触 */
}
/* --- 新增样式：可编辑行 --- */

.paper-toolbar {
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px dashed #dcc8a6;
  text-align: right;
}

.edit-tip {
  font-size: 12px;
  color: #8e3e3e; /* 朱砂红提示 */
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 5px;
  opacity: 0.8;
}

.text-line {
  display: flex;
  align-items: flex-start; /* 顶部对齐 */
  margin-bottom: 12px;
  position: relative; /* 为删除按钮定位 */
  padding-right: 30px; /* 给删除按钮留位置 */
  transition: all 0.3s;
}

/* 序号样式微调 */
.index-seal {
  flex-shrink: 0; /* 防止被挤压 */
  margin-top: 6px; /* 对齐文字第一行 */
}

/* 核心：深度修改 el-input 样式，使其隐形 */
.editable-input {
  flex: 1;
}

.editable-input :deep(.el-textarea__inner) {
  background-color: transparent !important; /* 透明背景 */
  border: none !important;         /* 去边框 */
  box-shadow: none !important;     /* 去阴影 */
  padding: 0 10px;                 /* 调整内边距 */
  font-family: "KaiTi", serif;     /* 保持楷体 */
  font-size: 18px;
  color: #2c3e50;
  line-height: 1.6;
  resize: none;
  min-height: 32px !important;
}

/* 鼠标悬停时给一点点背景反馈，提示可编辑 */
.editable-input :deep(.el-textarea__inner):hover,
.editable-input :deep(.el-textarea__inner):focus {
  background-color: rgba(255, 255, 255, 0.4) !important;
  border-radius: 4px;
}

/* 删除按钮样式 */
.line-actions {
  position: absolute;
  right: 0;
  top: 5px;
  opacity: 0; /* 默认隐藏 */
  transition: opacity 0.2s;
}

.text-line:hover .line-actions {
  opacity: 1; /* 悬浮该行时显示 */
}

.delete-icon {
  cursor: pointer;
  color: #dcdfe6;
  font-size: 16px;
  transition: color 0.2s;
}

.delete-icon:hover {
  color: #f56c6c; /* 红色高亮 */
}

/* 列表动画 */
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
/* 确保删除时其他元素平滑移动 */
.list-leave-active {
  position: absolute;
}

.action-bar {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* 原有的保存按钮 (朱砂红) */
.gufeng-btn {
  background-color: #8e3e3e;
  border-color: #8e3e3e;
  font-family: "KaiTi";
  letter-spacing: 2px;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
  transition: all 0.3s;
}
.gufeng-btn:hover {
  background-color: #a64b4b;
  transform: translateY(-1px);
}

/* 新增：清空按钮 (朴素风 - 米色底，深色字) */
.gufeng-btn-plain {
  background-color: transparent;
  border: 1px solid #8c8272;
  color: #5e482d;
  font-family: "KaiTi";
  letter-spacing: 1px;
}
.gufeng-btn-plain:hover {
  background-color: rgba(142, 62, 62, 0.1); /* 淡淡的红色背景 */
  color: #8e3e3e;
  border-color: #8e3e3e;
}
.gufeng-btn-plain.is-disabled {
  background-color: transparent;
  border-color: #dcdfe6;
  color: #c0c4cc;
}
.manual-trigger-box {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px dashed #e6dcc8; /* 加一条虚线分割 */
  text-align: center;
}

.start-btn {
  width: 100%;             /* 撑满宽度，很有气势 */
  height: 48px;            /*稍微高一点 */
  background-color: #5e482d; /* 深褐色，类似墨块或木质 */
  border-color: #5e482d;
  font-family: "KaiTi";
  font-size: 18px;
  letter-spacing: 4px;     /* 字间距拉大 */
  border-radius: 4px;
  box-shadow: 0 4px 6px rgba(94, 72, 45, 0.2);
  transition: all 0.3s;
}

.start-btn:hover {
  background-color: #7a6040;
  border-color: #7a6040;
  transform: translateY(-2px); /* 悬浮效果 */
  box-shadow: 0 6px 12px rgba(94, 72, 45, 0.3);
}

.start-btn.is-disabled {
  background-color: #dcdfe6;
  border-color: #dcdfe6;
  color: #909399;
}
</style>