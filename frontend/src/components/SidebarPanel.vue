<template>
  <div class="sidebar-panel">
    <div class="sidebar-header">
      <h1 class="title">飞书多维表格元数据获取工具</h1>
      <p class="subtitle">需要帮助请联系<a href="https://www.larkoffice.com/invitation/page/add_contact/?token=6e2ma113-ab71-48a6-a684-2c8bb2e38e32" target="_blank">作者</a></p>
    </div>

    <div class="sidebar-content">
      <!-- 认证方式 -->
      <div class="section">
        <h3 class="section-title">认证方式</h3>
        
        <div class="tabs-container">
          <button 
            v-for="tab in tabs" 
            :key="tab.key"
            :class="['tab-button', { active: activeTab === tab.key }]"
            @click="handleTabChange(tab.key)"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="tab-content">
          <!-- Token 标签页 -->
          <div v-if="activeTab === 'token'" class="tab-panel">
            <p class="info-text">
              直接输入已有的 <a href="#" @click.prevent="showTokenHelp" class="link">User Access Token</a>。
            </p>
            <p class="info-text">
              <a href="https://open.feishu.cn/api-explorer" target="_blank" class="link">前往 API 调试台</a> 获取。
            </p>
            
            <div class="input-group">
              <input 
                v-model="token" 
                :type="showToken ? 'text' : 'password'"
                placeholder="粘贴 User Access Token"
                class="form-input"
              />
              <button class="toggle-btn" @click="showToken = !showToken">
                {{ showToken ? '隐藏' : '显示' }}
              </button>
              <button class="api-btn" @click="openApiExplorer">打开调试台</button>
            </div>
          </div>

          <!-- OAuth 标签页 -->
          <div v-if="activeTab === 'oauth'" class="tab-panel">
            <p class="info-text">
              通过应用凭证一键获取 User Token。<br>
              <a href="https://open.feishu.cn" target="_blank" class="link">前往开放平台</a> 配置回调 URI: 
              <code class="code">http://localhost:3000</code>
            </p>
            
            <div class="form-group">
              <input 
                v-model="appId" 
                type="text" 
                placeholder="App ID (cli_...)"
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <input 
                v-model="appSecret" 
                type="password" 
                placeholder="App Secret"
                class="form-input"
              />
            </div>
            
            <button class="oauth-btn" @click="startOAuthFlow" :disabled="oauthLoading">
              {{ oauthLoading ? '授权中...' : '浏览器一键授权' }}
            </button>
            
            <p v-if="oauthStatus" :class="['status-text', oauthStatus.includes('错误') ? 'error' : 'success']">
              {{ oauthStatus }}
            </p>
          </div>

          <!-- Cookie 标签页 -->
          <div v-if="activeTab === 'cookie'" class="tab-panel">
            <div class="cookie-section">
              <p class="cookie-section-title">方式一：浏览器自动提取（推荐）</p>
              <p class="cookie-section-desc">自动打开飞书网页，登录后一键提取 Cookie。</p>
              
              <div class="cookie-buttons">
                <button class="get-cookie-btn" @click="startGetCookie" :disabled="cookieLoading">
                  🚀 启动浏览器
                </button>
                <button class="confirm-login-btn" @click="confirmGetCookie" :disabled="!confirmLoginEnabled || cookieLoading">
                  ✓ 已登录，提取 Cookie
                </button>
              </div>
              
              <p v-if="cookieStatus" :class="['status-text', cookieStatus.includes('错误') ? 'error' : 'warning']">
                {{ cookieStatus }}
              </p>
            </div>
            
            <div class="divider">
              <span class="divider-text">或</span>
            </div>
            
            <div class="cookie-section">
              <div class="cookie-header">
                <p class="cookie-section-title">方式二：手动输入</p>
                <button class="clear-btn" @click="cookie = ''">清空内容</button>
              </div>
              
              <textarea 
                v-model="cookie" 
                placeholder="请在此粘贴完整的飞书 Cookie..."
                rows="4"
                class="form-textarea"
              ></textarea>
            </div>
          </div>
        </div>
      </div>

      <!-- 目标数据表 -->
      <div class="section">
        <h3 class="section-title">目标数据表</h3>
        <input 
          v-model="feishuUrl" 
          type="text" 
          placeholder="https://xxx.feishu.cn/base/..."
          class="form-input"
        />
        
        <label class="checkbox-label">
          <input 
            v-model="fetchRecords" 
            type="checkbox"
            :disabled="activeTab === 'cookie'"
          />
          同时获取数据表记录内容
        </label>
      </div>

      <!-- 获取按钮 -->
      <button 
        class="fetch-btn"
        :disabled="loading || !canFetch"
        @click="handleFetch"
      >
        {{ loading ? '获取中...' : '获取数据' }}
      </button>

      <div v-if="progress" class="progress-text" :class="{ error: progress.includes('失败'), success: progress.includes('成功') }">
        {{ progress }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const emit = defineEmits(['fetch'])

const props = defineProps({
  loading: Boolean,
  progress: String
})

const tabs = [
  { key: 'token', label: 'Token' },
  { key: 'oauth', label: 'OAuth' },
  { key: 'cookie', label: 'Cookie（不推荐）' }
]

const activeTab = ref('token')
const feishuUrl = ref('')
const token = ref('')
const appId = ref('')
const appSecret = ref('')
const cookie = ref('')
const showToken = ref(false)
const fetchRecords = ref(true)

// OAuth 相关
const oauthLoading = ref(false)
const oauthStatus = ref('')

// Cookie 相关
const cookieLoading = ref(false)
const cookieStatus = ref('')
const confirmLoginEnabled = ref(false)

const canFetch = computed(() => {
  if (!feishuUrl.value) return false
  if (activeTab.value === 'cookie') {
    return !!cookie.value
  }
  return !!token.value
})

const handleTabChange = (tabKey) => {
  if (tabKey === 'cookie') {
    // 切换到 Cookie 标签页时禁用记录获取
    fetchRecords.value = false
  } else if (activeTab.value === 'cookie') {
    // 从 Cookie 标签页切出时恢复记录获取
    fetchRecords.value = true
  }
  activeTab.value = tabKey
}

const showTokenHelp = () => {
  alert('请查看原应用中的视频教程，或前往飞书开放平台获取 User Access Token')
}

const openApiExplorer = () => {
  window.open('https://open.feishu.cn/api-explorer', '_blank')
}

const startOAuthFlow = () => {
  if (!appId.value) {
    alert('请输入 App ID')
    return
  }
  if (!appSecret.value) {
    alert('请输入 App Secret')
    return
  }
  
  oauthLoading.value = true
  oauthStatus.value = '正在打开浏览器进行授权...'
  
  // 这里简化处理，实际应该实现完整的 OAuth 流程
  setTimeout(() => {
    oauthLoading.value = false
    oauthStatus.value = '✗ OAuth 功能需要后端支持'
  }, 2000)
}

const startGetCookie = () => {
  cookieLoading.value = true
  cookieStatus.value = '正在准备...'
  
  // 这里简化处理，实际应该启动浏览器自动化
  setTimeout(() => {
    cookieStatus.value = '请在浏览器中登录飞书，然后点击"已登录，提取 Cookie"'
    confirmLoginEnabled.value = true
    cookieLoading.value = false
  }, 1500)
}

const confirmGetCookie = () => {
  cookieLoading.value = true
  cookieStatus.value = '正在提取 Cookie...'
  
  // 这里简化处理
  setTimeout(() => {
    cookieStatus.value = '✗ Cookie 自动提取功能需要后端支持'
    cookieLoading.value = false
    confirmLoginEnabled.value = false
  }, 1500)
}

const handleFetch = () => {
  let authType, authData

  if (activeTab.value === 'cookie') {
    authType = 'cookie'
    authData = cookie.value
  } else {
    authType = 'token'
    authData = token.value
  }

  emit('fetch', {
    authType,
    authData,
    feishuUrl: feishuUrl.value,
    fetchRecords: activeTab.value === 'cookie' ? false : fetchRecords.value
  })
}
</script>

<style scoped>
.sidebar-panel {
  width: 420px;
  background: #ffffff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.sidebar-header {
  padding: 45px 35px 0;
}

.title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  letter-spacing: 1px;
  margin: 0 0 6px;
}

