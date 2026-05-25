<template>
  <div class="result-panel">
    <div class="panel-header">
      <h3 class="section-title">解析结果</h3>
      
      <!-- 搜索框 -->
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input 
          v-model="searchText"
          type="text"
          placeholder="在结果中搜索..."
          class="search-input"
          @input="handleSearch"
        />
        <span v-if="matchCount > 0" class="match-label">
          {{ currentMatchIndex + 1 }}/{{ matchCount }}
        </span>
        <div class="separator"></div>
        <button 
          class="nav-btn"
          @click="prevMatch"
          :disabled="matchCount === 0"
        >
          ▲
        </button>
        <button 
          class="nav-btn"
          @click="nextMatch"
          :disabled="matchCount === 0"
        >
          ▼
        </button>
      </div>
      
      <button 
        v-if="result"
        class="export-btn"
        @click="$emit('export')"
      >
        导出 JSON
      </button>
    </div>

    <div class="panel-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>正在获取数据...</p>
      </div>

      <div v-else-if="!result" class="empty-state">
        <svg class="empty-icon" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="8" y="8" width="48" height="48" rx="8" stroke="#ddd" stroke-width="2" stroke-dasharray="4 4"/>
          <path d="M24 30L32 38L48 22" stroke="#ddd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <p>请在左侧输入信息并点击"获取数据"</p>
      </div>

      <div v-else class="result-content">
        <pre v-if="!searchText" class="result-text">{{ formattedResult }}</pre>
        <div v-else class="result-text" v-html="highlightedResult"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

defineEmits(['export'])

const props = defineProps({
  result: Object,
  loading: Boolean
})

const searchText = ref('')
const searchMatches = ref([])
const currentMatchIndex = ref(0)

const formattedResult = computed(() => {
  if (!props.result) return ''
  return JSON.stringify(props.result, null, 2)
})

const matchCount = computed(() => searchMatches.value.length)

const handleSearch = () => {
  if (!searchText.value || !formattedResult.value) {
    searchMatches.value = []
    currentMatchIndex.value = 0
    return
  }
  
  // 查找所有匹配位置
  const text = formattedResult.value
  const matches = []
  let index = 0
  const searchLen = searchText.value.length
  
  while (index < text.length) {
    const idx = text.indexOf(searchText.value, index)
    if (idx === -1) break
    matches.push(idx)
    index = idx + searchLen
  }
  
  searchMatches.value = matches
  currentMatchIndex.value = 0
}

const highlightedResult = computed(() => {
  if (!searchText.value || searchMatches.value.length === 0) {
    return escapeHtml(formattedResult.value)
  }
  
  const text = formattedResult.value
  const searchLen = searchText.value.length
  let resultHtml = ''
  let lastPos = 0
  
  for (let i = 0; i < searchMatches.value.length; i++) {
    const pos = searchMatches.value[i]
    // 添加匹配前的文本
    resultHtml += escapeHtml(text.substring(lastPos, pos))
    // 添加高亮的匹配文本
    if (i === currentMatchIndex.value) {
      // 当前匹配用橙色高亮
      resultHtml += `<span style="background-color: #ffa500; color: black; font-weight: bold;">${escapeHtml(searchText.value)}</span>`
    } else {
      // 其他匹配用黄色高亮
      resultHtml += `<span style="background-color: yellow; color: black;">${escapeHtml(searchText.value)}</span>`
    }
    lastPos = pos + searchLen
  }
  
  // 添加剩余文本
  resultHtml += escapeHtml(text.substring(lastPos))
  
  return resultHtml
})

const escapeHtml = (text) => {
  if (!text) return ''
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

const prevMatch = () => {
  if (searchMatches.value.length === 0) return
  if (currentMatchIndex.value > 0) {
    currentMatchIndex.value--
  } else {
    currentMatchIndex.value = searchMatches.value.length - 1
  }
  scrollToCurrentMatch()
}

const nextMatch = () => {
  if (searchMatches.value.length === 0) return
  if (currentMatchIndex.value < searchMatches.value.length - 1) {
    currentMatchIndex.value++
  } else {
    currentMatchIndex.value = 0
  }
  scrollToCurrentMatch()
}

const scrollToCurrentMatch = () => {
  // 等待 DOM 更新后滚动
  nextTick(() => {
    const container = document.querySelector('.result-content')
    if (container) {
      // 简单的滚动到可见
      container.scrollTop = container.scrollHeight * (currentMatchIndex.value / Math.max(searchMatches.value.length, 1))
    }
  })
}
</script>

<style scoped>
.result-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f5f7fa;
  height: 100vh;
}

.panel-header {
  padding: 45px 40px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  background: #f5f7fa;
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  color: #606266;
  margin: 0;
  flex-shrink: 0;
}

.search-container {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 2px 8px;
  height: 34px;
  flex: 1;
  max-width: 350px;
}

.search-container:focus-within {
  border-color: #409eff;
}

.search-icon {
  font-size: 13px;
  color: #909399;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 13px;
  outline: none;
  padding: 0;
}

.match-label {
  font-size: 12px;
  color: #909399;
  min-width: 35px;
  text-align: right;
}

.separator {
  width: 1px;
  height: 16px;
  background: #e4e7ed;
}

.nav-btn {
  width: 26px;
  height: 26px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: #606266;
  font-size: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Segoe UI Symbol', 'Microsoft YaHei', sans-serif;
}

.nav-btn:hover:not(:disabled) {
  background: #f5f7fa;
  color: #409eff;
}

.nav-btn:disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.export-btn {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;
  flex-shrink: 0;
}

.export-btn:hover {
  background: #66b1ff;
}

.panel-content {
  flex: 1;
  overflow: auto;
  padding: 20px 40px 45px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f0f0f0;
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 16px;
}

.loading-state p,
.empty-state p {
  font-size: 14px;
  color: #909399;
}

.result-content {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  height: 100%;
  overflow: auto;
  box-sizing: border-box;
}

.result-text {
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.result-text ::v-deep span {
  display: inline;
}
</style>
