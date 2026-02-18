<template>
  <div class="article-detail-container">
    <el-container>
      <el-header class="header">
        <div class="logo" @click="router.push('/knowledge')"><el-icon><Back /></el-icon> 返回列表</div>
        <div class="user-info">
          <el-button @click="router.push('/')">回到首页</el-button>
        </div>
      </el-header>
      <el-main class="main-content" v-loading="loading">
        <div v-if="article" class="article-wrapper">
             <div class="article-header">
                 <h1 class="title">{{ article.title }}</h1>
                 <div class="meta">
                     <span class="user"><el-icon><User /></el-icon> {{ article.author }}</span>
                     <span class="time"><el-icon><Clock /></el-icon> {{ new Date(article.created_at!).toLocaleString() }}</span>
                     <span class="views"><el-icon><View /></el-icon> {{ article.view_count }} 阅读</span>
                 </div>
             </div>
             
             <div class="cover-image" v-if="article.cover_image">
                 <img :src="article.cover_image" alt="cover" />
             </div>

             <div class="content markdown-body" v-html="formattedContent"></div>
        </div>
        <el-empty v-else-if="!loading" description="文章不存在" />
      </el-main>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Back, User, Clock, View } from '@element-plus/icons-vue'
import { getArticle, ArticleItem } from '../api/article'

const route = useRoute()
const router = useRouter()
const article = ref<ArticleItem | null>(null)
const loading = ref(false)

// 简单的 Markdown 渲染 (如果未安装 marked，可以使用简单的换行替换)
// 由于没有安装 marked，这里使用简单的文本格式化
const formattedContent = computed(() => {
    if (!article.value?.content) return ''
    // 将换行符转换为 <br>
    return article.value.content.replace(/\n/g, '<br/>')
})

const loadArticle = async () => {
    const id = Number(route.params.id)
    if (!id) return
    
    loading.value = true
    try {
        const res: any = await getArticle(id)
        article.value = res
    } catch (error) {
        console.error(error)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    loadArticle()
})
</script>

<style scoped>
.article-detail-container {
  min-height: 100vh;
  background-color: #f9f9f9;
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
  font-size: 16px;
  color: #606266;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}
.logo:hover {
    color: var(--eco-green);
}

.main-content {
  padding: 40px;
  max-width: 800px;
  margin: 0 auto;
}

.article-wrapper {
    background: #fff;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.article-header {
    text-align: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.title {
    font-size: 32px;
    color: #303133;
    margin-bottom: 20px;
}

.meta {
    display: flex;
    justify-content: center;
    gap: 20px;
    color: #909399;
    font-size: 14px;
}

.meta span {
    display: flex;
    align-items: center;
    gap: 5px;
}

.cover-image {
    width: 100%;
    margin-bottom: 30px;
    border-radius: 8px;
    overflow: hidden;
}
.cover-image img {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
}

.content {
    font-size: 16px;
    line-height: 1.8;
    color: #303133;
}
</style>
