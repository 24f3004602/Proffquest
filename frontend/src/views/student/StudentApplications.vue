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
        <button class="btn btn-primary" @click="exportApplications" :disabled="exportLoading || exportJob">
          {{ exportLoading ? 'Starting Export...' : exportJob ? 'Export in Progress...' : 'Export to CSV' }}
        </button>
        <!-- New: Export status and download -->
        <div v-if="exportJob" class="export-status">
          <p>Export Status: {{ exportJob.status }}</p>
          <p v-if="exportJob.error">Error: {{ exportJob.error }}</p>
          <a v-if="exportJob.status === 'completed' && exportJob.file_path" :href="downloadUrl" class="btn btn-success" download>Download CSV</a>
        </div>
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

export default {
  name: 'StudentApplications',
  data() {
    return {
      loading: true,
      error: null,
      applications: [],
      statusFilter: '',
      exportLoading: false,
      exportJob: null,
      exportInterval: null
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
    selectedApps() {
      return this.applications.filter(a => a.status === 'Selected')
    },
    downloadUrl() {
      return this.exportJob ? `${api.defaults.baseURL}/exports/student/download/${this.exportJob.id}` : ''
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
    },
    async exportApplications() {
      this.exportLoading = true
      try {
        const { data } = await api.post('/exports/student/applications')
        this.exportJob = { id: data.job_id, status: 'queued' }
        this.pollExportStatus()
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to start export'
      } finally {
        this.exportLoading = false
      }
    },
    async pollExportStatus() {
      this.exportInterval = setInterval(async () => {
        try {
          const { data } = await api.get('/exports/student/jobs')
          const job = data.jobs.find(j => j.id === this.exportJob.id)
          if (job) {
            this.exportJob = job
            if (job.status === 'completed' || job.status === 'failed') {
              clearInterval(this.exportInterval)
            }
          }
        } catch (err) {
          this.error = 'Failed to check export status'
          clearInterval(this.exportInterval)
        }
      }, 5000) // Poll every 5 seconds
    }
  },
  beforeUnmount() {
    if (this.exportInterval) clearInterval(this.exportInterval)
  }
}
</script>
