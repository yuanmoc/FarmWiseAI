<template>
  <el-container class="app-container">
    <el-aside width="200px" v-if="isLoggedIn">
      <el-menu
        :router="true"
        :default-active="activeRoute"
        class="menu-vertical"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><Files /></el-icon>
          <span>知识库</span>
        </el-menu-item>
        <el-menu-item index="/qa">
          <el-icon><ChatDotRound /></el-icon>
          <span>智能问答</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header v-if="isLoggedIn">
        <div class="header-title">智慧农业咨询系统</div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-dropdown">
              {{ userEmail }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
  </div>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { House, Files, ChatDotRound, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const isLoggedIn = computed(() => {
  return localStorage.getItem('token') !== null
})

const userEmail = computed(() => {
  return localStorage.getItem('userEmail') || ''
})

const activeRoute = computed(() => {
  return route.path
})

const handleCommand = (command: string) => {
  if (command === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('userEmail')
    router.push('/login')
  }
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

#app {
  height: 100%;
}

.app-container {
  height: 100vh;
}

.menu-vertical {
  height: 100%;
  border-right: none;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-title {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.el-aside {
  background-color: #fff;
  border-right: 1px solid #dcdfe6;
}

.el-main {
  background-color: #f5f7fa;
  padding: 0;
}
</style>
