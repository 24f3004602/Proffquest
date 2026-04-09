<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>Company Dashboard</h1>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <!-- Top Summary Cards -->
       <div>
        <h2>Welcome, {{ company.company_name }}</h2>
        <p class="company-info">
          <h4><strong>HR Name:</strong> {{ company.hr_name }}</h4> 
          <h4><strong>Email:</strong> {{ company.email }}  </h4>
          <h4><strong>Website:</strong> <a :href="company.website" target="_blank" rel="noopener noreferrer">{{ company.website }}</a> <br></h4>
        </p>
       </div>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalDrives }}</div>
            <div class="stat-label">Total Placement Drives</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalApplications }}</div>
            <div class="stat-label">Total Applicants</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.shortlisted }}</div>
            <div class="stat-label">Shortlisted</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.interview }}</div>
            <div class="stat-label">Interviews</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.offer }}</div>
            <div class="stat-label">Offers</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.placed }}</div>
            <div class="stat-label">Placed</div>
          </div>
        </div>
      </div>

      <div class="dashboard-row">
        <!-- Recent Placement Drives -->
        <div class="content-section">
          <div class="section-header">
            <h3>Recent Placement Drives</h3>
          </div>
          <div v-if="recentDrives.length === 0" class="no-data">No drives created yet.</div>
          <div v-else class="scroll-area">
            <table class="recent-items data-table">
              <thead>
                <tr>
                  <th>Drive Name</th>
                  <th>Role</th>
                  <th>Applicants</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in recentDrives" :key="drive.id">
                  <td>{{ drive.job_title }}</td>
                  <td>{{ drive.role || '-' }}</td>
                  <td>{{ drive.applicant_count }}</td>
                  <td>
                    <span :class="'status-badge status-' + drive.status">{{ drive.status }}</span>
                  </td>
                  <td class="actions">
                    <router-link :to="'/company/applications?drive=' + drive.id" class="action-btn">View</router-link>
                    <router-link 
                      v-if="drive.is_active && drive.status !== 'closed'"
                      :to="'/company/create-drive?edit=' + drive.id" 
                      class="action-btn"
                    >
                      Edit
                    </router-link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <button class="btn btn-primary" @click="$router.push('/company/drives')">View All Drives</button>
        </div>

        <!-- Applicants per Drive Bar Chart -->
        <div class="content-section">
          <div class="section-header">
            <h3>Applicants per Drive</h3>
          </div>
          <div v-if="drives.length === 0" class="no-data">No data available.</div>
          <div v-else class="bar-chart scroll-area">
            <div v-for="drive in drives" :key="'bar-' + drive.id" class="bar-row">
              <div class="bar-label">{{ drive.job_title }}</div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: barWidth(drive) }"></div>
              </div>
              <div class="bar-value">{{ drive.applicant_count }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="content-section dashboard-full">
        <!-- Upcoming Interviews -->
        <div class="section-header">
          <h3>Upcoming Interviews</h3>
        </div>
        <div v-if="upcomingInterviews.length === 0" class="no-data">No upcoming interviews.</div>
        <div v-else class="recent-list scroll-area">
          <div v-for="item in upcomingInterviews" :key="item.application_id" class="recent-item compact">
            <div class="recent-header">
              <h4>{{ item.student.full_name }}</h4>
              <span class="status-badge status-shortlisted">Interview</span>
            </div>
            <p><strong>Drive:</strong> {{ item.drive.job_title }}</p>
            <p><strong>Schedule:</strong> {{ formatDateTime(item.interview_schedule) }}</p>
          </div>
        </div>
        <button class="btn btn-secondary" @click="$router.push('/company/interviews')">View All Interviews</button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import { formatDateTime } from '@/utils/formatters'

export default {
  name: 'CompanyDashboard',
  data() {
    return {
      loading: true,
      error: null,
      company: {},
      drives: [],
      stats: { totalDrives: 0, totalApplications: 0, shortlisted: 0, interview: 0, offer: 0, placed: 0 },
      upcomingInterviews: []
    }
  },
  computed: {
    recentDrives() {
      return this.drives.slice(0, 5)
    },
    maxApplicants() {
      if (this.drives.length === 0) return 0
      return Math.max(...this.drives.map(d => d.applicant_count || 0))
    }
  },
  async mounted() {
    await this.fetchDashboard()
    await this.fetchInterviews()
  },
  methods: {
    formatDateTime,
    barWidth(drive) {
      if (!this.maxApplicants) return '0%'
      const percent = Math.round((drive.applicant_count / this.maxApplicants) * 100)
      return `${percent}%`
    },
    async fetchDashboard() {
      try {
        const { data } = await api.get('/company/dashboard')
        this.company = data.company
        this.drives = data.drives
        this.stats = data.stats
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load dashboard'
      } finally {
        this.loading = false
      }
    },
    async fetchInterviews() {
      try {
        const { data } = await api.get('/company/interviews')
        this.upcomingInterviews = (data.interviews || []).filter(i => i.interview_schedule).slice(0, 5)
      } catch (err) {
        this.upcomingInterviews = []
      }
    }
  }
}
</script>