.subtitle {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.subtitle a {
  color: #409eff;
  text-decoration: none;
}

.sidebar-content {
  padding: 0 35px 45px;
  flex: 1;
  overflow-y: auto;
}

.section {
  margin-top: 15px;
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  color: #606266;
  margin: 0 0 5px;
}

.tabs-container {
  display: flex;
  gap: 0;
  margin-bottom: 0;
  padding-top: 10px;
}

.tab-button {
  padding: 8px 16px 8px 0;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #909399;
  margin-right: 16px;
}

.tab-button.active {
  color: #409eff;
  border-bottom-color: #409eff;
}

.tab-button:hover:not(.active) {
  color: #303133;
}

.tab-content {
  padding-top: 15px;
}

.tab-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-text {
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
}

.link {
  color: #409eff;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.form-group {
  margin-bottom: 0;
}

/* 统一的输入框样式 */
.form-input {
  width: 100%;
  height: 40px;
  padding: 0 14px;
  background: #ffffff;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  color: #303133;
  font-size: 13px;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-textarea {
  width: 100%;
  min-height: 100px;
  padding: 10px 14px;
  background: #ffffff;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  color: #303133;
  font-size: 13px;
  box-sizing: border-box;
  resize: vertical;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #409eff;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #c0c4cc;
}

.input-group {
  display: flex;
  gap: 10px;
}

.input-group .form-input {
  flex: 1;
}

.toggle-btn,
.api-btn {
  padding: 0 16px;
  height: 40px;
  background: #ffffff;
  color: #606266;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.toggle-btn:hover,
.api-btn:hover {
  background: #ecf5ff;
  color: #409eff;
  border-color: #c6e2ff;
}

.oauth-btn {
  width: 100%;
  padding: 0 16px;
  height: 40px;
  background: #ffffff;
  color: #606266;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.oauth-btn:hover:not(:disabled) {
  background: #ecf5ff;
  color: #409eff;
  border-color: #c6e2ff;
}

.oauth-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cookie-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cookie-section-title {
  color: #303133;
  font-weight: bold;
  font-size: 13px;
  margin: 0;
}

.cookie-section-desc {
  color: #909399;
  font-size: 12px;
  margin: 0 0 5px;
}

.cookie-buttons {
  display: flex;
  gap: 10px;
}

.get-cookie-btn {
  padding: 0 15px;
  height: 36px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: normal;
  cursor: pointer;
  transition: background 0.2s;
}

.get-cookie-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.get-cookie-btn:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}

.confirm-login-btn {
  padding: 0 15px;
  height: 36px;
  background: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: normal;
  cursor: pointer;
  transition: background 0.2s;
}

.confirm-login-btn:hover:not(:disabled) {
  background: #85ce61;
}

.confirm-login-btn:disabled {
  background: #b3e19d;
  cursor: not-allowed;
}

.cookie-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.clear-btn {
  padding: 4px 10px;
  background: transparent;
  color: #909399;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover {
  color: #f56c6c;
  border-color: #fbc4c4;
  background-color: #fef0f0;
}

.divider {
  display: flex;
  align-items: center;
  margin: 5px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #ebeef5;
}

.divider-text {
  color: #c0c4cc;
  font-size: 13px;
  padding: 0 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 12px;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #ffffff;
  cursor: pointer;
  appearance: none;
  position: relative;
}

.checkbox-label input[type="checkbox"]:checked {
  background: #409eff;
  border-color: #409eff;
}

.checkbox-label input[type="checkbox"]:checked::after {
  content: '✓';
  position: absolute;
  color: white;
  font-size: 12px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.status-text {
  font-size: 12px;
  margin: 5px 0 0;
}

.status-text.success {
  color: #67c23a;
}

.status-text.warning {
  color: #e6a23c;
}

.status-text.error {
  color: #f56c6c;
}

.fetch-btn {
  width: 100%;
  padding: 0 14px;
  height: 44px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 20px;
  transition: background 0.2s;
}

.fetch-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.fetch-btn:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}

.progress-text {
  margin-top: 10px;
  padding: 5px;
  text-align: center;
  font-size: 13px;
  font-weight: bold;
}

.progress-text.success {
  color: #67c23a;
}

.progress-text.error {
  color: #f56c6c;
}
</style>
