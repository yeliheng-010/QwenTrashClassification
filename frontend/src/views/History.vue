<template>
  <div class="history-container">
    <el-container>
      <el-header class="header">
        <div class="logo" @click="goHome">智能垃圾分类系统</div>
        <div class="user-info">
          <el-button @click="goHome">返回首页</el-button>
          <el-button type="danger" link @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="main-content">
        <el-tabs v-model="activeTab" class="custom-tabs" type="border-card">
            <el-tab-pane label="历史记录" name="history">
                <!-- 统计图表区域 -->
                <el-row :gutter="20" class="stats-row">
                    <el-col :span="6" :xs="24">
                        <el-card class="stats-card">
                            <template #header>
                                <div class="card-header">
                                    <span>总识别次数</span>
                                </div>
                            </template>
                            <div class="stats-number">{{ historyList.length }}</div>
                        </el-card>
                    </el-col>
                    <el-col :span="18" :xs="24">
                        <el-card class="chart-card">
                            <div ref="chartRef" style="width: 100%; height: 300px;"></div>
                        </el-card>
                    </el-col>
                </el-row>

                <!-- 历史记录列表 -->
                <el-card class="list-card">
                    <template #header>
                        <div class="card-header">
                            <span>历史记录</span>
                        </div>
                    </template>
                    <el-table :data="historyList" style="width: 100%" v-loading="loading">
                        <el-table-column prop="input_content" label="内容/图片" width="120">
                            <template #default="scope">
                                <el-image 
                                    v-if="scope.row.input_type === 'image'"
                                    style="width: 80px; height: 80px"
                                    :src="scope.row.input_content"
                                    :preview-src-list="[scope.row.input_content]"
                                    fit="cover"
                                    preview-teleported
                                />
                                <span v-else>{{ scope.row.input_content.length > 10 ? scope.row.input_content.substring(0, 10) + '...' : scope.row.input_content }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="recognized_item" label="物品名称" width="150" />
                        <el-table-column prop="ai_analysis.category" label="分类" width="120">
                            <template #default="scope">
                                <el-tag :type="getCategoryColor(scope.row.ai_analysis?.category)">
                                    {{ scope.row.ai_analysis?.category || '未知' }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column prop="ai_analysis.advice" label="处理建议" />
                        <el-table-column prop="created_at" label="时间" width="180">
                        <template #default="scope">
                            {{ formatDate(scope.row.created_at) }}
                        </template>
                        </el-table-column>
                        <el-table-column label="操作" width="100">
                            <template #default="scope">
                                <el-button type="danger" size="small" @click="deleteItem(scope.row.id)">删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </el-tab-pane>
            
            <el-tab-pane label="基本信息" name="profile">
                <el-card class="profile-card">
                    <template #header>
                        <div class="card-header">
                            <span>修改个人信息</span>
                        </div>
                    </template>
                    <el-form :model="userInfoForm" label-width="100px" style="max-width: 500px">
                        <el-form-item label="用户名">
                            <el-input v-model="userInfoForm.username" disabled placeholder="用户名不可修改" />
                        </el-form-item>
                        <el-form-item label="邮箱">
                            <el-input v-model="userInfoForm.email" placeholder="请输入邮箱地址" />
                        </el-form-item>
                        <el-form-item label="角色">
                            <el-tag>{{ userInfoForm.role === 'admin' ? '管理员' : '普通用户' }}</el-tag>
                        </el-form-item>
                         <el-form-item>
                            <el-button type="primary" @click="handleUpdateInfo" :loading="updateLoading">保存修改</el-button>
                        </el-form-item>
                    </el-form>
                </el-card>
            </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, nextTick, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '../utils/request'
import * as echarts from 'echarts'
import { getUserInfo, updateUserInfo } from '../api/user'

const router = useRouter()
const activeTab = ref('history')
const historyList = ref<any[]>([])
const loading = ref(false)
const chartRef = ref<HTMLElement | null>(null)

// 用户信息相关
const updateLoading = ref(false)
const userInfoForm = reactive({
    username: '',
    email: '',
    role: ''
})

// 获取当前用户信息
const fetchUserInfo = async () => {
    try {
        const res: any = await getUserInfo()
        userInfoForm.username = res.username
        userInfoForm.email = res.email
        userInfoForm.role = res.role
    } catch (error) {
        console.error(error)
    }
}

// 更新用户信息
const handleUpdateInfo = async () => {
    updateLoading.value = true
    try {
        const res: any = await updateUserInfo({
            email: userInfoForm.email
        })
        ElMessage.success('个人信息更新成功')
        // 同步更新本地存储
        // 满足用户要求：更新 localStorage 中的用户信息，确保其他组件如有使用能即时获取
        const userStr = localStorage.getItem('user')
        let userObj: any = {}
        if (userStr) {
             try {
                userObj = JSON.parse(userStr)
             } catch (e) {
                userObj = {}
             }
        }
        // 更新或设置 email
        userObj.email = res.email
        // 如果 localStorage 中没有 username (因为 Login.vue 分开存了), 咱们也补上，保持 user 对象完整性
        if (!userObj.username) userObj.username = userInfoForm.username
        
        localStorage.setItem('user', JSON.stringify(userObj))
        // 同时也更新单独的 email key (如果未来有组件用)
        localStorage.setItem('email', res.email)
        
        // 刷新数据
        fetchUserInfo()
    } catch (error) {
        // error handled
    } finally {
        updateLoading.value = false
    }
}

// 获取历史记录
const fetchHistory = async () => {
    loading.value = true
    try {
        const res: any = await axios.get('/recognition/history')
        historyList.value = res || []
        // 仅在 tab 为 history 时初始化图表
        if (activeTab.value === 'history') {
            initChart()
        }
    } catch (error) {
        // error handled
    } finally {
        loading.value = false
    }
}

// 初始化图表
const initChart = async () => {
    await nextTick()
    if (!chartRef.value) return

    const myChart = echarts.init(chartRef.value)
    
    // 统计数据
    const categoryCounts: Record<string, number> = {}
    historyList.value.forEach(item => {
        const category = item.ai_analysis?.category || '未知'
        categoryCounts[category] = (categoryCounts[category] || 0) + 1
    })
    
    const data = Object.keys(categoryCounts).map(key => ({
        value: categoryCounts[key],
        name: key
    }))

    const option = {
        title: {
            text: '垃圾分类统计',
            left: 'center'
        },
        tooltip: {
            trigger: 'item'
        },
        legend: {
            orient: 'vertical',
            left: 'left'
        },
        series: [
            {
                name: '分类',
                type: 'pie',
                radius: '50%',
                data: data,
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    }

    myChart.setOption(option)
    
    // 响应式大小
    window.addEventListener('resize', () => {
        myChart.resize()
    })
}

// 删除记录
const deleteItem = (id: number) => {
    ElMessageBox.confirm(
        '确定要删除这条记录吗？',
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
    )
    .then(async () => {
        try {
            await axios.delete(`/recognition/history/${id}`)
            ElMessage.success('删除成功')
            // Remove from list locally
            historyList.value = historyList.value.filter(item => item.id !== id)
            initChart() // Refresh chart
        } catch (error) {
            // handled
        }
    })
    .catch(() => {})
}

// 辅助函数
const getCategoryColor = (category: string) => {
    switch (category) {
        case '厨余垃圾': return 'success'
        case '可回收物': return 'primary'
        case '有害垃圾': return 'danger'
        case '其他垃圾': return 'info'
        default: return 'warning'
    }
}

const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString()
}

const goHome = () => {
    router.push('/')
}

const logout = () => {
    localStorage.removeItem('token')
    router.push('/login')
}

onMounted(() => {
    fetchHistory()
    fetchUserInfo()
})
</script>

<style scoped>
.history-container {
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
  max-width: 1200px;
  margin: 0 auto;
}
.stats-row {
    margin-bottom: 20px;
}
.stats-card, .chart-card, .list-card {
    /* 磨砂玻璃效果 */
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border-radius: 16px;
}
.stats-card {
    height: 340px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}
.stats-number {
    font-size: 60px;
    font-weight: bold;
    color: var(--eco-green); /* 使用主题色 */
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.chart-card {
    height: 340px;
}
.list-card {
    min-height: 400px;
}

/* 透明化表格背景以适应磨砂玻璃 */
:deep(.el-table), :deep(.el-table__expanded-cell) {
    background-color: transparent;
}
:deep(.el-table tr) {
    background-color: transparent;
}
:deep(.el-table th.el-table__cell) {
    background-color: rgba(255, 255, 255, 0.5);
}
:deep(.el-card__header) {
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
</style>
