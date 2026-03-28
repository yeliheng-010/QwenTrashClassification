<template>
  <div class="login-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>用户登录</span>
        </div>
      </template>
      <el-form ref="loginFormRef" :model="loginForm" status-icon label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" autocomplete="off" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" autocomplete="off" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">登录</el-button>
          <el-button @click="goToRegister">去注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from '../utils/request' // 导入配置好的 axios 实例

const router = useRouter()
const loginForm = reactive({
  username: '',
  password: ''
})

const submitForm = async () => {
    if(!loginForm.username || !loginForm.password) {
        ElMessage.error('请输入用户名和密码')
        return
    }
    
    try {
        const res: any = await axios.post('/users/login', loginForm)
            localStorage.setItem('token', res.access_token)
            localStorage.setItem('username', res.username)
            localStorage.setItem('is_admin', String(res.is_admin))
            ElMessage.success('登录成功')
            router.push('/')
    } catch (error) {
        // 错误已经在 request.ts 中统一处理了
    }
}

const goToRegister = () => {
    router.push('/register')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  /* 背景已在全局 body 中设置 */
  background-color: transparent;
}
.box-card {
  width: 400px;
  /* 磨砂玻璃效果 */
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}
/* 深度选择器修改 Element Plus 内部样式 */
:deep(.el-card__header) {
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
.card-header {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}
</style>
