<template>
  <div class="admin-analytics-page">
    <div class="page-header">
      <h1>Analytics Dashboard</h1>
      <p>Comprehensive placement analytics and insights</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading analytics data...</p>
    </div>

    <div v-else class="analytics-content">
      <!-- Funnel Section -->
      <section class="analytics-section">
        <h2>Application Funnel</h2>
        <div class="funnel-grid">
          <div class="funnel-chart-container">
            <Bar v-if="funnelChartData" :data="funnelChartData" :options="horizontalBarOptions" />
          </div>
          <div class="funnel-stats">
            <h3>Conversion Rates</h3>
            <div class="conversion-rates" v-if="funnelData?.conversion_rates">
              <div class="rate-item">
                <span class="rate-label">Applied → Shortlisted</span>
                <span class="rate-value">{{ funnelData.conversion_rates.applied_to_shortlisted || 0 }}%</span>
              </div>
              <div class="rate-item">
                <span class="rate-label">Shortlisted → Interview</span>
                <span class="rate-value">{{ funnelData.conversion_rates.shortlisted_to_interview || 0 }}%</span>
              </div>
              <div class="rate-item">
                <span class="rate-label">Interview → Offered</span>
                <span class="rate-value">{{ funnelData.conversion_rates.interview_to_offered || 0 }}%</span>
              </div>
              <div class="rate-item">
                <span class="rate-label">Offered → Placed</span>
                <span class="rate-value">{{ funnelData.conversion_rates.offered_to_placed || 0 }}%</span>
              </div>
              <div class="rate-item overall">
                <span class="rate-label">Overall Success Rate</span>
                <span class="rate-value">{{ funnelData.conversion_rates.overall || 0 }}%</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Placement Trends Section -->
      <section class="analytics-section">
        <h2>Placement Trends (Last 12 Months)</h2>
        <div class="chart-container large">
          <Line v-if="trendsChartData" :data="trendsChartData" :options="lineChartOptions" />
        </div>
      </section>

      <!-- Job Demand Section -->
      <section class="analytics-section">
        <h2>Job Market Demand</h2>
        <div class="demand-grid">
          <div class="chart-card">
            <h3>Top Skills in Demand</h3>
            <div class="chart-container">
              <Bar v-if="skillsChartData" :data="skillsChartData" :options="barChartOptions" />
            </div>
          </div>
          <div class="chart-card">
            <h3>Package Distribution</h3>
            <div class="chart-container">
              <Doughnut v-if="packageChartData" :data="packageChartData" :options="doughnutOptions" />
            </div>
          </div>
        </div>
        <div class="demand-grid">
          <div class="chart-card">
            <h3>Role Types</h3>
            <div class="chart-container">
              <Pie v-if="rolesChartData" :data="rolesChartData" :options="pieOptions" />
            </div>
          </div>
          <div class="chart-card">
            <h3>Top Locations</h3>
            <div class="locations-list">
              <div 
                class="location-item" 
                v-for="loc in jobDemandData?.locations?.slice(0, 8)" 
                :key="loc.location"
              >
                <span class="location-name">{{ loc.location }}</span>
                <div class="location-bar">
                  <div 
                    class="location-fill" 
                    :style="{ width: getLocationWidth(loc.count) + '%' }"
                  ></div>
                </div>
                <span class="location-count">{{ loc.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Branch Performance Section -->
      <section class="analytics-section">
        <h2>Branch-wise Performance</h2>
        <div class="table-container">
          <table class="analytics-table">
            <thead>
              <tr>
                <th>Branch</th>
                <th>Applications</th>
                <th>Placements</th>
                <th>Success Rate</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="branch in funnelData?.branch_performance" :key="branch.branch">
                <td>{{ branch.branch }}</td>
                <td>{{ branch.total_applications }}</td>
                <td>{{ branch.placements }}</td>
                <td>
                  <span class="success-rate" :class="getSuccessClass(branch.success_rate)">
                    {{ branch.success_rate }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Status Breakdown -->
      <section class="analytics-section">
        <h2>Current Status Breakdown</h2>
        <div class="status-cards">
          <div 
            class="status-card" 
            v-for="(count, status) in funnelData?.status_breakdown" 
            :key="status"
          >
            <div class="status-count">{{ count }}</div>
            <div class="status-label">{{ status }}</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Line, Bar, Doughnut, Pie } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import api from '@/services/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const loading = ref(true)
const trendsData = ref(null)
const jobDemandData = ref(null)
const funnelData = ref(null)

// Chart Options
const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' },
  },
  scales: {
    y: { beginAtZero: true },
  },
}

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: { display: false },
  },
}

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

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'right' },
  },
}

const pieOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'right' },
  },
}

// Computed chart data
const trendsChartData = computed(() => {
  if (!trendsData.value?.trends) return null
  
  return {
    labels: trendsData.value.trends.map(t => t.month),
    datasets: [
      {
        label: 'Applied',
        data: trendsData.value.trends.map(t => t.applied),
        borderColor: '#2196F3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Shortlisted',
        data: trendsData.value.trends.map(t => t.shortlisted),
        borderColor: '#FF9800',
        backgroundColor: 'rgba(255, 152, 0, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Placed',
        data: trendsData.value.trends.map(t => t.placed),
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  }
})

const funnelChartData = computed(() => {
  if (!funnelData.value?.funnel) return null
  
  const funnel = funnelData.value.funnel
  return {
    labels: ['Applied', 'Shortlisted', 'Interview', 'Offered', 'Placed'],
    datasets: [{
      data: [funnel.applied, funnel.shortlisted, funnel.interview, funnel.offered, funnel.placed],
      backgroundColor: [
        'rgba(33, 150, 243, 0.8)',
        'rgba(255, 152, 0, 0.8)',
        'rgba(156, 39, 176, 0.8)',
        'rgba(0, 188, 212, 0.8)',
        'rgba(76, 175, 80, 0.8)',
      ],
    }],
  }
})

const skillsChartData = computed(() => {
  if (!jobDemandData.value?.skills) return null
  
  const topSkills = jobDemandData.value.skills.slice(0, 10)
  return {
    labels: topSkills.map(s => s.skill),
    datasets: [{
      data: topSkills.map(s => s.demand),
      backgroundColor: 'rgba(102, 126, 234, 0.8)',
    }],
  }
})

const packageChartData = computed(() => {
  if (!jobDemandData.value?.package_distribution) return null
  
  const packages = jobDemandData.value.package_distribution
  return {
    labels: Object.keys(packages),
    datasets: [{
      data: Object.values(packages),
      backgroundColor: [
        'rgba(76, 175, 80, 0.8)',
        'rgba(33, 150, 243, 0.8)',
        'rgba(255, 152, 0, 0.8)',
        'rgba(156, 39, 176, 0.8)',
        'rgba(244, 67, 54, 0.8)',
      ],
    }],
  }
})

const rolesChartData = computed(() => {
  if (!jobDemandData.value?.roles) return null
  
  return {
    labels: jobDemandData.value.roles.map(r => r.role),
    datasets: [{
      data: jobDemandData.value.roles.map(r => r.count),
      backgroundColor: [
        'rgba(102, 126, 234, 0.8)',
        'rgba(118, 75, 162, 0.8)',
        'rgba(76, 175, 80, 0.8)',
        'rgba(255, 152, 0, 0.8)',
        'rgba(33, 150, 243, 0.8)',
        'rgba(156, 39, 176, 0.8)',
        'rgba(0, 188, 212, 0.8)',
        'rgba(244, 67, 54, 0.8)',
      ],
    }],
  }
})

const getLocationWidth = (count) => {
  if (!jobDemandData.value?.locations?.length) return 0
  const maxCount = Math.max(...jobDemandData.value.locations.map(l => l.count))
  return (count / maxCount) * 100
}

const getSuccessClass = (rate) => {
  if (rate >= 50) return 'excellent'
  if (rate >= 30) return 'good'
  if (rate >= 15) return 'fair'
  return 'low'
}

const fetchAnalytics = async () => {
  loading.value = true
  try {
    const [trendsRes, demandRes, funnelRes] = await Promise.all([
      api.get('/analytics/placement-trends'),
      api.get('/analytics/job-demand'),
      api.get('/analytics/funnel'),
    ])
    
    trendsData.value = trendsRes.data
    jobDemandData.value = demandRes.data
    funnelData.value = funnelRes.data
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
