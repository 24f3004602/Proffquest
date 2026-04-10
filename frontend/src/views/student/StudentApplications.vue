<template>
  <div class="student-shell">
    <div class="student-page-header">
      <div>
        <h1 class="student-eyebrow">My Applications</h1>
        <h2 class="student-title">Track Every Application</h2>
        <p class="page-subtitle">Stay updated with each drive you have applied for.</p>
        <!-- New: Export button -->
       
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
            <option value="Interview">Interview</option>
            <option value="Offer">Offer</option>
            <option value="Placed">Placed</option>
            <option value="Rejected">Rejected</option>
          </select>
           
        </div>
        <div class="export-app-btn">
        <button class="btn btn-primary" @click="handleExportAction" :disabled="exportLoading">
          {{ exportButtonText }}
        </button>
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
              <span class="status-badge status-interview">Interview</span>
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
import { formatDate, formatDateTime } from '@/utils/formatters'

export default {
  name: 'StudentApplications',
  data() {
    return {
      loading: true,
      error: null,
      applications: [],
      statusFilter: '',
      exportLoading: false
    }
  },
  computed: {
    filteredApplications() {
      if (!this.statusFilter) return this.applications
      return this.applications.filter(a => a.status === this.statusFilter)
    },
    interviewApps() {
      return this.applications.filter(a => a.interview_schedule && (a.status === 'Shortlisted' || a.status === 'Interview'))
    },
    exportButtonText() {
      if (this.exportLoading) return 'Downloading CSV...'
      return 'Download CSV'
    }
  },
  async mounted() {
    await this.fetchApplications()
  },
  methods: {
    formatDate,
    formatDateTime,
    async fetchApplications() {
      try {
        const { data } = await api.get('/student/applications')
        this.applications = data.applications
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load applications'
      } finally {
        this.loading = false
      }
    },
    _downloadBlob(response, fallbackName) {
      const blobUrl = window.URL.createObjectURL(new Blob([response.data]))
      const disposition = response.headers?.['content-disposition'] || ''
      const match = disposition.match(/filename="?([^";]+)"?/i)
      const filename = match ? match[1] : fallbackName

      const link = document.createElement('a')
      link.href = blobUrl
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(blobUrl)
    },
    async downloadExport() {
      this.exportLoading = true
      try {
        const response = await api.post('/student/exports', {}, { responseType: 'blob' })
        this._downloadBlob(response, `student_applications_${Date.now()}.csv`)
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to export applications'
      } finally {
        this.exportLoading = false
      }
    },
    async handleExportAction() {
      await this.downloadExport()
    }
  }
}
</script>
