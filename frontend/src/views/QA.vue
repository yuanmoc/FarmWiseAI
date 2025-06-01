<template>
  <div class="qa-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="chat-card">
          <div class="chat-messages" ref="chatContainer">
            <div v-for="(message, index) in messages" :key="index" :class="['message', message.type]">
              <div class="message-content">
                <div v-if="message.type === 'user'" class="user-avatar">
                  <el-avatar icon="User" />
                </div>
                <div class="message-text">
                  {{ message.content }}
                </div>
                <div v-if="message.type === 'assistant'" class="assistant-avatar">
                  <el-avatar :src="'/robot-avatar.png'" />
                </div>
              </div>
              <div v-if="message.sources && message.sources.length > 0" class="message-sources">
                <div class="sources-title">参考来源：</div>
                <div v-for="(source, sIndex) in message.sources" :key="sIndex" class="source-item">
                  {{ source.title }}
                </div>
              </div>
            </div>
          </div>
          <div class="chat-input">
            <el-input
              v-model="question"
              type="textarea"
              :rows="3"
              placeholder="请输入您的问题..."
              @keyup.enter.ctrl="sendQuestion"
            />
            <el-button type="primary" @click="sendQuestion" :loading="loading">
              发送
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="context-card">
          <template #header>
            <div class="card-header">
              <span>对话上下文</span>
              <el-button type="primary" size="small" @click="clearContext">
                清除上下文
              </el-button>
            </div>
          </template>
          <div class="context-list">
            <div v-for="(message, index) in messages" :key="index" class="context-item">
              <div v-if="message.type === 'user'" class="context-question">Q: {{ message.content }}</div>
              <div v-if="message.type === 'assistant'" class="context-answer">A: {{ message.content }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 添加类型定义
interface Message {
  type: 'user' | 'assistant'
  content: string
  sources?: Array<{ title: string }>
}

const chatContainer = ref<HTMLElement>()
const question = ref('怎么种植西红柿')
const loading = ref(false)
const messages = ref<Message[]>([])
let currentAssistantMessage = ref('')

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const loadChatHistory = async () => {
  try {
    const response = await axios.get('/api/v1/qa/history')
    if (response.data && response.data.length > 0) {
      messages.value = response.data
    } else {
      // 如果没有历史记录，显示欢迎消息
      messages.value = [
        {
          type: 'assistant',
          content: '您好！我是智慧农业咨询助手，请问有什么可以帮您？'
        }
      ]
    }
    scrollToBottom()
  } catch (error) {
    console.error('加载历史记录失败:', error)
    ElMessage.error('加载历史记录失败')
    // 显示默认欢迎消息
    messages.value = [
      {
        type: 'assistant',
        content: '您好！我是智慧农业咨询助手，请问有什么可以帮您？'
      }
    ]
  }
}

const sendQuestion = async () => {
  if (!question.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }

  loading.value = true
  const userQuestion = question.value
  
  // 添加用户问题到消息列表
  messages.value.push({
    type: 'user',
    content: userQuestion
  })

  // 添加一个空的助手回复
  messages.value.push({
    type: 'assistant',
    content: ''
  })

  // 重置当前助手消息
  currentAssistantMessage.value = ''
  
  try {
    const response = await fetch(`${axios.defaults.baseURL}/api/v1/qa/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({question: userQuestion})
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (reader) {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(5))
              if (data.error) {
                ElMessage.error(data.error)
                break
              }
              
              // 更新当前消息
              currentAssistantMessage.value += data.text
              messages.value[messages.value.length - 1].content = currentAssistantMessage.value
              scrollToBottom()
            } catch (e) {
              console.error('Error parsing SSE message:', e)
            }
          }
        }
      }
    }

    question.value = ''
    scrollToBottom()
  } catch (error) {
    ElMessage.error('获取回答失败')
    // 移除空的助手消息
    messages.value.pop()
  } finally {
    loading.value = false
  }
}

const clearContext = async () => {
  try {
    await axios.post('/api/v1/qa/clear-context')
    messages.value = [
      {
        type: 'assistant',
        content: '您好！我是智慧农业咨询助手，请问有什么可以帮您？'
      }
    ]
    ElMessage.success('对话上下文已清除')
  } catch (error) {
    ElMessage.error('清除上下文失败')
  }
}

onMounted(() => {
  loadChatHistory()
})
</script>

<style scoped>
.qa-container {
  padding: 20px;
  height: 100vh;
  box-sizing: border-box;
}

.chat-card {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  margin-bottom: 10px;
}

.chat-input {
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #fff;
}

.context-card {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #fff;
}

.context-list {
  flex: 1;
  overflow-y: auto;
  padding: 15px 15px 55px 15px;
}

.context-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.context-question {
  color: #1890ff;
  margin-bottom: 5px;
}

.context-answer {
  color: #52c41a;
}

.message {
  margin-bottom: 20px;
}

.message-content {
  display: flex;
  align-items: flex-start;
}

.message.user .message-content {
  flex-direction: row;
}

.message.assistant .message-content {
  flex-direction: row-reverse;
}

.message-text {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 8px;
  margin: 0 10px;
  word-break: break-word;
}

.user .message-text {
  background-color: #e6f7ff;
}

.assistant .message-text {
  background-color: #f6ffed;
}

.message-sources {
  margin-top: 10px;
  font-size: 12px;
  color: #666;
  padding-left: 50px;
}

.sources-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.source-item {
  margin-bottom: 3px;
}

:deep(.el-card__body) {
  height: 100%;
  padding: 0;
  display: flex;
  flex-direction: column;
}
</style> 