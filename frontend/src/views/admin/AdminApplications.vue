<template>
  <div class="admin-page">
    <div class="page-header">
      <h1>Applications Management</h1>
      <router-link to="/admin/dashboard" class="back-link">← Back to Dashboard</router-link>
    </div>

    <div class="content-section">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Student Name</th>
            <th>Roll Number</th>
            <th>Company</th>
            <th>Job Title</th>
            <th>Status</th>
            <th>Applied At</th>
            <th>Shortlisted At</th>
            <th>Selected At</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in applications" :key="app.id">
            <td>{{ app.id }}</td>
            <td>{{ app.student_name }}</td>
            <td>{{ app.student_roll }}</td>
            <td>{{ app.company_name }}</td>
            <td>{{ app.job_title }}</td>
            <td>
              <span :class="getStatusClass(app.status)">{{ app.status }}</span>
            </td>
            <td>{{ app.applied_at ? new Date(app.applied_at).toLocaleDateString() : 'N/A' }}</td>
            <td>{{ app.shortlisted_at ? new Date(app.shortlisted_at).toLocaleDateString() : 'N/A' }}</td>
            <td>{{ app.selected_at ? new Date(app.selected_at).toLocaleDateString() : 'N/A' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'AdminApplications',
  data() {
    return {
      applications: []
    }
  },
  async mounted() {
    await this.loadApplications()
  },
  methods: {
    async loadApplications() {
      try {
        const res = await api.get('/admin/applications')
        this.applications = res.data
      } catch (error) {
        console.error('Error loading applications:', error)
      }
    },
    getStatusClass(status) {
      switch (status) {
        case 'Applied':
          return 'status-applied'
        case 'Shortlisted':
          return 'status-shortlisted'
        case 'Selected':
          return 'status-selected'
        case 'Rejected':
          return 'status-rejected'
        default:
          return 'status-default'
      }
    }
  }
}
</script>

