<template>
  <div class="admin-page">
    <div class="page-header">
      <h1>Placement Drives Management</h1>
      <router-link to="/admin/dashboard" class="back-link">← Back to Dashboard</router-link>
    </div>

    <div class="content-section">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Company</th>
            <th>Job Title</th>
            <th>Package</th>
            <th>Location</th>
            <th>Application Deadline</th>
            <th>Drive Date</th>
            <th>Status</th>
            <th>Approved</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="drive in placementDrives" :key="drive.id">
            <td>{{ drive.id }}</td>
            <td>{{ drive.company_name }}</td>
            <td>{{ drive.job_title }}</td>
            <td>{{ drive.package_offered }}</td>
            <td>{{ drive.location }}</td>
            <td>{{ drive.application_deadline ? new Date(drive.application_deadline).toLocaleDateString() : 'N/A' }}</td>
            <td>{{ drive.drive_date ? new Date(drive.drive_date).toLocaleDateString() : 'N/A' }}</td>
            <td>{{ drive.status }}</td>
            <td>{{ drive.is_approved ? 'Yes' : 'No' }}</td>
            <td class="actions">
              <button v-if="drive.status === 'pending'" @click="approveDrive(drive.id)" class="action-btn btn-approve">Approve</button>
              <button v-if="drive.status === 'pending'" @click="rejectDrive(drive.id)" class="action-btn btn-reject">Reject</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'AdminDrives',
  data() {
    return {
      placementDrives: []
    }
  },
  async mounted() {
    await this.loadPlacementDrives()
  },
  methods: {
    async loadPlacementDrives() {
      try {
        const res = await api.get('/admin/placement_drives')
        this.placementDrives = res.data
      } catch (error) {
        console.error('Error loading placement drives:', error)
      }
    },
    async approveDrive(driveId) {
      try {
        await api.post(`/admin/approve_drive/${driveId}`)
        await this.loadPlacementDrives()
      } catch (error) {
        console.error('Error approving drive:', error)
      }
    },
    async rejectDrive(driveId) {
      try {
        await api.post(`/admin/reject_drive/${driveId}`)
        await this.loadPlacementDrives()
      } catch (error) {
        console.error('Error rejecting drive:', error)
      }
    }
  }
}
</script>

