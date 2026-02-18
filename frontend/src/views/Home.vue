<template>
  <div class="home-container">
    <el-container>
      <el-header class="header">
        <div class="logo">智能垃圾分类系统</div>
        <div class="user-info">
          <el-button type="text" class="nav-link" @click="router.push('/knowledge')">环保资讯</el-button>
          <el-button v-if="isAdmin" type="primary" @click="router.push('/admin')">管理后台</el-button>
          <el-button @click="router.push('/history')">个人中心 / 历史记录</el-button>
          <el-button @click="router.push('/feedback')">意见反馈</el-button>
          <el-button @click="openChangePasswordDialog">修改密码</el-button>
          <el-button type="danger" link @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="main-content">
        <el-row :gutter="40" justify="center">
          <el-col :span="10" :xs="24">
            <!-- 1. 本地词典检索卡片 -->
            <el-card class="input-card hover-effect" style="margin-bottom: 20px; height: auto;">
              <template #header>
                <div class="card-header">
                  <span><el-icon class="header-icon"><Notebook /></el-icon> 本地词典检索</span>
                </div>
              </template>
              <div class="search-area">
                <el-input 
                    v-model="searchKeyword" 
                    placeholder="输入关键词查询 (如: 电池)" 
                    clearable
                    @keyup.enter="handleSearch"
                >
                    <template #append>
                        <el-button :icon="Search" @click="handleSearch" :loading="searchLoading"/>
                    </template>
                </el-input>

                <!-- 搜索结果展示 -->
                <div v-if="searchResultList.length > 0" class="search-results">
                    <el-table :data="searchResultList" size="small" style="width: 100%" :show-header="false">
                        <el-table-column prop="item_name" width="120">
                            <template #default="scope">
                                <strong>{{ scope.row.item_name }}</strong>
                            </template>
                        </el-table-column>
                        <el-table-column prop="category" width="100">
                             <template #default="scope">
                                <el-tag size="small" :type="getCategoryType(scope.row.category)">{{ scope.row.category }}</el-tag>
                             </template>
                        </el-table-column>
                         <el-table-column prop="description" show-overflow-tooltip />
                    </el-table>
                </div>
                <div v-else-if="hasSearched && !searchLoading" class="no-result">
                    <p>未找到相关物品，请尝试使用下方 <strong>AI 智能识别</strong></p>
                </div>
              </div>
            </el-card>

            <!-- 2. AI 智能识别卡片 -->
            <el-card class="input-card hover-effect">
              <template #header>
                <div class="card-header">
                  <span><el-icon class="header-icon"><Search /></el-icon> 开始识别</span>
                </div>
              </template>
              
              <!-- 输入区域 -->
              <el-form label-position="top">
                <el-form-item label="文本描述">
                  <el-input 
                    v-model="textInput" 
                    placeholder="请输入物品名称（如：香蕉皮）" 
                    clearable
                    :disabled="!!imageFile"
                    prefix-icon="Edit"
                  />
                </el-form-item>
                
                <el-divider>Or</el-divider>
                
                <el-form-item label="上传图片">
                  <el-upload
                    class="upload-demo"
                    drag
                    action="#"
                    :auto-upload="false"
                    :limit="1"
                    :on-change="handleFileChange"
                    :on-remove="handleRemove"
                    :file-list="fileList"
                    list-type="picture"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      拖拽文件到此处或 <em>点击上传</em>
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        支持 jpg/png 文件，大小不超过 5MB
                      </div>
                    </template>
                  </el-upload>
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" size="large" class="submit-btn" @click="startRecognition" :loading="loading">
                    开始智能识别
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>
          
          <!-- 结果展示区域 -->
          <el-col :span="10" :xs="24">
             <transition name="el-zoom-in-top">
                <el-card 
                    class="result-card hover-effect" 
                    v-if="result"
                    :style="{ borderTop: `5px solid ${getCategoryColorValue(result.category)}` }"
                >
                  <template #header>
                    <div class="card-header">
                      <span><el-icon class="header-icon"><Trophy /></el-icon> 识别结果</span>
                    </div>
                  </template>
                  <div class="result-content">
                    <div class="result-header">
                        <div class="icon-wrapper" :style="{ backgroundColor: getCategoryColorValue(result.category) }">
                             <el-icon color="#fff" :size="32">
                                <component :is="getCategoryIcon(result.category)" />
                             </el-icon>
                        </div>
                        <div class="result-title">
                            <h3>{{ result.result_name }}</h3>
                            <el-tag :type="getCategoryType(result.category)" effect="dark" size="large" round>
                                {{ result.category }}
                            </el-tag>
                        </div>
                    </div>
                    
                    <el-divider />

                    <div class="result-item">
                      <span class="label">投放建议：</span>
                      <p class="advice" :style="{ borderLeftColor: getCategoryColorValue(result.category) }">
                        {{ result.advice }}
                      </p>
                    </div>
                  </div>
                </el-card>
             </transition>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
    <!-- 修改密码弹窗 -->
    <el-dialog
        v-model="passwordDialogVisible"
        title="修改密码"
        width="400px"
    >
        <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="80px">
            <el-form-item label="旧密码" prop="old_password">
                <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
                <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
                <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="passwordDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="submitPasswordForm(passwordFormRef)">确认修改</el-button>
            </span>
        </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, UploadFile, UploadFiles, FormInstance, ElMessageBox } from 'element-plus'
