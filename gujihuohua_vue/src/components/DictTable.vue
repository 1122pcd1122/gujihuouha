<template>
  <div class="table-container fade-in">
    <div class="header-row">
      <h2 class="gufeng-title">典籍数据总览</h2>
      <div class="type-switch">
        <el-radio-group v-model="currentType" @change="handleTypeChange" fill="#8e3e3e">
          <el-radio-button label="idiom">成语</el-radio-button>
          <el-radio-button label="word">汉字</el-radio-button>
          <el-radio-button label="ci">词语</el-radio-button>
          <el-radio-button label="xiehouyu">歇后语</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div class="main-table-box custom-scrollbar">
      <el-table
          :data="tableData"
          style="width: 100%; height: 100%"
          v-loading="loading"
          stripe
          :header-cell-style="{background:'#f3e8d3', color:'#5e482d'}"
      >
        <el-table-column type="index" label="序" width="60" align="center" />

        <el-table-column v-if="currentType==='idiom'" prop="word" label="成语" width="150" font-weight="bold" />
        <el-table-column v-if="currentType==='idiom'" prop="pinyin" label="拼音" width="200" />
        <el-table-column v-if="currentType==='idiom'" prop="explanation" label="释义" min-width="300" show-overflow-tooltip />
        <el-table-column v-if="currentType==='idiom'" prop="derivation" label="出处" min-width="200" show-overflow-tooltip />

        <el-table-column v-if="currentType==='word'" prop="word" label="汉字" width="80" align="center">
          <template #default="scope"><span style="font-size: 20px; font-weight: bold">{{ scope.row.word }}</span></template>
        </el-table-column>
        <el-table-column v-if="currentType==='word'" prop="oldword" label="繁体" width="80" align="center" />
        <el-table-column v-if="currentType==='word'" prop="pinyin" label="拼音" width="100" />
        <el-table-column v-if="currentType==='word'" prop="strokes" label="笔画" width="80" />
        <el-table-column v-if="currentType==='word'" prop="explanation" label="释义" min-width="400" show-overflow-tooltip />

        <el-table-column v-if="currentType==='ci'" prop="ci" label="词语" width="150" font-weight="bold" />
        <el-table-column v-if="currentType==='ci'" prop="explanation" label="解释" min-width="400" show-overflow-tooltip />

        <el-table-column v-if="currentType==='xiehouyu'" prop="riddle" label="谜面" width="250" font-weight="bold" />
        <el-table-column v-if="currentType==='xiehouyu'" prop="answer" label="谜底" min-width="250" />

      </el-table>
    </div>

    <div class="pagination-box">
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="fetchData"
          @current-change="fetchData"
          background
      />
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const currentType = ref('idiom')
const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const handleTypeChange = () => {
  currentPage.value = 1
  fetchData()
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8080/api/dict/page', {
      params: {
        type: currentType.value,
        page: currentPage.value,
        size: pageSize.value
      }
    })
    // MyBatis Plus 分页返回结构: { records: [], total: 100, ... }
    tableData.value = res.data.records
    total.value = res.data.total
  } catch (e) {
    console.error(e)
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.table-container { height: 100%; display: flex; flex-direction: column; font-family: "KaiTi", serif; }
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #e6dcc8; padding-bottom: 10px; }
.gufeng-title { color: #5e482d; border-left: 4px solid #8e3e3e; padding-left: 15px; margin: 0; }

.main-table-box { flex: 1; border: 1px solid #e6dcc8; border-radius: 4px; overflow: hidden; background: #fff; }
.pagination-box { padding-top: 15px; display: flex; justify-content: flex-end; }

/* 滚动条 */
.custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #dcc8a6; border-radius: 3px; }

.fade-in { animation: fadeIn 0.6s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>