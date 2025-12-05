const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  // 确保没有关闭热更新
  devServer: {
    hot: true, // 开启热更新
    open: true // 启动后自动打开浏览器
  }
})
