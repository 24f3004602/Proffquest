
<template>
  <div class="home-page">
    <div class="hero-section">
      <div class="hero-content">
        <p class="hero-eyebrow">Campus Placements Reimagined</p>
        <h1 class="hero-title">Welcome to ProffQuest</h1>
        <p class="hero-subtitle">Bridging the gap between students and companies</p>
        <div class="hero-highlights">
          <span>Smart Matching</span>
          <span>Realtime Insights</span>
          <span>Faster Hiring</span>
        </div>
      </div>
    </div>

    <!-- Statistics Section -->
    <div class="stats-section" v-if="stats">
      <div class="container">
        <h2 class="section-title">Placement Statistics</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">{{ stats.summary?.total_placements || 0 }}</div>
            <div class="stat-label">Students Placed</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ stats.summary?.total_drives || 0 }}</div>
            <div class="stat-label">Placement Drives</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ stats.summary?.active_companies || 0 }}</div>
            <div class="stat-label">Active Companies</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ stats.summary?.registered_students || 0 }}</div>
            <div class="stat-label">Registered Students</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section" v-if="stats && stats.monthly_trends">
      <div class="container">
        <h2 class="section-title">Monthly Placement Trends</h2>
        <div class="charts-grid">
          <div class="chart-card">
            <h3>Placements Over Time</h3>
            <div class="chart-container">
              <Line v-if="placementChartData" :data="placementChartData" :options="chartOptions" />
            </div>
          </div>
          <div class="chart-card">
            <h3>Drives vs Applications</h3>
            <div class="chart-container">
              <Bar v-if="drivesChartData" :data="drivesChartData" :options="chartOptions" />
            </div>
          </div>
        </div>

      </div>
    </div>

    <div class="content-section">
      <div class="container">
        <section class="about-section">
          <h2 class="section-title">About ProffQuest</h2>
          <p>ProffQuest is a comprehensive platform designed to bridge the gap between students and companies. It offers a seamless experience for students to explore placement opportunities and for companies to connect with potential candidates. Our mission is to facilitate meaningful connections and foster career growth for students while providing companies with access to a diverse talent pool.</p>
        </section>

        <section class="features-section">
          <h2 class="section-title">Key Features of ProffQuest</h2>
          <div class="features-grid">
            <div class="feature-item">
              <h3>Seamless Student-Company Matching</h3>
              <p>Advanced algorithms to match the right candidates with the right opportunities.</p>
            </div>
            <div class="feature-item">
              <h3>User-Friendly Interface</h3>
              <p>Intuitive design that makes navigation and application simple.</p>
            </div>
            <div class="feature-item">
              <h3>Real-time Analytics</h3>
              <p>Track placement trends, job demand, and application funnels.</p>
            </div>
          </div>
        </section>

        <section class="user-features">
          <div class="features-row">
            <div class="feature-item">
              <h2 class="section-title">Student Features</h2>
              <ul class="feature-list">
                <li>Access to Job Listings</li>
                <li>Application Tracking System</li>
                <li>Personal Analytics Dashboard</li>
                <li>View Placement History</li>
              </ul>
            </div>
            <div class="feature-item">
              <h2 class="section-title">Company Features</h2>
              <ul class="feature-list">
                <li>Post Job Openings</li>
                <li>Search and Filter Candidates</li>
                <li>Analytics & Reporting</li>
                <li>Interview Management</li>
              </ul>
            </div>
          </div>
        </section>

        <section class="benefits-section">
          <h2 class="section-title">Why Choose ProffQuest?</h2>
          <p>ProffQuest simplifies the job search and hiring process by providing a centralized platform where students and companies can connect seamlessly. It offers tools to help students build their profiles, apply to jobs, and track their applications, while companies can easily post job openings, search for candidates, and manage applications. With ProffQuest, both students and companies benefit from a streamlined experience that saves time and effort.</p>
        </section>

        <section class="college-benefits">
          <h2 class="section-title">How This Helps Colleges</h2>
          <p>ProffQuest helps colleges by providing a platform where students can explore placement opportunities, companies can connect with potential candidates, and administrators can manage all aspects of the platform. This facilitates career growth for students and gives colleges access to a diverse talent pool, enhancing their reputation and student outcomes.</p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Line, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import api from '@/services/api'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const stats = ref(null)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
  },
  scales: {
    y: {
      beginAtZero: true,
    },
  },
}

const placementChartData = computed(() => {
  if (!stats.value?.monthly_trends) return null
  
  return {
    labels: stats.value.monthly_trends.map(m => m.month),
    datasets: [
      {
        label: 'Placements',
        data: stats.value.monthly_trends.map(m => m.placements),
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.2)',
        fill: true,
        tension: 0.4,
      },
    ],
  }
})

const drivesChartData = computed(() => {
  if (!stats.value?.monthly_trends) return null
  
  return {
    labels: stats.value.monthly_trends.map(m => m.month),
    datasets: [
      {
        label: 'Drives',
        data: stats.value.monthly_trends.map(m => m.drives),
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
      },
      {
        label: 'Applications',
        data: stats.value.monthly_trends.map(m => m.applications),
        backgroundColor: 'rgba(255, 159, 64, 0.7)',
      },
    ],
  }
})

const fetchStats = async () => {
  try {
    const response = await api.get('/public/stats')
    stats.value = response.data
  } catch (err) {
    console.error('Failed to fetch stats:', err)
  }
}

onMounted(() => {
  fetchStats()
})
</script>
