<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// Main app component
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 
    'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #2c4a6d 0%, #1e3a5f 100%);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #1e3a5f 0%, #2c4a6d 100%);
}

/* Element Plus 自定义样式 */
.el-button {
  transition: all 0.3s ease;
}

.el-button:hover {
  transform: translateY(-2px);
}

.el-card {
  transition: all 0.3s ease;
}

.el-card:hover {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}
</style>
