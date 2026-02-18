<template>
  <div class="admin-container">
    <el-container>
      <el-aside width="200px" class="aside">
        <div class="logo">管理后台</div>
        <el-menu
          default-active="overview"
          class="el-menu-vertical-demo"
          @select="handleSelect"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF">
          <el-menu-item index="overview">
            <el-icon><DataLine /></el-icon>
            <span>总览统计</span>
          </el-menu-item>
          <el-menu-item index="users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="records">
            <el-icon><List /></el-icon>
            <span>识别记录</span>
          </el-menu-item>
          <el-menu-item index="feedbacks">
            <el-icon><ChatLineSquare /></el-icon>
            <span>用户反馈</span>
          </el-menu-item>
          <el-menu-item index="dictionary">
            <el-icon><Notebook /></el-icon>
            <span>分类词库</span>
          </el-menu-item>
          <el-menu-item index="knowledge">
            <el-icon><Reading /></el-icon>
            <span>知识库管理</span>
          </el-menu-item>
          <el-menu-item index="system-logs">
            <el-icon><Monitor /></el-icon>
            <span>系统日志</span>
          </el-menu-item>
          <el-menu-item index="home" @click="goHome">
            <el-icon><House /></el-icon>
            <span>返回前台</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <div class="breadcrumb">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item>首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentTabName }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="user-info">
             管理员
          </div>
        </el-header>
        <el-main>
            <!-- 概览 -->
            <div v-if="currentTab === 'overview'">
                <el-row :gutter="20">
                    <el-col :span="12">
                        <el-card>
                            <template #header><span>平台总数据</span></template>
                            <div class="stats-item">总用户数: {{ stats.total_users }}</div>
                            <div class="stats-item">总识别记录: {{ stats.total_records }}</div>
                        </el-card>
                    </el-col>
                    <el-col :span="12">
                        <el-card>
                            <div ref="chartRef" style="width: 100%; height: 300px;"></div>
                        </el-card>
                    </el-col>
                </el-row>
            </div>

            <!-- 用户列表 -->
            <div v-if="currentTab === 'users'">
                 <el-table :data="userList" border style="width: 100%">
                    <el-table-column prop="id" label="ID" width="80" />
                    <el-table-column prop="username" label="用户名" />
                    <el-table-column prop="email" label="邮箱" />
                    <el-table-column prop="role" label="角色" />
                    <el-table-column prop="is_admin" label="管理员" width="100">
                        <template #default="scope">
                            <el-tag :type="scope.row.is_admin ? 'success' : 'info'">{{ scope.row.is_admin ? '是' : '否' }}</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="is_active" label="状态" width="100">
                        <template #default="scope">
                            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">{{ scope.row.is_active ? '正常' : '封禁' }}</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="created_at" label="注册时间" />
                    <el-table-column label="操作" width="200">
                        <template #default="scope">
                            <el-button 
                                type="warning" 
                                size="small" 
                                @click="handleResetPassword(scope.row.id)"
                            >重置密码</el-button>
                            <el-button 
                                :type="scope.row.is_active ? 'danger' : 'success'" 
                                size="small" 
                                @click="handleUpdateStatus(scope.row)"
                                :disabled="scope.row.id === currentAdminId"
                            >
                                {{ scope.row.is_active ? '封禁' : '解禁' }}
                            </el-button>
                        </template>
                    </el-table-column>
                 </el-table>
            </div>

            <!-- 记录列表 -->
            <div v-if="currentTab === 'records'">
                <el-table :data="recordList" border style="width: 100%">
                    <el-table-column prop="id" label="ID" width="80" />
                    <el-table-column prop="username" label="用户" width="120" />
                    <el-table-column prop="input_content" label="内容" width="120">
                        <template #default="scope">
                            <span v-if="scope.row.input_type === 'text'">{{ scope.row.input_content }}</span>
                            <el-image 
                                v-else
                                style="width: 50px; height: 50px"
                                :src="scope.row.input_content"
                                :preview-src-list="[scope.row.input_content]"
                                preview-teleported
                            />
                        </template>
                    </el-table-column>
                    <el-table-column prop="recognized_item" label="物品" />
                    <el-table-column prop="ai_analysis.category" label="分类" width="100">
                        <template #default="scope">
                             <el-tag>{{ scope.row.ai_analysis?.category || '未知' }}</el-tag>
                        </template>
                    </el-table-column>
                     <el-table-column prop="created_at" label="时间" />
                     <el-table-column label="操作" width="100">
                        <template #default="scope">
                            <el-button type="danger" size="small" @click="deleteRecord(scope.row.id)">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <!-- 反馈列表 -->
            <div v-if="currentTab === 'feedbacks'">
                <el-table :data="feedbackList" border style="width: 100%">
                    <el-table-column prop="id" label="ID" width="80" />
                    <el-table-column prop="username" label="提交者" width="120" />
                    <el-table-column prop="content" label="反馈内容" show-overflow-tooltip />
                    <el-table-column prop="created_at" label="提交时间" width="180">
                        <template #default="scope">
                            {{ new Date(scope.row.created_at).toLocaleString() }}
                        </template>
                    </el-table-column>
                    <el-table-column prop="status" label="状态" width="100">
                        <template #default="scope">
                            <el-tag :type="scope.row.status === 'resolved' ? 'success' : 'warning'">
                                {{ scope.row.status === 'resolved' ? '已解决' : '待处理' }}
                            </el-tag>
                        </template>
                    </el-table-column>
                     <el-table-column label="操作" width="120">
                        <template #default="scope">
                            <el-button 
                                v-if="scope.row.status === 'pending'"
                                type="primary" 
                                size="small" 
                                @click="resolveFeedback(scope.row.id)"
                            >
                                标记解决
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <!-- 分类词库管理 -->
            <div v-if="currentTab === 'dictionary'">
                <div style="margin-bottom: 20px;">
                    <el-button type="primary" icon="Plus" @click="openAddDialog">新增词条</el-button>
                </div>
                
                <el-table :data="dictionaryList" border style="width: 100%">
                    <el-table-column prop="item_name" label="物品名称" width="180" />
                    <el-table-column prop="category" label="分类" width="120">
                        <template #default="scope">
                            <el-tag :type="scope.row.category === '有害垃圾' ? 'danger' : scope.row.category === '可回收物' ? 'primary' : scope.row.category === '厨余垃圾' ? 'success' : 'info'">
                                {{ scope.row.category }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="description" label="补充说明" show-overflow-tooltip />
                    <el-table-column label="操作" width="180">
                        <template #default="scope">
                            <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
                            <el-button size="small" type="danger" @click="handleDeleteDictionaryItem(scope.row.id)">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <!-- 知识库管理 -->
            <div v-if="currentTab === 'knowledge'">
                <div style="margin-bottom: 20px;">
                    <el-button type="primary" icon="Plus" @click="openArticleAddDialog">发布新文章</el-button>
                </div>

                <el-table :data="articleList" border style="width: 100%">
                    <el-table-column prop="id" label="ID" width="80" />
                    <el-table-column prop="title" label="标题" show-overflow-tooltip />
                    <el-table-column prop="author" label="发布者" width="120" />
                    <el-table-column prop="created_at" label="发布时间" width="180">
                        <template #default="scope">
                            {{ new Date(scope.row.created_at).toLocaleString() }}
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="180">
                        <template #default="scope">
                            <el-button size="small" @click="openArticleEditDialog(scope.row)">编辑</el-button>
                            <el-button size="small" type="danger" @click="handleDeleteArticle(scope.row.id)">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <!-- 系统日志 -->
            <div v-if="currentTab === 'system-logs'">
                <div style="margin-bottom: 20px;">
                    <el-button type="primary" :loading="logLoading" @click="loadLogs">刷新日志</el-button>
                </div>
                <div class="log-terminal" ref="logTerminalRef">
                    {{ logContent }}
                </div>
            </div>

            <!-- 词典编辑/新增弹窗 -->
            <el-dialog
                v-model="dictionaryDialogVisible"
                :title="isEditMode ? '编辑词条' : '新增词条'"
                width="500px"
            >
                <el-form :model="dictionaryForm" :rules="dictionaryRules" ref="dictionaryFormRef" label-width="80px">
                    <el-form-item label="物品名称" prop="item_name">
                        <el-input v-model="dictionaryForm.item_name" placeholder="请输入物品名称" />
                    </el-form-item>
                    <el-form-item label="垃圾分类" prop="category">
                         <el-select v-model="dictionaryForm.category" placeholder="请选择分类" style="width: 100%">
                            <el-option label="可回收物" value="可回收物" />
                            <el-option label="干垃圾" value="干垃圾" />
                            <el-option label="湿垃圾" value="湿垃圾" />
                            <el-option label="有害垃圾" value="有害垃圾" />
                            <el-option label="厨余垃圾" value="厨余垃圾" />
                            <el-option label="其他垃圾" value="其他垃圾" />
                        </el-select>
                    </el-form-item>
                    <el-form-item label="补充说明" prop="description">
                        <el-input type="textarea" v-model="dictionaryForm.description" placeholder="请输入投放建议或说明" />
                    </el-form-item>
                </el-form>
                <template #footer>
                    <span class="dialog-footer">
                        <el-button @click="dictionaryDialogVisible = false">取消</el-button>
                        <el-button type="primary" @click="submitDictionaryForm(dictionaryFormRef)">确定</el-button>
                    </span>
                </template>
            </el-dialog>

            <!-- 文章编辑/新增弹窗 -->
            <el-dialog
                v-model="articleDialogVisible"
                :title="isArticleEditMode ? '编辑文章' : '发布新文章'"
                width="700px"
            >
                <el-form :model="articleForm" :rules="articleRules" ref="articleFormRef" label-width="80px">
                    <el-form-item label="文章标题" prop="title">
                        <el-input v-model="articleForm.title" placeholder="请输入文章标题" />
                    </el-form-item>
                    <el-form-item label="封面图片" prop="cover_image">
                        <el-input v-model="articleForm.cover_image" placeholder="请输入封面图片 URL" />
                    </el-form-item>
                    <el-form-item label="文章内容" prop="content">
                        <el-input 
                            v-model="articleForm.content" 
                            type="textarea" 
                            :rows="10" 
                            placeholder="支持 Markdown 或 HTML 格式" 
                        />
                    </el-form-item>
                </el-form>
                <template #footer>
                    <span class="dialog-footer">
                        <el-button @click="articleDialogVisible = false">取消</el-button>
                        <el-button type="primary" @click="submitArticleForm(articleFormRef)">发布/更新</el-button>
                    </span>
                </template>
            </el-dialog>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed, nextTick, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { DataLine, User, List, House, ChatLineSquare, Notebook, Plus, Reading, Monitor } from '@element-plus/icons-vue'
import axios from '../utils/request'
import * as echarts from 'echarts'
import { getSystemStats, getSystemLogs, resetUserPassword, updateUserStatus } from '../api/admin'
import { searchDictionary, getDictionaryItems, createDictionaryItem, updateDictionaryItem, deleteDictionaryItem, DictionaryItem } from '../api/dictionary'
import { getArticles, createArticle, updateArticle, deleteArticle, ArticleItem } from '../api/article'

const router = useRouter()
const currentTab = ref('overview')
const stats = ref<any>({})
const userList = ref([])
const currentAdminId = ref(0) // 存储当前管理员ID
const recordList = ref([])
const feedbackList = ref([])
const dictionaryList = ref<DictionaryItem[]>([]) // 词典列表数据
const articleList = ref<ArticleItem[]>([]) // 文章列表
const chartRef = ref<HTMLElement | null>(null)
const dictionaryLoading = ref(false)
const articleLoading = ref(false)

// 词典表单相关
const dictionaryDialogVisible = ref(false)
const isEditMode = ref(false)
const dictionaryFormRef = ref<FormInstance>()
const dictionaryForm = reactive<DictionaryItem>({
    item_name: '',
    category: '',
    description: ''
})

const dictionaryRules = {
    item_name: [{ required: true, message: '请输入物品名称', trigger: 'blur' }],
    category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

// 知识库表单相关
const articleDialogVisible = ref(false)
const isArticleEditMode = ref(false)
const articleFormRef = ref<FormInstance>()
const articleForm = reactive<ArticleItem>({
    title: '',
    content: '',
    cover_image: '',
    author: '管理员',
    is_published: true
})

const articleRules = {
    title: [{ required: true, message: '请输入文章标题', trigger: 'blur' }],
    content: [{ required: true, message: '请输入文章内容', trigger: 'blur' }]
}

const currentTabName = computed(() => {
    switch (currentTab.value) {
        case 'overview': return '总览统计'
        case 'users': return '用户管理'
        case 'records': return '识别记录'
        case 'feedbacks': return '用户反馈'
        case 'dictionary': return '分类词库'
        case 'knowledge': return '知识库管理'
        case 'system-logs': return '系统日志'
        default: return ''
    }
})

const handleSelect = (key: string) => {
    if (key === 'home') return
    currentTab.value = key
    fetchData()
}

const goHome = () => {
    router.push('/')
}

const fetchData = async () => {
    try {
        if (currentTab.value === 'overview') {
            const res: any = await getSystemStats()
            stats.value = res
            initChart(res.category_distribution)
        } else if (currentTab.value === 'users') {
            const res: any = await axios.get('/admin/users')
            userList.value = res
            // 获取当前用户信息以避免禁用自己 (简单通过 username 匹配，或后端返回 id)
            // 这里假设 localStorage 中存了 username，遍历 userList 找到自己的 id
            const currentUsername = localStorage.getItem('username')
            const me = res.find((u: any) => u.username === currentUsername)
            if (me) {
                currentAdminId.value = me.id
            }
        } else if (currentTab.value === 'records') {
            const res: any = await axios.get('/admin/records')
            recordList.value = res
        } else if (currentTab.value === 'feedbacks') {
            const res: any = await axios.get('/feedbacks/admin/all')
            feedbackList.value = res
        } else if (currentTab.value === 'dictionary') {
            loadDictionaries()
        } else if (currentTab.value === 'knowledge') {
            loadArticles()
        } else if (currentTab.value === 'system-logs') {
            loadLogs()
        }
    } catch (error) {
        // error handled
    }
}

// 加载词典数据
const loadDictionaries = async () => {
    dictionaryLoading.value = true
    try {
        const res: any = await getDictionaryItems()
        dictionaryList.value = res
    } finally {
        dictionaryLoading.value = false
    }
}

// 加载文章数据
const loadArticles = async () => {
    articleLoading.value = true
    try {
        const res: any = await getArticles({ limit: 100 })
        articleList.value = res
    } finally {
        articleLoading.value = false
    }
}

// 系统日志相关
const logContent = ref('')
const logTerminalRef = ref<HTMLElement | null>(null)
const logLoading = ref(false)

const loadLogs = async () => {
    logLoading.value = true
    try {
        const res: any = await getSystemLogs()
        logContent.value = res.logs || '暂无日志'
        // 滚动到底部
        nextTick(() => {
            if (logTerminalRef.value) {
                logTerminalRef.value.scrollTop = logTerminalRef.value.scrollHeight
            }
        })
    } catch(err) {
        logContent.value = '获取日志失败'
    } finally {
        logLoading.value = false
    }
}



// 初始化图表
const initChart = async (distribution: any) => {
    if (!chartRef.value) return
    
    // Dispose old instance to avoid memory leak or "instance already initialized" warning
    let myChart = echarts.getInstanceByDom(chartRef.value)
    if (myChart) {
        myChart.dispose()
    }
    myChart = echarts.init(chartRef.value)

    const data = Object.keys(distribution || {}).map(key => ({
        value: distribution[key],
        name: key
    }))

    const option = {
        title: { text: '全站分类占比', left: 'center' },
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left' },
        series: [
            {
                name: '分类',
                type: 'pie',
                radius: '50%',
                data: data
            }
        ]
    }
    myChart.setOption(option)
}

const deleteRecord = (id: number) => {
    ElMessageBox.confirm('确定删除该记录?', '警告', { type: 'warning' })
    .then(async () => {
        await axios.delete(`/admin/records/${id}`)
        ElMessage.success('删除成功')
        fetchData()
    })
    .catch(() => {})
}

// 解决反馈
const resolveFeedback = (id: number) => {
     ElMessageBox.confirm('确定将该反馈标记为已解决?', '提示', { type: 'info' })
    .then(async () => {
        await axios.put(`/feedbacks/admin/${id}/resolve`)
        ElMessage.success('操作成功')
        fetchData()
    })
    .catch(() => {})
}

// 重置用户密码
const handleResetPassword = (id: number) => {
    ElMessageBox.confirm('确定要将该用户的密码重置为 123456 吗？', '警告', {
        type: 'warning'
    }).then(async () => {
        await resetUserPassword(id)
        ElMessage.success('密码重置成功')
    }).catch(() => {})
}

// 修改用户状态
const handleUpdateStatus = (row: any) => {
    const action = row.is_active ? '封禁' : '解禁'
    ElMessageBox.confirm(`确定要${action}该用户吗？`, '警告', {
        type: row.is_active ? 'danger' : 'success'
    }).then(async () => {
        await updateUserStatus(row.id, !row.is_active)
        ElMessage.success(`用户已${action}`)
        fetchData()
    }).catch(() => {})
}

// -------------------------------------------------------------------
// 词典管理相关方法
// -------------------------------------------------------------------

// 辅助函数：获取分类 Type
const getCategoryType = (category: string) => {
     switch (category) {
        case '厨余垃圾': return 'success'
        case '可回收物': return 'primary'
        case '有害垃圾': return 'danger'
        case '其他垃圾': return 'info'
        default: return 'warning'
    }
}

// 打开新增弹窗
const openAddDialog = () => {
    isEditMode.value = false
    dictionaryForm.id = undefined
    dictionaryForm.item_name = ''
    dictionaryForm.category = ''
    dictionaryForm.description = ''
    dictionaryDialogVisible.value = true
}

// 打开编辑弹窗
const openEditDialog = (row: DictionaryItem) => {
    isEditMode.value = true
    dictionaryForm.id = row.id
    dictionaryForm.item_name = row.item_name
    dictionaryForm.category = row.category
    dictionaryForm.description = row.description
    dictionaryDialogVisible.value = true
}

// 提交词典表单
const submitDictionaryForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate(async (valid, fields) => {
        if (valid) {
            try {
                if (isEditMode.value && dictionaryForm.id) {
                    await updateDictionaryItem(dictionaryForm.id, dictionaryForm)
                    ElMessage.success('修改成功')
                } else {
                    await createDictionaryItem(dictionaryForm)
                    ElMessage.success('添加成功')
                }
                dictionaryDialogVisible.value = false
                loadDictionaries() // 刷新列表
            } catch (error) {
                // error handled in request.ts
            }
        }
    })
}

// 删除词条
const handleDeleteDictionaryItem = (id: number) => {
    ElMessageBox.confirm('确定删除该词条?', '警告', { type: 'warning' })
    .then(async () => {
        await deleteDictionaryItem(id)
        ElMessage.success('删除成功')
        loadDictionaries()
    })
    .catch(() => {})
}

// -------------------------------------------------------------------
// 知识库管理相关方法
// -------------------------------------------------------------------

const openArticleAddDialog = () => {
    isArticleEditMode.value = false
    articleForm.id = undefined
    articleForm.title = ''
    articleForm.content = ''
    articleForm.cover_image = ''
    articleForm.author = '管理员'
    articleForm.is_published = true
    articleDialogVisible.value = true
}

const openArticleEditDialog = (row: ArticleItem) => {
    isArticleEditMode.value = true
    Object.assign(articleForm, row)
    articleDialogVisible.value = true
}

const submitArticleForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    
    await formEl.validate(async (valid) => {
        if (valid) {
            try {
                if (isArticleEditMode.value && articleForm.id) {
                    await updateArticle(articleForm.id, articleForm)
                    ElMessage.success('更新成功')
                } else {
                    await createArticle(articleForm)
                    ElMessage.success('发布成功')
                }
                articleDialogVisible.value = false
                loadArticles()
            } catch (error) {
                console.error(error)
            }
        }
    })
}

