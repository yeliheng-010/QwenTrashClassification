import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const service = axios.create({
    baseURL: '/api', // 使用 Vite 代理指向 http://127.0.0.1:8000
    timeout: 10000 // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
    config => {
        // 从 localStorage 获取 Token
        const token = localStorage.getItem('token')
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`
        }
        return config
    },
    error => {
        console.log(error)
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    response => {
        return response.data
    },
    error => {
        console.log('err' + error)
        let message = error.message
        if (error.response && error.response.data && error.response.data.detail) {
            message = error.response.data.detail
        }

        ElMessage({
            message: message,
            type: 'error',
            duration: 5 * 1000
        })

        // 如果是 401 未授权，可以在这里处理登出逻辑
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token')
            // router.push('/login') // 这里的 router 需要引入，或者并在组件层处理
            window.location.href = '/login'
        }

        return Promise.reject(error)
    }
)

export default service