import { UploadFilled, Search, Trophy, Edit, Food, Refresh, CircleClose, Delete, Notebook } from '@element-plus/icons-vue'
import axios from '../utils/request'
import { updatePassword } from '../api/user'
import { searchDictionary, DictionaryItem } from '../api/dictionary'

const router = useRouter()
const isAdmin = ref(localStorage.getItem('is_admin') === 'true')
const textInput = ref('')
const fileList = ref<UploadFiles>([])
const imageFile = ref<File | null>(null)
const loading = ref(false)
const result = ref<any>(null)

// 本地词典搜索相关
const searchKeyword = ref('')
const searchResultList = ref<DictionaryItem[]>([])
const searchLoading = ref(false)
const hasSearched = ref(false) // 是否执行过搜索

// 处理文件选择
const handleFileChange = (uploadFile: UploadFile) => {
    imageFile.value = uploadFile.raw as File
    textInput.value = '' // 清空文本，互斥
}

const handleRemove = () => {
    imageFile.value = null
    fileList.value = []
}

// 获取分类对应颜色值 (用于动态样式)
const getCategoryColorValue = (category: string) => {
    switch (category) {
        case '厨余垃圾': return 'var(--category-kitchen)' // 棕色
        case '可回收物': return 'var(--category-recyclable)' // 蓝色
        case '有害垃圾': return 'var(--category-harmful)' // 红色
        case '其他垃圾': return 'var(--category-other)' // 灰色
        default: return '#E6A23C'
    }
}

// 获取分类对应 Element Plus Type
const getCategoryType = (category: string) => {
     switch (category) {
        case '厨余垃圾': return 'success'
        case '可回收物': return 'primary'
        case '有害垃圾': return 'danger'
        case '其他垃圾': return 'info'
        default: return 'warning'
    }
}

// 获取分类对应图标组件名
const getCategoryIcon = (category: string) => {
    switch (category) {
        case '厨余垃圾': return 'Food'
        case '可回收物': return 'Refresh'
        case '有害垃圾': return 'CircleClose'
        case '其他垃圾': return 'Delete'
        default: return 'Search'
    }
}

// 执行本地搜索
const handleSearch = async () => {
    if (!searchKeyword.value) return
    searchLoading.value = true
    hasSearched.value = true // 标记已搜索
    try {
        const res: any = await searchDictionary(searchKeyword.value)
        searchResultList.value = res
    } catch (error) {
        // error handled
    } finally {
        searchLoading.value = false
    }
}

