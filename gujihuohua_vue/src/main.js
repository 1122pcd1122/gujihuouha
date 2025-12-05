import { createApp } from 'vue'
import App from './App.vue'

// --- 必须添加下面这两行 ---
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// ------------------------


const app = createApp(App)

// --- 必须添加这一行 ---
app.use(ElementPlus)
// -------------------

app.mount('#app')
