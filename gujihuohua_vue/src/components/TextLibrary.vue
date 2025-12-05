<template>
  <div class="library-container fade-in">
    <div class="header-row">
      <h2 class="gufeng-title">珍藏语料库</h2>
      <el-button circle :icon="Refresh" @click="fetchList" title="刷新列表" />
    </div>

    <div class="table-box">
      <el-table
          v-loading="loading"
          :data="libraryList"
          style="width: 100%"
          height="100%"
          :header-cell-style="{background:'#f3e8d3', color:'#5e482d', borderColor:'#e6dcc8'}"
          :cell-style="{borderColor:'#f0e6d2', backgroundColor: 'transparent'}"
      >
        <el-table-column type="index" label="序" width="60" align="center" />
        <el-table-column prop="title" label="篇名" min-width="200">
          <template #default="scope">
            <span class="book-title">《{{ scope.row.title }}》</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="部类" width="100" align="center">
          <template #default="scope">
            <el-tag color="#fcf6e9" style="color: #8e3e3e; border-color: #e6dcc8;">
              {{ scope.row.category }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sentenceCount" label="句数" width="100" align="center" />
        <el-table-column prop="createTime" label="收录时间" width="180" align="center">
          <template #default="scope">
            {{ formatTime(scope.row.createTime) }}
          </template>
        </el-table-column>
        <el-table-column label="处置" width="250" align="center">
          <template #default="scope">
            <el-button size="small" type="warning" plain :icon="View" @click="handlePreview(scope.row)">预览</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(scope.row.id)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
        v-model="previewVisible"
        title="文稿阅览"
        width="800px"
        class="ancient-dialog"
        align-center
    >
      <div class="paper-panel custom-scrollbar">
        <div class="paper-bg">
          <h3 class="preview-title">{{ currentPreview.title }}</h3>
          <div class="text-content">
            <div v-for="item in currentContent" :key="item.index" class="text-line">
              <span class="index-seal">{{ item.index }}</span>
              <span class="content-char">{{ item.content }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, onMounted } from 'vue'
import { Refresh, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 修正点3：去掉 const emit = ，因为我们在 script 里没用到它，只在 template 里用了 $emit
defineEmits(['use-record'])

const loading = ref(false)
const libraryList = ref([])
const previewVisible = ref(false)
const currentPreview = ref({})
const currentContent = ref([])

// 格式化时间
const formatTime = (timeStr) => {
  if(!timeStr) return ''
  return timeStr.replace('T', ' ').substring(0, 16)
}

// 获取列表
const fetchList = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8080/api/library/list')
    libraryList.value = res.data
  } catch (e) {
    ElMessage.error('获取语料库失败')
  } finally {
    loading.value = false
  }
}

// 删除
const handleDelete = (id) => {
  ElMessageBox.confirm('确认移除该条古籍数据吗？', '警告', { type: 'warning' })
      .then(async () => {
        await axios.delete(`http://localhost:8080/api/library/${id}`)
        ElMessage.success('已移除')
        fetchList()
      })
}

// 修改 TextLibrary.vue 中的 handlePreview
const handlePreview = async (row) => {
  currentPreview.value = row
  try {
    const res = await axios.get(`http://localhost:8080/api/library/detail/${row.id}`)

    // 注意：后端现在返回的是 { info: {}, processedJson: "..." }
    const dataStr = res.data.processedJson

    if (dataStr) {
      currentContent.value = JSON.parse(dataStr)
    } else {
      currentContent.value = []
    }
    previewVisible.value = true
  } catch (e) {
    console.error(e)
    ElMessage.error('无法读取文件内容')
  }
}
onMounted(() => {
  fetchList()
})

defineExpose({ fetchList })
</script>

<style scoped>
.library-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 2px solid #e6dcc8;
  padding-bottom: 10px;
}
.gufeng-title {
  margin: 0;
  color: #5e482d;
  font-weight: normal;
  font-size: 24px;
  border-left: 4px solid #8e3e3e;
  padding-left: 15px;
}
.table-box {
  flex: 1;
  background: #fff;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  border: 1px solid #e6dcc8;
}
.book-title {
  font-weight: bold;
  color: #2c3e50;
  font-family: "KaiTi";
}
.fade-in { animation: fadeIn 0.6s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* 预览弹窗样式 */
.paper-panel {
  height: 500px;
  overflow-y: auto;
  background: #fffdf6;
  border: 1px solid #dcc8a6;
  padding: 20px;
}
.paper-bg {
  background-image: linear-gradient(90deg, transparent 95%, rgba(220, 200, 166, 0.3) 95%);
  background-size: 40px 100%;
  min-height: 100%;
}
.preview-title {
  text-align: center;
  font-family: "KaiTi";
  font-size: 22px;
  color: #5e482d;
  margin-bottom: 30px;
}
.text-line {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  font-size: 18px;
  color: #2c3e50;
  line-height: 1.6;
  font-family: "KaiTi";
}
.index-seal {
  display: inline-block;
  min-width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  background-color: #f3e8d3;
  color: #8f7d62;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 12px;
  margin-top: 3px;
}
.content-char {
  border-bottom: 1px solid rgba(0,0,0,0.05);
  width: 100%;
}
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #dcc8a6; border-radius: 3px; }
</style>

<style>
.ancient-dialog .el-dialog__header {
  background-color: #fcf9f2;
  border-bottom: 1px solid #e6dcc8;
  margin-right: 0;
}
.ancient-dialog .el-dialog__title {
  font-family: "KaiTi";
  color: #5e482d;
  font-size: 20px;
}
.ancient-dialog .el-dialog__body {
  padding: 0;
  background-color: #fcf9f2;
}
</style>