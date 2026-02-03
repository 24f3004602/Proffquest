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
              <button v-if="!student.is_blacklisted" @click="blacklistStudent(student.id)" class="blacklist-btn">Blacklist</button>
              <button v-else @click="activateStudent(student.id)" class="activate-btn">Activate</button>
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
  name: 'AdminStudents',
  data() {
    return {
      students: [],
      searchQuery: '',
      filteredStudents: []
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
    }
  }
}
</script>

