import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import History from '../views/History.vue'
import Feedback from '../views/Feedback.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        name: 'Home',
        component: Home,
        meta: { requiresAuth: true }
    },
    {
        path: '/knowledge',
        name: 'Knowledge',
        component: () => import('../views/Knowledge.vue'),
        meta: { requiresAuth: false } // 公开访问
    },
    {
        path: '/article/:id',
        name: 'ArticleDetail',
        component: () => import('../views/ArticleDetail.vue'),
        meta: { requiresAuth: false } // 公开访问
    },
    {
        path: '/admin',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
        path: '/history',
        name: 'History',
        component: History,
        meta: { requiresAuth: true }
    },
    {
        path: '/feedback',
        name: 'Feedback',
        component: Feedback,
        meta: { requiresAuth: true }
    },
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/register',
        name: 'Register',
        component: Register
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    const isAuthenticated = !!token

    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login')
    } else if (to.meta.requiresAdmin) {
        const isAdmin = localStorage.getItem('is_admin') === 'true'
        if (isAdmin) {
            next()
        } else {
            next('/') // 非管理员跳转回首页
        }
    } else {
        next()
    }
})

export default router