// 开始识别
const startRecognition = async () => {
    if (!textInput.value && !imageFile.value) {
        ElMessage.warning('请输入文本或上传图片')
        return
    }

    loading.value = true
    result.value = null

    try {
        const formData = new FormData()
        if (imageFile.value) {
            formData.append('image', imageFile.value)
        } else {
            formData.append('text', textInput.value)
        }

        const res: any = await axios.post('/recognition/classify', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })

        if (res.result) {
            result.value = res.result
            ElMessage.success('识别成功')
        }
    } catch (error) {
        // Error handled in interceptor
    } finally {
        loading.value = false
    }
}

// -------------------------------------------------------------------
// 修改密码相关
// -------------------------------------------------------------------
const passwordDialogVisible = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordForm = reactive({
    old_password: '',
    new_password: '',
    confirm_password: ''
})

const validatePass2 = (rule: any, value: any, callback: any) => {
    if (value === '') {
        callback(new Error('请再次输入密码'))
    } else if (value !== passwordForm.new_password) {
        callback(new Error('两次输入密码不一致!'))
    } else {
        callback()
    }
}

const passwordRules = {
    old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
    new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }],
    confirm_password: [{ required: true, validator: validatePass2, trigger: 'blur' }]
}

const openChangePasswordDialog = () => {
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    passwordDialogVisible.value = true
}

const submitPasswordForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate(async (valid) => {
        if (valid) {
            try {
                await updatePassword({
                    old_password: passwordForm.old_password,
                    new_password: passwordForm.new_password
                })
                ElMessage.success('密码修改成功，请重新登录')
                passwordDialogVisible.value = false
                logout() // 强制登出
            } catch (error) {
                // error handled
            }
        }
    })
}

// 退出登录
const logout = () => {
    localStorage.removeItem('token')
    router.push('/login')
}
</script>

<style scoped>
.home-container {
  height: 100vh;
  /* 背景已在全局 body 中设置，此处只需透明 */
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
.input-card, .result-card {
  height: 100%; /* 确保卡片高度填满 */
  /* 磨砂玻璃带来的圆角和背景 */
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease; /* 微动效：平滑过渡 */
}

/* 悬停微动效 */
.hover-effect:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.card-header {
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: bold;
    color: #303133;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-link {
    font-size: 16px;
    color: #606266;
    font-weight: normal;
}
.nav-link:hover {
    color: var(--eco-green);
}

.user-profile {
}
.header-icon {
    margin-right: 8px;
    margin-top: 2px;
}

.submit-btn {
  width: 100%;
  margin-top: 20px;
  background-color: var(--eco-green);
  border-color: var(--eco-green);
  font-weight: bold;
  transition: all 0.3s ease;
}
/* 按钮点击涟漪/缩放效果 */
.submit-btn:hover {
    transform: scale(1.05); 
    box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
}
.submit-btn:active {
    transform: scale(0.95);
}

.result-content {
  padding: 10px;
}
.result-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}
.icon-wrapper {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 20px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.result-title h3 {
    margin: 0 0 10px 0;
    font-size: 24px;
    color: #303133;
}

.label {
  font-weight: bold;
  margin-right: 10px;
  color: #303133;
}
.advice {
  margin-top: 10px;
  color: #606266;
  line-height: 1.6;
  background-color: rgba(240, 249, 235, 0.8); /* 半透明背景 */
  padding: 15px;
  border-radius: 8px;
  border-left: 5px solid; /* 颜色由内联样式动态控制 */
}

/* 针对 Element Plus 组件的样式微调 */
:deep(.el-card__header) {
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    padding: 15px 20px;
}
:deep(.el-upload-dragger) {
    background-color: rgba(255, 255, 255, 0.5);
    border-radius: 8px;
}
:deep(.el-upload-dragger:hover) {
    border-color: var(--eco-green);
}
</style>
