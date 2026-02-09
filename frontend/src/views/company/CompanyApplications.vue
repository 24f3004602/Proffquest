<template>
  <div class="applications-page">
    <div class="page-header">
      <h1>Applications Management</h1>
    </div>

    <div v-if="loading" class="loading">Loading applications...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
    <div class="application-filter">
      <div class="filter-sec">
        <div class="form-group">
          <label for="drive-filter">Filter by Drive:</label>
          <select v-model="selectedDriveId" @change="filterApplications" id="drive-filter">
            <option value="">All Drives</option>
            <option v-for="drive in drives" :key="drive.id" :value="drive.id">
              {{ drive.job_title }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label for="status-filter">Filter by Status:</label>
          <select v-model="statusFilter" @change="filterApplications" id="status-filter">
            <option value="">All Status</option>
            <option value="Applied">Applied</option>
            <option value="Shortlisted">Shortlisted</option>
            <option value="Selected">Selected</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>
      </div>
    </div>
      <div v-if="filteredApplications.length === 0" class="no-data">No applications found.</div>
      <div v-else class="content-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Drive</th>
              <th>CGPA</th>
              <th>Status</th>
              <th>Applied</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="application in filteredApplications" :key="application.application_id">
              <td>
                <div>
                  <strong>{{ application.full_name }}</strong>
                  <div class="text-small">{{ application.branch }} | {{ application.roll_number }}</div>
                </div>
              </td>
              <td>{{ application.drive_title }}</td>
              <td>{{ application.cgpa }}</td>
              <td>
                <span :class="'status-badge status-' + application.status.toLowerCase()">{{ application.status }}</span>
              </td>
              <td>{{ formatDate(application.applied_at) }}</td>
              <td class="actions">
                <button class="action-btn" @click="openProfile(application)">View</button>
                <button class="action-btn btn-approve" @click="setStatus(application, 'Shortlisted')">Shortlist</button>
                <button class="action-btn btn-reject" @click="setStatus(application, 'Rejected')">Reject</button>
                <button class="action-btn" @click="setStatus(application, 'Selected')">Mark Selected</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Profile Modal -->
    <div v-if="profileModal.visible" class="modal" @click.self="closeProfile">
      <div class="card modal-content">
        <h3>Student Profile</h3>
        <p><strong>Name:</strong> {{ profileModal.data.full_name }}</p>
        <p><strong>Email:</strong> {{ profileModal.data.email }}</p>
        <p><strong>Roll Number:</strong> {{ profileModal.data.roll_number }}</p>
        <p><strong>College:</strong> {{ profileModal.data.college }}</p>
        <p><strong>Branch:</strong> {{ profileModal.data.branch }}</p>
        <p><strong>CGPA:</strong> {{ profileModal.data.cgpa }}</p>
        <p><strong>Year:</strong> {{ profileModal.data.year }}</p>
        <p><strong>Resume:</strong>
          <span v-if="profileModal.data.resume_url">
            <a :href="profileModal.data.resume_url" target="_blank">View Resume</a>
          </span>
          <span v-else>N/A</span>
        </p>
        <div class="form-actions">
          <button class="btn btn-secondary" @click="closeProfile">Close</button>
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
      statusFilter: '',
      filteredApplications: [],
      profileModal: { visible: false, data: {} }
    }
  },
  async mounted() {
    await this.fetchApplications()
    const driveId = this.$route.query.drive
    if (driveId) {
      this.selectedDriveId = driveId
      this.filterApplications()
    }
  },
  methods: {
    formatDate(d) { return new Date(d).toLocaleDateString() },
    filterApplications() {
      let list = this.applications
      if (this.selectedDriveId) {
        list = list.filter(app => app.drive_id === parseInt(this.selectedDriveId))
      }
      if (this.statusFilter) {
        list = list.filter(app => app.status === this.statusFilter)
      }
      this.filteredApplications = list
    },
    async fetchApplications() {
      try {
        const { data } = await api.get('/company/dashboard')
        this.drives = data.drives

        const responses = await Promise.all(
          this.drives.map(drive => api.get(`/company/drive/${drive.id}/applicants`))
        )
        this.applications = responses.flatMap((res, idx) =>
          res.data.applicants.map(a => ({
            ...a,
            drive_id: this.drives[idx].id,
            drive_title: this.drives[idx].job_title
          }))
        )

        this.filteredApplications = [...this.applications]
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load applications'
      } finally {
        this.loading = false
      }
    },
    async setStatus(application, status) {
      try {
        await api.put(`/company/application/${application.application_id}/status`, { status })
        application.status = status
        this.filterApplications()
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to update status')
      }
    },
    openProfile(application) {
      this.profileModal = { visible: true, data: application }
    },
    closeProfile() {
      this.profileModal = { visible: false, data: {} }
    }
  }
}
</script>
