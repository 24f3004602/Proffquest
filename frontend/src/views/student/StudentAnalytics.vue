<template>
  <div class="student-analytics-page">
    <div class="page-header">
      <h1>My Analytics</h1>
      <p>Track your application progress and performance</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading your analytics...</p>
    </div>

    <div v-else-if="analytics" class="analytics-content">
      <!-- Overview Cards -->
      <section class="overview-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ analytics.overview.total_applications }}</div>
            <div class="stat-label">Total Applications</div>
          </div>
          <div class="stat-card success">
            <div class="stat-value">{{ analytics.overview.placed }}</div>
            <div class="stat-label">Placements</div>
          </div>
          <div class="stat-card info">
            <div class="stat-value">{{ analytics.overview.shortlisted }}</div>
            <div class="stat-label">Shortlisted</div>
          </div>
          <div class="stat-card warning">
            <div class="stat-value">{{ analytics.overview.interviews }}</div>
            <div class="stat-label">Interviews</div>
          </div>
          <div class="stat-card primary">
            <div class="stat-value">{{ analytics.overview.offers }}</div>
            <div class="stat-label">Offers</div>
          </div>
          <div class="stat-card danger">
            <div class="stat-value">{{ analytics.overview.rejected }}</div>
            <div class="stat-label">Rejected</div>
          </div>
        </div>
      </section>

      <!-- Application Timeline Chart -->
       <div class="student-analytics">
      <section class="chart-section">
        <h2>Application Timeline (Last 6 Months)</h2>
        <div class="chart-container">
          <Bar v-if="timelineChartData" :data="timelineChartData" :options="barChartOptions" />
        </div>
      </section>

      <!-- Status Distribution -->
      <section class="chart-section">
        <h2>Application Status Distribution</h2>
        <div class="distribution-grid">
          <div class="pie-chart-container">
            <Doughnut v-if="statusChartData" :data="statusChartData" :options="doughnutOptions" />
          </div>
            <h3>Status Details</h3>
            <div class="status-list">
              <div 
                class="status-item" 
                v-for="(count, status) in analytics.status_breakdown" 
                :key="status"
              >
                <span class="status-name">{{ status }}</span>
                <span class="status-count">{{ count }}</span>
                <span class="status-percent">
                  {{ getPercentage(count, analytics.overview.total_applications) }}%
                </span>
              </div>
            </div>
          
        </div>
      </section>
      </div>
      <!-- Success Metrics -->
       <div class="student-analytics">
      <section class="metrics-section">
        <h2>Success Metrics</h2>
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-label">Response Rate</div>
            <div class="metric-value">
              {{ getResponseRate() }}%
            </div>
            <div class="metric-desc">Applications that got a response</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Interview Rate</div>
            <div class="metric-value">
              {{ getInterviewRate() }}%
            </div>
            <div class="metric-desc">Applications that led to interviews</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value highlight">
              {{ getSuccessRate() }}%
            </div>
            <div class="metric-desc">Applications that resulted in placement</div>
          </div>
        </div>
      </section>

      <!-- Tips Section -->
      <section class="tips-section">
        <h2>Tips to Improve</h2>
        <div class="tips-grid">
          <div class="tip-card" v-if="analytics.overview.rejected > analytics.overview.shortlisted">
            <h3>Enhance Your Resume</h3>
            <p>Try our ATS Resume Screener to optimize your resume for better matches.</p>
            <router-link to="/ats-screener" class="tip-link">Try ATS Screener</router-link>
          </div>
          <div class="tip-card" v-if="analytics.overview.shortlisted > analytics.overview.interviews">
            <h3>Prepare for Interviews</h3>
            <p>You're getting shortlisted! Focus on interview preparation to convert more.</p>
          </div>
          <div class="tip-card" v-if="analytics.overview.total_applications < 10">
            <h3>Apply More</h3>
            <p>Increase your applications to improve your chances of placement.</p>
            <router-link to="/student/drives" class="tip-link">View Drives</router-link>
          </div>
          <div class="tip-card" v-if="getSuccessRate() >= 20">
            <h3>Great Performance!</h3>
            <p>Your success rate is above average. Keep up the good work!</p>
          </div>
        </div>
      </section>
       </div>
       </div>
    

    <div v-else class="empty-state">
      <h2>No Data Yet</h2>
      <p>Start applying to placement drives to see your analytics.</p>
      <router-link to="/student/drives" class="btn-primary">Browse Drives</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import api from '@/services/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const loading = ref(true)
const analytics = ref(null)

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    y: { beginAtZero: true },
  },
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' },
  },
}

const timelineChartData = computed(() => {
  if (!analytics.value?.timeline) return null
  
  return {
    labels: analytics.value.timeline.map(t => t.month),
    datasets: [{
      label: 'Applications',
      data: analytics.value.timeline.map(t => t.applications),
      backgroundColor: 'rgba(102, 126, 234, 0.8)',
      borderColor: '#667eea',
      borderWidth: 1,
      borderRadius: 6,
    }],
  }
})

const statusChartData = computed(() => {
  if (!analytics.value?.status_breakdown) return null
  
  const statusColors = {
    'Applied': 'rgba(33, 150, 243, 0.8)',
    'Shortlisted': 'rgba(255, 152, 0, 0.8)',
    'Interview': 'rgba(156, 39, 176, 0.8)',
    'Offer': 'rgba(0, 188, 212, 0.8)',
    'Selected': 'rgba(76, 175, 80, 0.8)',
    'Placed': 'rgba(46, 125, 50, 0.8)',
    'Rejected': 'rgba(244, 67, 54, 0.8)',
  }
  
  const labels = Object.keys(analytics.value.status_breakdown)
  const data = Object.values(analytics.value.status_breakdown)
  const colors = labels.map(l => statusColors[l] || 'rgba(158, 158, 158, 0.8)')
  
  return {
    labels,
    datasets: [{
      data,
      backgroundColor: colors,
    }],
  }
})

const getPercentage = (value, total) => {
  if (!total) return 0
  return Math.round((value / total) * 100)
}

const getResponseRate = () => {
  if (!analytics.value?.overview) return 0
  const total = analytics.value.overview.total_applications
  const responded = total - (analytics.value.status_breakdown?.Applied || 0)
  return total ? Math.round((responded / total) * 100) : 0
}

const getInterviewRate = () => {
  if (!analytics.value?.overview) return 0
  const total = analytics.value.overview.total_applications
  const interviews = (analytics.value.overview.interviews || 0) + 
                     (analytics.value.overview.offers || 0) + 
                     (analytics.value.overview.placed || 0)
  return total ? Math.round((interviews / total) * 100) : 0
}

const getSuccessRate = () => {
  if (!analytics.value?.overview) return 0
  const total = analytics.value.overview.total_applications
  const placed = analytics.value.overview.placed || 0
  return total ? Math.round((placed / total) * 100) : 0
}

const fetchAnalytics = async () => {
  loading.value = true
  try {
    const response = await api.get('/student/analytics')
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
