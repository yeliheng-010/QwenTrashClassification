<template>
  <div class="feedback-container">
    <el-container>
      <el-header class="header">
        <div class="logo" @click="goHome">智能垃圾分类系统</div>
        <div class="user-info">
          <el-button @click="goHome">返回首页</el-button>
          <el-button type="danger" link @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="main-content">
        <el-row justify="center">
            <el-col :span="12" :xs="24">
                <el-card class="feedback-card">
                    <template #header>
                        <div class="card-header">
                            <span>意见反馈</span>
                        </div>
                    </template>
                    <div class="form-content">
                        <el-alert
                            title="您的建议是我们进步的动力"
                            type="info"
                            :closable="false"
                            show-icon
                            style="margin-bottom: 20px"
                        />
                        <el-form :model="form" ref="formRef">
                            <el-form-item prop="content">
                                <el-input
                                    v-model="form.content"
                                    type="textarea"
                                    :rows="8"
                                    placeholder="请填写您的反馈意见或遇到的问题..."
                                    maxlength="1000"
                                    show-word-limit
                                />
                            </el-form-item>
                            <el-form-item>
                                <el-button type="primary" class="submit-btn" @click="submitFeedback" :loading="loading">
                                    提交反馈
                                </el-button>
                            </el-form-item>
                        </el-form>
                    </div>
                </el-card>
            </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from '../utils/request'

const router = useRouter()
const loading = ref(false)
const form = reactive({
    content: ''
})

const submitFeedback = async () => {
    if (!form.content.trim()) {
        ElMessage.warning('请输入反馈内容')
        return
    }

    loading.value = true
    try {
        await axios.post('/feedbacks/', { content: form.content })
        ElMessage.success('感谢您的反馈！我们会尽快处理。')
        form.content = '' // 清空输入
        setTimeout(() => {
            router.push('/')
        }, 1500)
    } catch (error) {
        // error handled
    } finally {
        loading.value = false
    }
}

const goHome = () => {
    router.push('/')
}

const logout = () => {
    localStorage.removeItem('token')
    router.push('/login')
}
</script>

<style scoped>
.feedback-container {
  min-height: 100vh;
  /* 背景已在全局 body 中设置 */
  background-color: transparent;
}
.header {
  /* 磨砂玻璃效果 */
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 0 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}
.logo {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(120deg, var(--eco-green), #409EFF);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  cursor: pointer;
}
.main-content {
  padding: 40px;
}
.feedback-card {
    /* 磨砂玻璃效果 */
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border-radius: 16px;
}
.card-header {
    font-size: 18px;
    font-weight: bold;
    color: #303133;
}
.submit-btn {
  width: 100%;
  background-color: var(--eco-green);
  border-color: var(--eco-green);
  font-weight: bold;
  transition: all 0.3s ease;
}
.submit-btn:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
}

:deep(.el-card__header) {
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    padding: 15px 20px;
}
/* 输入框背景透明化 */
:deep(.el-textarea__inner) {
    background-color: rgba(255, 255, 255, 0.5);
}
:deep(.el-textarea__inner:focus) {
    background-color: #fff;
    box-shadow: 0 0 0 1px var(--eco-green) inset;
}
</style>
