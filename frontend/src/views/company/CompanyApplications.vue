<template>
  <div class="applications-page">
    <div class="page-header">
      <h1>Manage Applications</h1>
      <router-link to="/company/dashboard" class="back-link">← Back to Dashboard</router-link>
    </div>

    <div v-if="loading" class="loading">Loading applications...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <!-- Drive Filter -->
      <div class="filter-section">
        <div class="form-group">
          <label for="drive-filter">Filter by Drive:</label>
          <select v-model="selectedDriveId" @change="filterApplications" id="drive-filter">
            <option value="">All Drives</option>
            <option v-for="drive in drives" :key="drive.id" :value="drive.id">
              {{ drive.job_title }}
            </option>
          </select>
        </div>
      </div>

      <!-- Applications List -->
      <div v-if="filteredApplications.length === 0" class="no-applications">
        No applications found.
      </div>
      <div v-else class="applications-list">
        <div v-for="application in filteredApplications" :key="application.application_id" class="card application-card">
          <div class="application-header">
            <h3>{{ application.student.full_name }}</h3>
            <span :class="'status-badge status-' + application.status.toLowerCase()">
              {{ application.status }}
            </span>
          </div>

          <div class="application-details">
            <div class="detail-row">
              <span><strong>Roll Number:</strong> {{ application.student.roll_number }}</span>
              <span><strong>College:</strong> {{ application.student.college }}</span>
            </div>
            <div class="detail-row">
              <span><strong>Branch:</strong> {{ application.student.branch }}</span>
              <span><strong>CGPA:</strong> {{ application.student.cgpa }}</span>
            </div>
            <div class="detail-row">
              <span><strong>Year:</strong> {{ application.student.year }}</span>
              <span><strong>Applied:</strong> {{ new Date(application.applied_at).toLocaleDateString() }}</span>
            </div>
            <div v-if="application.interview_schedule" class="detail-row">
              <span><strong>Interview:</strong> {{ new Date(application.interview_schedule).toLocaleString() }}</span>
            </div>
          </div>

          <div v-if="application.student.resume_url" class="resume-section">
            <a :href="application.student.resume_url" target="_blank" class="btn btn-secondary">View Resume</a>
          </div>

          <!-- Status Update Section -->
          <div class="status-update-section">
            <div class="form-group">
              <label>Update Status:</label>
              <select v-model="application.newStatus" @change="updateStatus(application)">
                <option value="Applied">Applied</option>
                <option value="Shortlisted">Shortlisted</option>
                <option value="Selected">Selected</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>

            <div v-if="application.newStatus === 'Shortlisted'" class="form-group">
              <button @click="scheduleInterview(application)" class="btn btn-secondary">Schedule Interview</button>
            </div>

            <div class="form-group">
              <label>Feedback/Notes:</label>
              <textarea v-model="application.feedback" @blur="updateFeedback(application)" rows="3" placeholder="Add feedback or notes..."></textarea>
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
  name: 'CompanyApplications',
  data() {
    return {
      loading: true,
      error: null,
      drives: [],
      applications: [],
      selectedDriveId: '',
      filteredApplications: []
    }
  },
  async mounted() {
    await this.fetchApplications()
    // Check for drive filter from query params
    const driveId = this.$route.query.drive
    if (driveId) {
      this.selectedDriveId = driveId
      this.filterApplications()
    }
  },
  methods: {
    async fetchApplications() {
      try {
        // First get company drives
        const dashboardResponse = await api.get('/company/dashboard')
        this.drives = dashboardResponse.data.drives

        // Get all applications for all drives
        const applicationsPromises = this.drives.map(drive =>
          api.get(`/company/drive/${drive.id}/applicants`)
        )

        const responses = await Promise.all(applicationsPromises)
        this.applications = responses.flatMap(response => response.data.applicants)

        // Initialize feedback and newStatus for each application
        this.applications = this.applications.map(app => ({
          ...app,
          newStatus: app.status,
          feedback: app.interview_notes || ''
        }))

        this.filteredApplications = [...this.applications]
        this.loading = false
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to load applications'
        this.loading = false
      }
    },
    filterApplications() {
      if (this.selectedDriveId) {
        this.filteredApplications = this.applications.filter(app => app.placement_drive.id === parseInt(this.selectedDriveId))
      } else {
        this.filteredApplications = [...this.applications]
      }
    },
    async updateStatus(application) {
      try {
        await api.put(`/company/application/${application.application_id}/status`, {
          status: application.newStatus,
          feedback: application.feedback
        })
        application.status = application.newStatus
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to update status')
        application.newStatus = application.status
      }
    },
    async updateFeedback(application) {
      try {
        await api.put(`/company/application/${application.application_id}/status`, {
          status: application.status,
          feedback: application.feedback
        })
      } catch (error) {
        alert('Failed to update feedback')
      }
    },
    scheduleInterview(application) {
      const date = prompt('Enter interview date and time (YYYY-MM-DDTHH:MM):')
      if (date) {
        try {
          api.put(`/company/application/${application.application_id}/status`, {
            status: application.status,
            feedback: application.feedback,
            interview_schedule: date
          })
          application.interview_schedule = date
        } catch (error) {
          alert('Failed to schedule interview')
        }
      }
    }
  }
}
</script>