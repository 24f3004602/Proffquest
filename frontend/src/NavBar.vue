<template>
  <nav class="main-navbar">
    <div class="nav-container">
      <div class="nav-top-row">
        <div class="nav-brand">
          <router-link to="/" class="brand-link">
            <span class="brand-text">ProffQuest</span>
          </router-link>
        </div>
      </div>

      <div class="nav-links">
        <div v-if="!isLoggedIn" class="nav-menu">
          <router-link to="/" class="nav-link">Home</router-link>
          <router-link to="/login" class="nav-link">Login</router-link>
          <router-link to="/register" class="nav-link">Register</router-link>
        </div>
        <!-- Admin Navigation -->
        <div v-else-if="userRole === 'admin'" class="nav-menu">
          <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
          <router-link to="/admin/students" class="nav-link">Students</router-link>
          <router-link to="/admin/companies" class="nav-link">Companies</router-link>
          <router-link to="/admin/drives" class="nav-link">Placement Drives</router-link>
          <router-link to="/admin/applications" class="nav-link">Applications</router-link>
          <button class="nav-link nav-link-btn" @click="logout"> Logout</button>
        </div>
        <!-- Company Navigation -->
        <div v-else-if="userRole === 'company'" class="nav-menu">
          <router-link to="/company/dashboard" class="nav-link">Dashboard</router-link>
          <router-link to="/company/drives" class="nav-link">Placement Drives</router-link>
          <router-link to="/company/applications" class="nav-link">Applications</router-link>
          <router-link to="/company/interviews" class="nav-link">Interviews</router-link>
          <router-link to="/company/results" class="nav-link">Results</router-link>
          <button class="nav-link nav-link-btn" @click="logout"> Logout</button>
        </div>
        <!-- Student Navigation -->
        <div v-else-if="userRole === 'student'" class="nav-menu">
          <router-link to="/student/dashboard" class="nav-link"> Dashboard</router-link>
          <router-link to="/student/drives" class="nav-link"> Placement Drives</router-link>
          <router-link to="/student/applications" class="nav-link"> My Applications</router-link>
          <router-link to="/student/history" class="nav-link"> Placement History</router-link>
          <router-link to="/student/profile" class="nav-link"> My Profile</router-link>
          <button class="nav-link nav-link-btn" @click="logout"> Logout</button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import api from '@/services/api'
import { authState } from '@/stores/auth'

export default {
  name: 'NavBar',
  data() {
    return {
      companyName: '',
      studentSearch: '',
      showProfileMenu: false
    }
  },
  computed: {
    isLoggedIn() {
      return authState.isLoggedIn
    },
    userRole() {
      return authState.role
    }
  },
  watch: {
    userRole: {
      immediate: true,
      handler(newRole) {
        if (newRole === 'company' && this.isLoggedIn) {
          this.fetchCompanyProfile()
        }
      }
    },
    $route() {
      this.showProfileMenu = false
    }
  },
  methods: {
    logout() {
      authState.clearAuth()
      this.companyName = ''
      this.showProfileMenu = false
      this.$router.push('/')
    },
    toggleProfileMenu() {
      this.showProfileMenu = !this.showProfileMenu
    },
    async fetchCompanyProfile() {
      try {
        const { data } = await api.get('/company/profile')
        this.companyName = data.company_name
      } catch {
        this.companyName = ''
      }
    }
  }
}
</script>
