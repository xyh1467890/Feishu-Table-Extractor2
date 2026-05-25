<template>
  <div class="app-container">
    <SidebarPanel 
      :loading="loading"
      :progress="progress"
      @fetch="handleFetch"
    />
    <ResultPanel 
      :result="result"
      :loading="loading"
      @export="handleExport"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SidebarPanel from './components/SidebarPanel.vue'
import ResultPanel from './components/ResultPanel.vue'
import { fetchBitableData } from './api'

const loading = ref(false)
const progress = ref('')
const result = ref(null)

const handleFetch = async (params) => {
  loading.value = true
  progress.value = '正在获取数据...'
  result.value = null

  try {
    const data = await fetchBitableData(params)
    result.value = data
    progress.value = '✓ 获取成功！'
  } catch (error) {
    progress.value = `✗ 获取失败: ${error.message}`
  } finally {
    loading.value = false
  }
}

const handleExport = () => {
  if (!result.value) return

  const blob = new Blob([JSON.stringify(result.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `bitable-data-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.app-container {
  display: flex;
  width: 100%;
  height: 100vh;
  background-color: #f5f7fa;
  overflow: hidden;
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
</style>