const handleDeleteArticle = (id: number) => {
     ElMessageBox.confirm('确定要删除该文章吗？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
    }).then(async () => {
        await deleteArticle(id)
        ElMessage.success('删除成功')
        loadArticles()
    }).catch(() => {})
}

onMounted(() => {
    fetchData()
})
</script>

<style scoped>
.admin-container {
    height: 100vh;
    background-color: transparent;
}
.toolbar {
    margin-bottom: 20px;
}
.aside {
    /* 深色磨砂玻璃 */
    background: rgba(48, 65, 86, 0.85);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    color: #fff;
    min-height: 100vh;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}
.logo {
    height: 60px;
    line-height: 60px;
    text-align: center;
    font-size: 18px;
    font-weight: bold;
    color: #fff;
    background-color: rgba(255, 255, 255, 0.1); /* 半透明背景 */
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
/* 菜单背景透明化以适应 sidebar */
:deep(.el-menu) {
    background-color: transparent !important;
    border-right: none;
}
:deep(.el-menu-item) {
    background-color: transparent !important;
}
:deep(.el-menu-item:hover) {
    background-color: rgba(255, 255, 255, 0.1) !important;
}
:deep(.el-menu-item.is-active) {
    background-color: rgba(64, 158, 255, 0.2) !important;
}

.header {
    /* 浅色磨砂玻璃 */
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

/* 卡片磨砂效果 */
:deep(.el-card) {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border-radius: 16px;
    color: #303133;
}
:deep(.el-card__header) {
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

/* 表格透明化 */
:deep(.el-table), :deep(.el-table__expanded-cell) {
    background-color: transparent;
}
:deep(.el-table tr) {
    background-color: transparent;
}
:deep(.el-table th.el-table__cell) {
    background-color: rgba(255, 255, 255, 0.5);
}

.stats-item {
    font-size: 16px;
    margin-bottom: 10px;
}

/* 日志终端样式 */
.log-terminal {
    background-color: #1e1e1e;
    color: #00ff00;
    padding: 15px;
    border-radius: 8px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.5;
    height: 600px;
    overflow-y: auto;
    white-space: pre-wrap; /* 保留换行和空格 */
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
}
.log-terminal::-webkit-scrollbar {
    width: 8px;
    background-color: #2d2d2d;
}
.log-terminal::-webkit-scrollbar-thumb {
    background-color: #555;
    border-radius: 4px;
}
</style>
