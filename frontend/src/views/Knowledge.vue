<template>
  <div class="knowledge-container">
    <el-container>
      <el-header class="header">
        <div class="logo" @click="router.push('/')">环保资讯</div>
        <div class="user-info">
          <el-button v-if="isAdmin" type="primary" icon="Plus" @click="openPublishDialog" style="margin-right: 10px;">发布资讯</el-button>
          <el-button @click="router.push('/')">返回首页</el-button>
        </div>
      </el-header>
      <el-main class="main-content">
        <div class="page-title">
             <h2><el-icon><Reading /></el-icon> 最新环保资讯</h2>
             <p>了解最新的环保政策、科普知识与行业动态</p>
        </div>
        
        <el-row :gutter="20" v-loading="loading">
            <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="article in articleList" :key="article.id" style="margin-bottom: 20px;">
                <el-card class="article-card hover-effect" :body-style="{ padding: '0px' }" @click="goToDetail(article.id!)">
                    <div class="image-wrapper" v-if="article.cover_image">
                        <img :src="article.cover_image" class="image" />
                    </div>
                    <div class="image-placeholder" v-else>
                        <el-icon :size="50" color="#909399"><Picture /></el-icon>
                    </div>
                    <div style="padding: 14px">
                        <h3 class="article-title">{{ article.title }}</h3>
                        <div class="bottom">
                            <span class="time">{{ new Date(article.created_at!).toLocaleDateString() }}</span>
                            <span class="author">{{ article.author }}</span>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col v-if="articleList.length === 0 && !loading" :span="24">
                <el-empty description="暂无资讯" />
            </el-col>
</el-row>

        <!-- 文章发布弹窗 -->
        <el-dialog
            v-model="articleDialogVisible"
            title="发布新文章"
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
                    <el-button type="primary" @click="submitArticleForm(articleFormRef)">发布</el-button>
                </span>
            </template>
        </el-dialog>

      </el-main>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Reading, Picture, Plus } from '@element-plus/icons-vue'
import { getArticles, createArticle, ArticleItem } from '../api/article'
import { ElMessage, FormInstance } from 'element-plus'

const router = useRouter()
const articleList = ref<ArticleItem[]>([])
const loading = ref(false)

// 简单的权限判断，实际应从 Pinia 或 localStorage 获取
console.log('Knowledge.vue mounted')
console.log('localStorage is_admin:', localStorage.getItem('is_admin'))
const isAdmin = ref(localStorage.getItem('is_admin') === 'true')
console.log('isAdmin ref:', isAdmin.value)

// 表单相关
const articleDialogVisible = ref(false)
const articleFormRef = ref<FormInstance>()
const articleForm = reactive<ArticleItem>({
    title: '',
    content: '',
    cover_image: '',
    author: localStorage.getItem('username') || '管理员',
    is_published: true
})

const articleRules = {
    title: [{ required: true, message: '请输入文章标题', trigger: 'blur' }],
    content: [{ required: true, message: '请输入文章内容', trigger: 'blur' }]
}

const loadArticles = async () => {
    loading.value = true
    try {
        const res: any = await getArticles({ limit: 50 })
        articleList.value = res
    } catch (error) {
        console.error(error)
    } finally {
        loading.value = false
    }
}

const goToDetail = (id: number) => {
    router.push(`/article/${id}`)
}

const openPublishDialog = () => {
    articleForm.title = ''
    articleForm.content = ''
    articleForm.cover_image = ''
    articleDialogVisible.value = true
}

const submitArticleForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate(async (valid) => {
        if (valid) {
            try {
                await createArticle(articleForm)
                ElMessage.success('发布成功')
                articleDialogVisible.value = false
                loadArticles()
            } catch (error) {
                console.error(error)
            }
        }
    })
}

onMounted(() => {
    loadArticles()
})
</script>

<style scoped>
.knowledge-container {
  min-height: 100vh;
  /* 渐变背景 */
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
}
.header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 0 40px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.logo {
  font-size: 20px;
  font-weight: bold;
  color: var(--eco-green);
  cursor: pointer;
}
.main-content {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}
.page-title {
    text-align: center;
    margin-bottom: 40px;
}
.page-title h2 {
    font-size: 32px;
    color: #303133;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin-bottom: 10px;
}
.page-title p {
    color: #909399;
    font-size: 16px;
}

.article-card {
    cursor: pointer;
    transition: all 0.3s ease;
    border: none;
    border-radius: 12px;
    overflow: hidden;
}
.article-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 16px 32px rgba(0, 0, 0, 0.1);
}

.image-wrapper {
    width: 100%;
    height: 160px;
    overflow: hidden;
}
.image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
}
.article-card:hover .image {
    transform: scale(1.1);
}
.image-placeholder {
    width: 100%;
    height: 160px;
    background-color: #f0f2f5;
    display: flex;
    justify-content: center;
    align-items: center;
}

.article-title {
    font-size: 18px;
    font-weight: bold;
    color: #303133;
    margin: 0 0 10px 0;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2; /* 限制2行 */
    overflow: hidden;
    height: 50px; /* 固定标题高度 */
}

.bottom {
    margin-top: 10px;
    line-height: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    color: #999;
}
</style>
