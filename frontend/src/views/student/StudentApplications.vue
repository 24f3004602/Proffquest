<template>
  <div class="student-shell">
    <div class="student-page-header">
      <div>
        <h1 class="student-eyebrow">My Applications</h1>
        <h2 class="student-title">Track Every Application</h2>
        <p class="page-subtitle">Stay updated with each drive you have applied for.</p>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading applications...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <div class="student-filter-app">
        <div class="filter-pill">
          <label for="status-filter">Status</label>
          <select v-model="statusFilter" id="status-filter">
            <option value="">All</option>
            <option value="Applied">Applied</option>
            <option value="Shortlisted">Shortlisted</option>
            <option value="Selected">Selected</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>
      </div>

      <div v-if="filteredApplications.length === 0" class="no-data">No applications found.</div>

      <div v-else class="content-section student-table-card">
        <table class="data-table student-table">
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Applied On</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in filteredApplications" :key="app.application_id">
              <td><strong>{{ app.company_name }}</strong></td>
              <td>{{ app.job_title }}</td>
              <td>{{ formatDate(app.applied_at) }}</td>
              <td>
                <span :class="'status-badge status-' + app.status.toLowerCase()">{{ app.status }}</span>
              </td>
              <td class="student-table-actions">
                <button class="btn btn-ghost" @click="viewApplication">View</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="interviewApps.length > 0" class="student-section">
        <div class="section-header">
          <h3>Scheduled Interviews</h3>
        </div>
        <div class="recent-list">
          <div v-for="app in interviewApps" :key="'int-' + app.application_id" class="card recent-item">
            <div class="recent-header">
              <h4>{{ app.job_title }}</h4>
              <span class="status-badge status-shortlisted">Interview</span>
            </div>
            <p><strong>Company:</strong> {{ app.company_name }}</p>
            <p><strong>Date:</strong> {{ formatDateTime(app.interview_schedule) }}</p>
            <p v-if="app.interview_notes"><strong>Notes:</strong> {{ app.interview_notes }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'StudentApplications',
  data() {
    return {
      loading: true,
      error: null,
      applications: [],
      statusFilter: ''
    }
  },
  computed: {
    filteredApplications() {
      if (!this.statusFilter) return this.applications
      return this.applications.filter(a => a.status === this.statusFilter)
    },
    interviewApps() {
      return this.applications.filter(a => a.interview_schedule && a.status === 'Shortlisted')
    },
    selectedApps() {
      return this.applications.filter(a => a.status === 'Selected')
    }
  },
  async mounted() {
    await this.fetchApplications()
  },
  methods: {
    formatDate(d) { return new Date(d).toLocaleDateString() },
    formatDateTime(d) { return new Date(d).toLocaleString() },
    viewApplication() {
      this.$router.push('/student/applications')
    },
    countByStatus(status) {
      return this.applications.filter(a => a.status === status).length
    },
    async fetchApplications() {
      try {
        const { data } = await api.get('/student/applications')
        this.applications = data.applications
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load applications'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
