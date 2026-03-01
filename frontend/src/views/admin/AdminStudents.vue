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
              <button v-if="!student.is_blacklisted" @click="blacklistStudent(student.id)" class="blacklist-btn">Blacklist</button>
              <button v-else @click="activateStudent(student.id)" class="activate-btn">Activate</button>
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
        const res = await api.get('/admin/search_students')
        this.students = res.data
        this.filteredStudents = res.data
      } catch (error) {
        console.error('Error loading students:', error)
      }
    },
    async searchStudents() {
      if (this.searchQuery.trim() === '') {
        this.filteredStudents = this.students
      } else {
        try {
          const res = await api.get(`/admin/search_students?q=${encodeURIComponent(this.searchQuery)}`)
          this.filteredStudents = res.data
        } catch (error) {
          console.error('Error searching students:', error)
        }
      }
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
    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString()
    }
  }
}
</script>

