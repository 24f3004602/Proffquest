<template>
  <nav class="main-navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">
          <span class="brand-text">ProffQuest</span>
        </router-link>
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
        </div>
        <!-- Student Navigation -->
        <div v-else-if="userRole === 'student'" class="nav-menu">
          <router-link to="/student/dashboard" class="nav-link">Dashboard</router-link>
          <router-link to="/" class="nav-link">Home</router-link>
        </div>
        <!-- Company Navigation -->
        <div v-else-if="userRole === 'company'" class="nav-menu">
          <router-link to="/company/dashboard" class="nav-link">Dashboard</router-link>
          <router-link to="/" class="nav-link">Home</router-link>
        </div>
      </div>
      <!-- User Actions -->
      <div v-if="isLoggedIn" class="nav-actions">
        <span class="user-role">{{ getRoleDisplayName(userRole) }}</span>
        <button @click="logout" class="logout-btn">Logout</button>
      </div>
    </div>
  </nav>
</template>

<script>
import { authState } from '@/stores/auth'

export default {
  name: 'NavBar',
  computed: {
    isLoggedIn() {
      return authState.isLoggedIn
    },
    userRole() {
      return authState.role
    }
  },
  methods: {
    getRoleDisplayName(role) {
      switch (role) {
        case 'admin':
          return 'Admin'
        case 'student':
          return 'Student'
        case 'company':
          return 'Company'
        default:
          return ''
      }
    },
    logout() {
      authState.clearAuth()
      this.$router.push('/')
    }
  }
}
</script>

