import request from '../utils/request'

// 文章数据接口定义
export interface ArticleItem {
    id?: number
    title: string
    content: string
    cover_image?: string
    author?: string
    view_count?: number
    is_published?: boolean
    created_at?: string
    updated_at?: string
}

// 获取文章列表 (公开)
export const getArticles = (params: { skip?: number, limit?: number } = {}) => {
    return request({
        url: '/articles',
        method: 'get',
        params
    })
}

// 获取文章详情 (公开)
export const getArticle = (id: number) => {
    return request({
        url: `/articles/${id}`,
        method: 'get'
    })
}

// 发布新文章 (管理员)
export const createArticle = (data: ArticleItem) => {
    return request({
        url: '/articles/admin',
        method: 'post',
        data
    })
}

// 修改文章 (管理员)
export const updateArticle = (id: number, data: ArticleItem) => {
    return request({
        url: `/articles/admin/${id}`,
        method: 'put',
        data
    })
}

// 删除文章 (管理员)
export const deleteArticle = (id: number) => {
    return request({
        url: `/articles/admin/${id}`,
        method: 'delete'
    })
}
