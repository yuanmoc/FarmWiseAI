<template>
  <div class="knowledge-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="category-card">
          <template #header>
            <div class="card-header">
              <span>文档分类</span>
              <el-button type="primary" size="small" @click="showAddCategoryDialog">
                添加分类
              </el-button>
            </div>
          </template>
          <el-tree :data="categories" :props="defaultProps" @node-click="handleNodeClick" />
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>文档列表</span>
              <el-upload
                class="upload-demo"
                :action="uploadUrl"
                :headers="uploadHeaders"
                :data="uploadData"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
              >
                <el-button type="primary">上传文档</el-button>
              </el-upload>
            </div>
          </template>
          <el-table :data="documents" style="width: 100%">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="category" label="分类" />
            <el-table-column label="创建时间">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="file_type" label="文件类型" />
            <el-table-column label="操作" width="420">
              <template #default="scope">
                <el-button type="text" @click="viewDocument(scope.row)">查看</el-button>
                <el-button type="text" @click="editDocument(scope.row)">修改</el-button>
                <el-button type="text" @click="viewVectors(scope.row)">向量数据</el-button>
                <el-button type="text" @click="reprocessDocument(scope.row)">重新处理</el-button>
                <el-button type="text" class="delete-btn" @click="deleteDocument(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 添加分页组件 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="pagination.currentPage"
              v-model:page-size="pagination.pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="pagination.total"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              layout="total, sizes, prev, pager, next"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加分类对话框 -->
    <el-dialog v-model="categoryDialog" title="添加分类">
      <el-form :model="categoryForm" :rules="categoryRules" ref="categoryFormRef">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="categoryForm.description" />
        </el-form-item>
        <el-form-item label="父级分类">
          <el-select v-model="categoryForm.parent_id" clearable placeholder="请选择">
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="categoryDialog = false">取消</el-button>
          <el-button type="primary" @click="submitCategory">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 向量数据对话框 -->
    <el-dialog
      v-model="vectorDialog"
      title="文档向量数据"
      width="80%"
      :close-on-click-modal="false"
    >
      <el-table :data="vectorData" style="width: 100%" max-height="500">
        <el-table-column prop="id" label="向量ID" width="180" />
        <el-table-column prop="chunk_index" label="块索引" width="100" />
        <el-table-column prop="text" label="文本内容">
          <template #default="scope">
            <div class="text-content">
              <div v-if="!scope.row.isExpanded" class="text-preview">
                {{ scope.row.text.slice(0, 100) }}
                <span v-if="scope.row.text.length > 100">...</span>
              </div>
              <div v-else class="text-full" style="white-space: pre-wrap;">
                {{ scope.row.text }}
              </div>
              <el-button 
                v-if="scope.row.text.length > 100"
                link 
                type="primary" 
                @click="scope.row.isExpanded = !scope.row.isExpanded"
              >
                {{ scope.row.isExpanded ? '收起' : '展开' }}
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="元数据" width="200">
          <template #default="scope">
            <div v-for="(value, key) in scope.row.metadata" :key="key">
              <strong>{{ key }}:</strong> {{ value }}
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 添加向量数据分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="vectorPagination.currentPage"
          v-model:page-size="vectorPagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="vectorPagination.total"
          @size-change="handleVectorSizeChange"
          @current-change="handleVectorCurrentChange"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </el-dialog>

    <!-- 添加修改文档对话框 -->
    <el-dialog v-model="editDialog" title="修改文档">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="editForm.category" placeholder="请选择分类">
            <el-option
              v-for="item in flatCategories"
              :key="item.name"
              :label="item.name"
              :value="item.name"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialog = false">取消</el-button>
          <el-button type="primary" @click="submitEdit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

interface Category {
  id: number
  name: string
  description?: string
  children?: Category[]
}

interface Document {
  id: number
  title: string
  category: string
  file_path: string
  file_type: string
  created_at: string
  updated_at: string
}

interface DocumentResponse {
  items: Document[];
  total: number;
  page: number;
  size: number;
}

interface VectorItem {
  id: number | string;
  text: string;
  metadata: Record<string, any>;
  chunk_index?: number;
  score?: number;
}

const categories = ref<Category[]>([])
const documents = ref<Document[]>([])
const categoryDialog = ref(false)
const categoryFormRef = ref()
const vectorDialog = ref(false)
const vectorData = ref<VectorItem[]>([])
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const vectorPagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const currentDocId = ref<number | null>(null)

const defaultProps = {
  children: 'children',
  label: 'name'
}

const categoryForm = reactive({
  name: '',
  description: '',
  parent_id: null as number | null
})

const categoryRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

const uploadData = reactive({
  title: '',
  category: ''
})

const uploadUrl = computed(() => {
  return `${axios.defaults.baseURL}/api/v1/knowledge/documents/upload`
})

