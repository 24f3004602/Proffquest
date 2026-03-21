<template>
  <div class="drives-page">
    <div class="page-header">
      <div>
        <h1>Placement Drives</h1>
      </div>
            </div>

    <div v-if="loading" class="loading">Loading drives...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
    
      <div class="filter-section">
        <div class="filter-row">
          <div class="form-group">
            <label for="status-filter">Filter by Status:</label>
            <select v-model="statusFilter" id="status-filter">
              <option value="">All</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <button class="btn create-drive" @click="$router.push('/company/create-drive')">Create New Drive</button>
        </div>
      </div>

      <div v-if="filteredDrives.length === 0" class="no-data">No drives found.</div>
      <div v-else class="content-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>Drive</th>
              <th>Role</th>
              <th>Job Type</th>
              <th>Package</th>
              <th>Applicants</th>
              <th>Status</th>
              <th>Last Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="drive in filteredDrives" :key="drive.id">
              <td>
                <strong>{{ drive.job_title }}</strong>
                <div class="text-small">{{ drive.location }}</div>
              </td>
              <td>{{ drive.role || '-' }}</td>
              <td>{{ drive.job_type || 'Full-time' }}</td>
              <td>{{ drive.package_offered }}</td>
              <td>{{ drive.applicant_count }}</td>
              <td>
                <span :class="'status-badge status-' + drive.status">{{ drive.status }}</span>
              </td>
              <td>{{ formatDate(drive.application_deadline) }}</td>
              <td class="actions">
                <router-link 
                  v-if="drive.is_active && drive.status !== 'closed'"
                  :to="'/company/create-drive?edit=' + drive.id" 
                  class="action-btn"
                >
                  Edit
                </router-link>
                <button
                  v-if="drive.is_active"
                  @click="toggleDrive(drive)"
                  class="action-btn btn-reject"
                  :disabled="togglingId === drive.id"
                >
                  {{ togglingId === drive.id ? 'Updating...' : 'Close' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import { formatDate } from '@/utils/formatters'

export default {
  name: 'CompanyDrivesPage',
  data() {
    return {
      loading: true,
      error: null,
      drives: [],
      statusFilter: '',
      togglingId: null
    }
  },
  computed: {
    filteredDrives() {
      if (!this.statusFilter) return this.drives
      return this.drives.filter(d => d.status === this.statusFilter)
    }
  },
  async mounted() {
    await this.fetchDrives()
  },
  methods: {
    formatDate,
    async fetchDrives() {
      try {
        const { data } = await api.get('/company/drives')
        this.drives = data.drives
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load drives'
      } finally {
        this.loading = false
      }
    },
    async toggleDrive(drive) {
      this.togglingId = drive.id
      try {
        await api.put(`/company/drive/${drive.id}/status`, { is_active: false, status: 'closed' })
        drive.is_active = false
        drive.status = 'closed'
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to close drive')
      } finally {
        this.togglingId = null
      }
    }
  }
}
</script>
