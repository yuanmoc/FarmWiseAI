<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="12" v-for="(card, index) in cards" :key="index">
        <el-card class="feature-card" :body-style="{ padding: '0px' }">
          <img :src="card.image" class="card-image">
          <div class="card-content">
            <h3>{{ card.title }}</h3>
            <p>{{ card.description }}</p>
            <el-button type="primary" @click="navigateTo(card.route)">
              {{ card.buttonText }}
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="(stat, index) in stats" :key="index">
        <el-card class="stat-card">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const cards = ref([
  {
    title: '智能问答',
    description: '基于AI的智能农业咨询服务，为您解答各类农业问题',
    image: '/assets/qa-feature.png',
    route: '/qa',
    buttonText: '开始咨询'
  },
  {
    title: '知识库管理',
    description: '农业知识文档的管理与检索，支持多种格式文档',
    image: '/assets/knowledge-feature.png',
    route: '/knowledge',
    buttonText: '查看知识库'
  }
])

const stats = ref([
  {
    value: '1000+',
    label: '知识文档'
  },
  {
    value: '5000+',
    label: '用户咨询'
  },
  {
    value: '98%',
    label: '满意度'
  },
  {
    value: '24/7',
    label: '在线服务'
  }
])

const navigateTo = (route: string) => {
  router.push(route)
}
</script>

<style scoped>
.home-container {
  padding: 40px;
}

.feature-card {
  margin-bottom: 30px;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.card-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.card-content {
  padding: 20px;
}

.card-content h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.card-content p {
  color: #606266;
  margin-bottom: 20px;
}

.stats-row {
  margin-top: 40px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  color: #606266;
}
</style> 