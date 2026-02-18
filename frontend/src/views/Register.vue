<template>
  <div class="register-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>用户注册</span>
        </div>
      </template>
      <el-form ref="registerFormRef" :model="registerForm" status-icon label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" autocomplete="off" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" autocomplete="off" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" autocomplete="off" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">注册</el-button>
          <el-button @click="goToLogin">返回登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from '../utils/request'

const router = useRouter()
const registerForm = reactive({
  username: '',
  password: '',
  email: ''
})

const submitForm = async () => {
     if(!registerForm.username || !registerForm.password) {
        ElMessage.error('用户名和密码必填')
        return
    }

    try {
        await axios.post('/users/register', {
            username: registerForm.username,
            password: registerForm.password,
            email: registerForm.email || undefined,
            role: 'user'
        })
        ElMessage.success('注册成功，请登录')
        router.push('/login')
    } catch (error) {
        // Error handled in interceptor
    }
}

const goToLogin = () => {
    router.push('/login')
}
</script>

<style scoped>
.register-container {
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
