<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>Company Dashboard</h1>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="card company-info">
        <h2>{{ company.company_name }}</h2>
        <p><strong>HR:</strong> {{ company.hr_name }}</p>
        <p><strong>Website:</strong> <a :href="company.website" target="_blank">{{ company.website }}</a></p>
        <p><strong>Description:</strong> {{ company.description }}</p>
        <p><strong>Address:</strong> {{ company.address }}</p>
      </div>

      <!-- Dashboard Statistics -->
      <div class="stats-section">
        <h3>Overview</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ stats.totalDrives }}</div>
              <div class="stat-label">Placement Drives</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ stats.totalApplications }}</div>
              <div class="stat-label">Total Applications</div>
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
              <div class="stat-number">{{ stats.selected }}</div>
              <div class="stat-label">Selected</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Applications -->
      <div class="recent-section">
        <div class="section-header">
          <h3>Recent Applications</h3>
        </div>
        <div v-if="recentApplications.length === 0" class="no-data">
          No recent applications.
        </div>
        <div v-else class="recent-list">
          <div v-for="app in recentApplications" :key="app.application_id" class="card recent-item">
            <div class="recent-header">
              <h4>{{ app.student.full_name }}</h4>
              <span :class="'status-badge status-' + app.status.toLowerCase()">{{ app.status }}</span>
            </div>
            <p><strong>Applied for:</strong> {{ app.placement_drive.job_title }}</p>
            <p><strong>Applied on:</strong> {{ new Date(app.applied_at).toLocaleDateString() }}</p>
            <div v-if="app.interview_schedule" class="interview-info">
              <p><strong>Interview:</strong> {{ new Date(app.interview_schedule).toLocaleString() }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Drives -->
      <div class="drives-section">
        <div class="section-header">
          <h3>Your Placement Drives</h3>
        </div>
        <div class="no-data">
        <div v-if="drives.length === 0" class="no-drives">
          No placement drives created yet.
        </div>
        <div v-else class="drives-list">
          <div v-for="drive in drives" :key="drive.id" class="card drive-card">
            <h4>{{ drive.job_title }}</h4>

            <p><strong>Package:</strong> {{ drive.package_offered }}</p>
            <p><strong>Location:</strong> {{ drive.location }}</p>
            <p><strong>Status:</strong> {{ drive.status }}</p>
            <p><strong>Active:</strong> {{ drive.is_active ? 'Yes' : 'No' }}</p>
            <p><strong>Applicants:</strong> {{ drive.applicant_count }}</p>
            <p><strong>Deadline:</strong> {{ new Date(drive.application_deadline).toLocaleDateString() }}</p>
            <p><strong>Drive Date:</strong> {{ new Date(drive.drive_date).toLocaleDateString() }}</p>
            <div class="drive-actions">
              <button @click="gotoApplications()" class="btn btn-secondary">View applicants</button>
              <button @click="toggleDriveStatus(drive)" class="btn btn-secondary">
                {{ drive.is_active ? 'Close Drive' : 'Open Drive' }}
              </button>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'CompanyDashboard',
  data() {
    return {
      loading: true,
      error: null,
      company: {},
      drives: [],
      stats: {
        totalDrives: 0,
        totalApplications: 0,
        shortlisted: 0,
        selected: 0
      },
      recentApplications: []
    }
  },
  async mounted() {
    await this.fetchDashboard()
  },
  methods: {
    gotoApplications(){
        this.$router.push('/company/applications')
    },
    async fetchDashboard() {
      try {
        const response = await api.get('/company/dashboard')
        this.company = response.data.company
        this.drives = response.data.drives
        this.stats = response.data.stats
        this.recentApplications = response.data.recentApplications
        this.loading = false
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to load dashboard'
        this.loading = false
      }
    },
    async toggleDriveStatus(drive) {
      try {
        await api.put(`/company/drive/${drive.id}/status`, {
          is_active: !drive.is_active
        })
        drive.is_active = !drive.is_active
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to update drive status')
      }
    }
  }
}
</script>
