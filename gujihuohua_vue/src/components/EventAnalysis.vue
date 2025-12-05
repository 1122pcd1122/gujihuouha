<template>
  <div class="analysis-container fade-in">
    <div class="header-row">
      <h2 class="gufeng-title">古籍事件脉络抽取</h2>
      <el-button type="primary" class="gufeng-btn" @click="loadEventData">
        <el-icon style="margin-right:5px"><Timer /></el-icon> 载入事件流
      </el-button>
    </div>

    <div class="timeline-workspace custom-scrollbar">
      <div v-if="events.length === 0" class="empty-state">暂无事件数据</div>

      <el-timeline v-else>
        <el-timeline-item
            v-for="(activity, index) in events"
            :key="index"
            :timestamp="activity.time"
            placement="top"
            :color="activity.color"
            size="large"
        >
          <el-card class="event-card">
            <h4 class="event-title">{{ activity.title }}</h4>
            <p class="event-desc">{{ activity.content }}</p>
            <div class="event-tags">
              <el-tag size="small" effect="plain" type="danger" v-for="role in activity.roles" :key="role">{{ role }}</el-tag>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref } from 'vue'
import { Timer } from '@element-plus/icons-vue'

const events = ref([])

const loadEventData = () => {
  // 模拟数据
  events.value = [
    { time: '秦二世元年（前209年）', title: '斩蛇起义', content: '高祖醉酒，夜径泽中，令一人行前。行前者还报曰：“前有大蛇当径，愿还。”高祖醉，曰：“壮士行，何畏！”乃前，拔剑击斩蛇。', roles: ['刘邦'], color: '#8e3e3e' },
    { time: '汉元年（前206年）', title: '鸿门宴', content: '项羽大怒，欲击刘邦。沛公左司马曹无伤使人言于项羽... 沛公旦日从百余骑来见项王。', roles: ['项羽', '刘邦', '范增', '项庄'], color: '#b8860b' },
    { time: '汉五年（前202年）', title: '垓下之战', content: '项王军壁垓下，兵少食尽，汉军及诸侯兵围之数重。夜闻汉军四面皆楚歌，项王乃大惊。', roles: ['项羽', '虞姬'], color: '#2b4b64' }
  ]
}
</script>

<style scoped>
.analysis-container { height: 100%; display: flex; flex-direction: column; }
.header-row { display: flex; justify-content: space-between; padding-bottom: 10px; border-bottom: 2px solid #e6dcc8; margin-bottom: 20px; }
.gufeng-title { color: #5e482d; border-left: 4px solid #8e3e3e; padding-left: 15px; margin: 0; }
.gufeng-btn { background: #8e3e3e; border: none; font-family: "KaiTi"; }
.timeline-workspace { flex: 1; overflow-y: auto; padding: 20px 100px; background: #fcf9f2; }
.event-card { border: 1px solid #e6dcc8; background: #fffdf6; }
.event-title { color: #8e3e3e; font-size: 18px; margin: 0 0 10px 0; font-family: "KaiTi"; }
.event-desc { color: #555; line-height: 1.6; }
.event-tags { margin-top: 10px; display: flex; gap: 5px; }
.empty-state { text-align: center; color: #ccc; padding-top: 100px; }
/* 滚动条美化 */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #dcc8a6; border-radius: 3px; }
</style>