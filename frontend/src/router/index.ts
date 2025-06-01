import { createRouter, createWebHistory } from 'vue-router'
import axios, { AxiosError } from 'axios'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('../views/Knowledge.vue')
  },
  {
    path: '/qa',
    name: 'QA',
    component: () => import('../views/QA.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 配置axios
axios.defaults.baseURL = 'http://localhost:8000'

// 添加axios响应拦截器处理token刷新
axios.interceptors.response.use(
  (response) => {
    const newToken = response.headers['x-new-token']
    if (newToken) {
      localStorage.setItem('token', newToken)
    }
    return response
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login').then(r => {})
    }
    return error
  }
)


// 添加axios请求拦截器
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return error
  }
)

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router 