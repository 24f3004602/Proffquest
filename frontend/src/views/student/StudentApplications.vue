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
        <button class="btn btn-primary" @click="handleExportAction" :disabled="exportLoading || isExportInProgress">
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
      exportLoading: false,
      exportJob: null,
      exportInterval: null,
      autoDownloadPending: false
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
    isExportInProgress() {
      return this.exportJob && this.exportJob.status !== 'completed' && this.exportJob.status !== 'failed'
    },
    exportButtonText() {
      if (this.exportLoading) return 'Starting Download...'
      if (this.isExportInProgress) return 'Preparing CSV...'
      if (this.exportJob && this.exportJob.status === 'completed' && this.exportJob.file_path) return 'Download CSV'
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
    async exportApplications() {
      this.exportLoading = true
      try {
        this.autoDownloadPending = true
        const { data } = await api.post('/student/exports')
        this.exportJob = {
          id: data.job_id,
          status: data.status || 'queued',
          file_path: data.file_path || null,
          error: data.error || null
        }

        if (this.exportJob.status === 'completed' && this.exportJob.file_path) {
          await this.downloadExport()
          this.autoDownloadPending = false
        } else if (this.exportJob.status !== 'failed') {
          this.pollExportStatus()
        } else {
          this.autoDownloadPending = false
        }
      } catch (err) {
        this.autoDownloadPending = false
        this.error = err.response?.data?.message || 'Failed to start export'
      } finally {
        this.exportLoading = false
      }
    },
    async handleExportAction() {
      if (this.exportJob && this.exportJob.status === 'completed' && this.exportJob.file_path) {
        await this.downloadExport()
        return
      }
      await this.exportApplications()
    },
    async pollExportStatus() {
      if (this.exportInterval) clearInterval(this.exportInterval)
      this.exportInterval = setInterval(async () => {
        try {
          const { data } = await api.get('/student/exports/jobs')
          const job = data.jobs.find(j => j.id === this.exportJob.id)
          if (job) {
            this.exportJob = job
            if (job.status === 'completed' || job.status === 'failed') {
              clearInterval(this.exportInterval)
              this.exportInterval = null
              if (job.status === 'completed' && job.file_path && this.autoDownloadPending) {
                await this.downloadExport()
              }
              this.autoDownloadPending = false
            }
          }
        } catch (err) {
          this.autoDownloadPending = false
          this.error = 'Failed to check export status'
          clearInterval(this.exportInterval)
          this.exportInterval = null
        }
      }, 5000) // Poll every 5 seconds
    },
    async downloadExport() {
      if (!this.exportJob) return
      try {
        const response = await api.get(`/student/exports/${this.exportJob.id}/download`, {
          responseType: 'blob'
        })

        const blobUrl = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = blobUrl
        link.setAttribute('download', `student_applications_${this.exportJob.id}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(blobUrl)
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to download export file'
      }
    }
  },
  beforeUnmount() {
    if (this.exportInterval) clearInterval(this.exportInterval)
  }
}
</script>
