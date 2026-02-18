<template>
  <div class="attachment-management-view">
    <el-card class="header-card">
      <div class="header-content">
        <h2>附件管理</h2>
        <p class="subtitle">
          查阅和下载所有归档附件
        </p>
      </div>
    </el-card>

    <el-card class="filter-card">
      <el-form
        :inline="true"
        :model="filters"
        class="filter-form"
      >
        <el-form-item label="教研室">
          <el-input
            v-model="filters.teachingOfficeName"
            placeholder="输入教研室名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="考核指标">
          <el-select
            v-model="filters.indicator"
            placeholder="选择考核指标"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="indicator in indicators"
              :key="indicator.key"
              :label="indicator.label"
              :value="indicator.key"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="考核年度">
          <el-select
            v-model="filters.evaluationYear"
            placeholder="选择年度"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="year in availableYears"
              :key="year"
              :label="`${year}年`"
              :value="year"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="loadAttachments"
          >
            查询
          </el-button>
          <el-button @click="resetFilters">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="content-card">
      <el-table
        v-loading="loading"
        :data="paginatedAttachments"
        stripe
        style="width: 100%"
      >
        <el-table-column
          prop="file_name"
          label="文件名"
          min-width="200"
        />
        
        <el-table-column
          label="考核指标"
          width="150"
        >
          <template #default="{ row }">
            <el-tag>{{ getIndicatorLabel(row.indicator) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column
          prop="teaching_office_name"
          label="教研室"
          width="150"
        />
        
        <el-table-column
          prop="evaluation_year"
          label="考核年度"
          width="100"
        >
          <template #default="{ row }">
            {{ row.evaluation_year }}年
          </template>
        </el-table-column>

        <el-table-column
          label="文件大小"
          width="120"
        >
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>

        <el-table-column
          label="上传时间"
          width="180"
        >
          <template #default="{ row }">
            {{ formatDate(row.uploaded_at) }}
          </template>
        </el-table-column>

        <el-table-column
          label="归档状态"
          width="100"
        >
          <template #default="{ row }">
            <el-tag :type="row.is_archived ? 'success' : 'info'">
              {{ row.is_archived ? '已归档' : '未归档' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="操作"
          width="150"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="Download"
              :disabled="!row.is_archived"
              @click="downloadAttachment(row)"
            >
              下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div
        v-if="attachments.length === 0 && !loading"
        class="empty-state"
      >
        <el-empty description="暂无附件数据" />
      </div>

      <div
        v-if="attachments.length > 0"
        class="pagination-container"
      >
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import apiClient from '@/api/client'
import { INDICATORS } from '@/types/attachment'
import type { AttachmentWithRelations } from '@/types/attachment'

// State
const loading = ref(false)
const attachments = ref<AttachmentWithRelations[]>([])
const allAttachments = ref<AttachmentWithRelations[]>([]) // Store all attachments for client-side filtering
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// Filters
const filters = ref({
  teachingOfficeName: '',
  indicator: '',
  evaluationYear: null as number | null
})

// Indicators configuration
const indicators = INDICATORS

// Available years (last 5 years)
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => currentYear - i)
})

// Load attachments
const loadAttachments = async () => {
  loading.value = true
  try {
    const params: any = {
      is_archived: true // Only show archived attachments
    }
    
    if (filters.value.indicator) {
      params.indicator = filters.value.indicator
    }
    
    if (filters.value.evaluationYear) {
      params.evaluation_year = filters.value.evaluationYear
    }

    const response = await apiClient.get('/teaching-office/attachments', { params })
    allAttachments.value = response.data || []
    
    // Apply client-side filtering for teaching office name
    applyFilters()
  } catch (error) {
    console.error('Failed to load attachments:', error)
    ElMessage.error('加载附件列表失败')
  } finally {
    loading.value = false
  }
}

// Apply client-side filters
const applyFilters = () => {
  let filtered = [...allAttachments.value]
  
  // Filter by teaching office name (client-side)
  if (filters.value.teachingOfficeName) {
    const searchTerm = filters.value.teachingOfficeName.toLowerCase()
    filtered = filtered.filter(att => 
      att.teaching_office_name?.toLowerCase().includes(searchTerm)
    )
  }
  
  attachments.value = filtered
  total.value = filtered.length
  currentPage.value = 1 // Reset to first page
}

// Reset filters
const resetFilters = () => {
  filters.value = {
    teachingOfficeName: '',
    indicator: '',
    evaluationYear: null
  }
  loadAttachments()
}

// Download attachment
const downloadAttachment = async (attachment: AttachmentWithRelations) => {
  try {
    const response = await apiClient.get(`/teaching-office/attachments/${attachment.id}/download`, {
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', attachment.file_name)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('文件下载成功')
  } catch (error) {
    console.error('Failed to download attachment:', error)
    ElMessage.error('文件下载失败')
  }
}

// Get indicator label
const getIndicatorLabel = (key: string): string => {
  const indicator = indicators.find(i => i.key === key)
  return indicator ? indicator.label : key
}

// Format file size
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Format date
const formatDate = (dateString: string): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Pagination handlers
const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
}

// Computed paginated data
const paginatedAttachments = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return attachments.value.slice(start, end)
})

// Initialize
onMounted(async () => {
  await loadAttachments()
})
</script>

<style scoped>
.attachment-management-view {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.header-content {
  text-align: center;
}

.header-content h2 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 24px;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin: 0;
}

.content-card {
  min-height: 400px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