const editDialog = ref(false)
const editFormRef = ref()
const editForm = reactive({
  id: 0,
  title: '',
  category: ''
})

const editRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

onMounted(async () => {
  await loadCategories()
  await loadDocuments()
})

const loadCategories = async () => {
  try {
    const response = await axios.get('/api/v1/knowledge/categories')
    categories.value = response.data.categories
  } catch (error) {
    ElMessage.error('加载分类失败')
  }
}

const loadDocuments = async (category?: string) => {
  try {
    const response = await axios.get<DocumentResponse>('/api/v1/knowledge/documents', {
      params: { 
        category,
        page: pagination.currentPage,
        size: pagination.pageSize
      }
    })
    documents.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('加载文档失败')
  }
}

const handleNodeClick = async (data: Category) => {
  await loadDocuments(data.name)
}

const showAddCategoryDialog = () => {
  categoryDialog.value = true
}

const submitCategory = async () => {
  if (!categoryFormRef.value) return

  await categoryFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        await axios.post('/api/v1/knowledge/categories', categoryForm)
        ElMessage.success('添加分类成功')
        categoryDialog.value = false
        await loadCategories()
      } catch (error) {
        ElMessage.error('添加分类失败')
      }
    }
  })
}

const handleUploadSuccess = () => {
  ElMessage.success('上传成功')
  loadDocuments(uploadData.category)
}

const handleUploadError = (error: any) => {
  console.error('上传失败:', error)
  ElMessage.error('上传失败：' + (error.response?.data?.detail || '未知错误'))
}

const viewDocument = (row: Document) => {
  // 在新窗口中打开文档
  window.open(`${axios.defaults.baseURL}/${row.file_path}`, '_blank')
}

const deleteDocument = async (row: Document) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文档吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete(`/api/v1/knowledge/documents/${row.id}`)
    ElMessage.success('删除成功')
    await loadDocuments(row.category)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || '未知错误'))
    }
  }
}

const reprocessDocument = async (row: Document) => {
  try {
    await ElMessageBox.confirm('确定要重新处理这个文档的向量数据吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await axios.post(`/api/v1/knowledge/documents/${row.id}/reprocess`)
    ElMessage.success('重新处理成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('重新处理失败：' + (error.response?.data?.detail || '未知错误'))
    }
  }
}

const viewVectors = async (row: Document) => {
  try {
    currentDocId.value = row.id
    const response = await axios.get(`/api/v1/knowledge/documents/${row.id}/vectors`, {
      params: {
        page: vectorPagination.currentPage,
        size: vectorPagination.pageSize
      }
    })
    vectorData.value = response.data.items.map((item: VectorItem) => ({
      ...item,
      isExpanded: false // 初始化展开状态
    }))
    vectorPagination.total = response.data.total
    vectorDialog.value = true
  } catch (error: any) {
    console.error('获取向量数据失败:', error)
    ElMessage.error('获取向量数据失败')
  }
}

const handleCurrentChange = async (page: number) => {
  pagination.currentPage = page
  await loadDocuments()
}

const handleSizeChange = async (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  await loadDocuments()
}

const handleVectorSizeChange = async (size: number) => {
  vectorPagination.pageSize = size
  vectorPagination.currentPage = 1
  if (currentDocId.value !== null) {
    await viewVectors({ id: currentDocId.value } as Document)
  }
}

const handleVectorCurrentChange = async (page: number) => {
  vectorPagination.currentPage = page
  if (currentDocId.value !== null) {
    await viewVectors({ id: currentDocId.value } as Document)
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 计算属性：将分类树展平为列表
const flatCategories = computed(() => {
  const result: Category[] = []
  const flatten = (items: Category[]) => {
    items.forEach(item => {
      result.push(item)
      if (item.children) {
        flatten(item.children)
      }
    })
  }
  flatten(categories.value)
  return result
})

// 打开修改对话框
const editDocument = (row: Document) => {
  editForm.id = row.id
  editForm.title = row.title
  editForm.category = row.category
  editDialog.value = true
}

// 提交修改
const submitEdit = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        await axios.put(`/api/v1/knowledge/documents/${editForm.id}`, {
          title: editForm.title,
          category: editForm.category
        })
        ElMessage.success('修改成功')
        editDialog.value = false
        await loadDocuments()
      } catch (error: any) {
        ElMessage.error('修改失败：' + (error.response?.data?.detail || '未知错误'))
      }
    }
  })
}
</script>

<style scoped>
.knowledge-container {
  padding: 20px;
}

.category-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  margin-top: 20px;
}

.delete-btn {
  color: #F56C6C;
}

.el-table :deep(.cell) {
  word-break: break-word;
}

.text-content {
  position: relative;
}

.text-preview {
  color: #606266;
}

.text-full {
  margin-bottom: 8px;
  color: #303133;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 