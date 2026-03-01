<template>
  <div class="company-analytics-page">
    <div class="page-header">
      <h1>Company Analytics</h1>
      <p>Track your recruitment performance and hiring funnel</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading analytics...</p>
    </div>

    <div v-else-if="analytics" class="analytics-content">
      <!-- Overview Cards -->
      <section class="overview-section">
        <div class="stats-grid">
          <div class="stat-card primary">
            <div class="stat-value">{{ analytics.overview.total_drives }}</div>
            <div class="stat-label">Total Drives</div>
          </div>
          <div class="stat-card info">
            <div class="stat-value">{{ analytics.overview.total_applications }}</div>
            <div class="stat-label">Total Applications</div>
          </div>
          <div class="stat-card success">
            <div class="stat-value">{{ analytics.overview.total_placed }}</div>
            <div class="stat-label">Students Placed</div>
          </div>
        </div>
      </section>

      <!-- Funnel Visualization -->
      <section class="funnel-section">
        <h2>Recruitment Funnel</h2>
        <div class="funnel-container">
          <div class="funnel-chart">
            <Bar v-if="funnelChartData" :data="funnelChartData" :options="horizontalBarOptions" />
          </div>
          <div class="funnel-breakdown">
            <h3>Status Breakdown</h3>
            <div class="breakdown-list">
              <div 
                class="breakdown-item" 
                v-for="(count, status) in analytics.funnel" 
                :key="status"
              >
                <span class="status-dot" :class="getStatusClass(status)"></span>
                <span class="status-name">{{ status }}</span>
                <span class="status-count">{{ count }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Drive-wise Performance -->
      <section class="drives-section">
        <h2>Drive-wise Performance</h2>
        <div v-if="analytics.drive_performance && analytics.drive_performance.length > 0" class="drives-grid">
          <div 
            class="drive-card" 
            v-for="drive in analytics.drive_performance" 
            :key="drive.drive_id"
          >
            <div class="drive-header">
              <h3>{{ drive.job_title }}</h3>
              <span class="drive-status" :class="drive.status">{{ drive.status }}</span>
            </div>
            <div class="drive-stats">
              <div class="drive-stat">
                <span class="stat-num">{{ drive.total_applications }}</span>
                <span class="stat-label">Applications</span>
              </div>
              <div class="drive-stat">
                <span class="stat-num success">{{ drive.placed }}</span>
                <span class="stat-label">Placed</span>
              </div>
              <div class="drive-stat">
                <span class="stat-num">
                  {{ drive.total_applications ? Math.round(drive.placed / drive.total_applications * 100) : 0 }}%
                </span>
                <span class="stat-label">Success Rate</span>
              </div>
            </div>
            <div class="drive-date">
              Created: {{ formatDate(drive.created_at) }}
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
      <h2>No Data Yet</h2>
      <p>Create placement drives to see your analytics.</p>
      <button class="btn" @click="$router.push('/company/drives')">Create Drive</button>
    </div>
      </section>

    </div>

    
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import api from '@/services/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const loading = ref(true)
const analytics = ref(null)

const horizontalBarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { beginAtZero: true },
  },
}

const funnelChartData = computed(() => {
  if (!analytics.value?.funnel) return null
  
  const statusOrder = ['Applied', 'Shortlisted', 'Interview', 'Offer', 'Selected', 'Placed', 'Rejected']
  const colors = {
    'Applied': 'rgba(33, 150, 243, 0.8)',
    'Shortlisted': 'rgba(255, 152, 0, 0.8)',
    'Interview': 'rgba(156, 39, 176, 0.8)',
    'Offer': 'rgba(0, 188, 212, 0.8)',
    'Selected': 'rgba(76, 175, 80, 0.8)',
    'Placed': 'rgba(46, 125, 50, 0.8)',
    'Rejected': 'rgba(244, 67, 54, 0.8)',
  }
  
  const data = []
  const labels = []
  const bgColors = []
  
  for (const status of statusOrder) {
    if (analytics.value.funnel[status] !== undefined) {
      labels.push(status)
      data.push(analytics.value.funnel[status])
      bgColors.push(colors[status] || 'rgba(158, 158, 158, 0.8)')
    }
  }
  
  return {
    labels,
    datasets: [{
      data,
      backgroundColor: bgColors,
      borderRadius: 4,
    }],
  }
})

const getStatusClass = (status) => {
  const classes = {
    'Applied': 'applied',
    'Shortlisted': 'shortlisted',
    'Interview': 'interview',
    'Offer': 'offer',
    'Selected': 'selected',
    'Placed': 'placed',
    'Rejected': 'rejected',
  }
  return classes[status] || 'default'
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const fetchAnalytics = async () => {
  loading.value = true
  try {
    const response = await api.get('/company/analytics')
    analytics.value = response.data
  } catch (err) {
    console.error('Failed to fetch analytics:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAnalytics()
})
</script>
