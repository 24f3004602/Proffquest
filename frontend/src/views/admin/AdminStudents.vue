<template>
  <div class="admin-page">
    <div class="page-header">
      <h1>Student Management</h1>
      <router-link to="/admin/dashboard" class="back-link">← Back to Dashboard</router-link>
    </div>

    <div class="search-section">
      <input v-model="searchQuery" @input="searchStudents" type="text" placeholder="Search students by name, roll number, or email...">
    </div>

    <div class="content-section">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Full Name</th>
            <th>Roll Number</th>
            <th>Email</th>
            <th>College</th>
            <th>Branch</th>
            <th>CGPA</th>
            <th>Year</th>
            <th>Blacklisted</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in filteredStudents" :key="student.id">
            <td>{{ student.id }}</td>
            <td>{{ student.full_name }}</td>
            <td>{{ student.roll_number }}</td>
            <td>{{ student.email }}</td>
            <td>{{ student.college }}</td>
            <td>{{ student.branch }}</td>
            <td>{{ student.cgpa }}</td>
            <td>{{ student.year }}</td>
            <td>{{ student.is_blacklisted ? 'Yes' : 'No' }}</td>
            <td class="actions">
              <button @click="openProfile(student)" class="action-btn">View</button>
              <button v-if="!student.is_blacklisted" @click="blacklistStudent(student.id)" class="action-btn btn-blacklist">Blacklist</button>
              <button v-else @click="activateStudent(student.id)" class="action-btn btn-activate">Activate</button>
              <button @click="removeStudent(student.id)" class="action-btn">Remove</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="profileModal.visible" class="modal" @click.self="closeProfile">
      <div class="card modal-content">
        <h3>Student Profile</h3>
        <div v-if="profileModal.loading" class="loading">Loading profile...</div>
        <div v-else-if="profileModal.error" class="error-message">{{ profileModal.error }}</div>
        <div v-else>
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
        </div>
        <h4>Applications</h4>
        <div v-if="profileModal.appsLoading" class="loading">Loading applications...</div>
        <div v-else-if="profileModal.appsError" class="error-message">{{ profileModal.appsError }}</div>
        <div v-else-if="profileModal.applications.length === 0" class="no-data">No applications found.</div>
        <div v-else class="content-section">
          <table class="data-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Drive</th>
                <th>Status</th>
                <th>Applied</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in profileModal.applications" :key="app.application_id">
                <td>{{ app.company_name }}</td>
                <td>{{ app.job_title }}</td>
                <td><span :class="'status-badge status-' + app.status.toLowerCase()">{{ app.status }}</span></td>
                <td>{{ formatDate(app.applied_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="form-actions">
          <button class="btn btn-secondary" @click="closeProfile">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import { formatDate } from '@/utils/formatters'

export default {
  name: 'AdminStudents',
  data() {
    return {
      students: [],
      searchQuery: '',
      filteredStudents: [],
      profileModal: { visible: false, data: {}, loading: false, error: null, applications: [], appsLoading: false, appsError: null }
    }
  },
  async mounted() {
    await this.loadStudents()
  },
  methods: {
    async loadStudents() {
      try {
        const res = await api.get('/admin/student')
        const list = Array.isArray(res.data) ? res.data : (res.data?.students || [])
        this.students = list
        this.searchStudents()
      } catch (error) {
        console.error('Error loading students:', error)
      }
    },
    async removeStudent(studentId) {
      if (confirm('Are you sure you want to remove this student? This action cannot be undone.')) {
        try {
          await api.delete(`/admin/student/${studentId}`)
          await this.loadStudents()
        } catch (error) {
          console.error('Error removing student:', error)
        }
      }
    },
    searchStudents() {
      const query = this.searchQuery.trim().toLowerCase()
      if (!query) {
        this.filteredStudents = [...this.students]
        return
      }

      this.filteredStudents = this.students.filter(student => {
        const name = (student.full_name || '').toLowerCase()
        const roll = (student.roll_number || '').toLowerCase()
        const email = (student.email || '').toLowerCase()
        return name.includes(query) || roll.includes(query) || email.includes(query)
      })
    },
    async blacklistStudent(studentId) {
      if (confirm('Are you sure you want to blacklist this student?')) {
        try {
          await api.post(`/admin/blacklist_student/${studentId}`)
          await this.loadStudents()
        } catch (error) {
          console.error('Error blacklisting student:', error)
        }
      }
    },
    async activateStudent(studentId) {
      try {
        await api.post(`/admin/activate_student/${studentId}`)
        await this.loadStudents()
      } catch (error) {
        console.error('Error activating student:', error)
      }
    },
    async openProfile(student) {
      this.profileModal = { visible: true, data: {}, loading: true, error: null, applications: [], appsLoading: true, appsError: null }
      try {
        const [profileRes, appsRes] = await Promise.all([
          api.get(`/admin/student/${student.id}`),
          api.get(`/admin/student/${student.id}/applications`)
        ])
        this.profileModal.data = profileRes.data
        this.profileModal.applications = appsRes.data.applications || []
      } catch (error) {
        this.profileModal.error = error.response?.data?.message || 'Failed to load profile'
      } finally {
        this.profileModal.loading = false
        this.profileModal.appsLoading = false
      }
    },
    closeProfile() {
      this.profileModal = { visible: false, data: {}, loading: false, error: null, applications: [], appsLoading: false, appsError: null }
    },
    formatDate,
  }
}
</script>

