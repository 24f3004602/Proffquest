<template>
  <nav class="main-navbar">
    <div class="nav-container">
      <div class="nav-top-row">
        <div class="nav-brand">
          <router-link to="/" class="brand-link">
            <span class="brand-text">ProffQuest</span>
          </router-link>
        </div>
        <button class="hamburger" :class="{ active: menuOpen }" @click="toggleMenu" aria-label="Toggle navigation">
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
        </button>
      </div>

      <div class="nav-links" :class="{ open: menuOpen }">
        <div v-if="!isLoggedIn" class="nav-menu">
          <router-link to="/" class="nav-link" @click="closeMenu">Home</router-link>
          <router-link to="/login" class="nav-link" @click="closeMenu">Login</router-link>
          <router-link to="/register" class="nav-link" @click="closeMenu">Register</router-link>
        </div>
        <!-- Admin Navigation -->
        <div v-else-if="userRole === 'admin'" class="nav-menu">
          <router-link to="/admin/dashboard" class="nav-link" @click="closeMenu">Dashboard</router-link>
          <router-link to="/admin/students" class="nav-link" @click="closeMenu">Students</router-link>
          <router-link to="/admin/companies" class="nav-link" @click="closeMenu">Companies</router-link>
          <router-link to="/admin/drives" class="nav-link" @click="closeMenu">Placement Drives</router-link>
          <router-link to="/admin/applications" class="nav-link" @click="closeMenu">Applications</router-link>
          <button class="nav-link nav-link-btn" @click="logout"> Logout</button>
        </div>
        <!-- Company Navigation -->
        <div v-else-if="userRole === 'company'" class="nav-menu">
          <router-link to="/company/dashboard" class="nav-link" @click="closeMenu">Dashboard</router-link>
          <router-link to="/company/drives" class="nav-link" @click="closeMenu">Placement Drives</router-link>
          <router-link to="/company/applications" class="nav-link" @click="closeMenu">Applications</router-link>
          <router-link to="/company/interviews" class="nav-link" @click="closeMenu">Interviews</router-link>
          <router-link to="/company/results" class="nav-link" @click="closeMenu">Results</router-link>
          <button class="nav-link nav-link-btn" @click="logout"> Logout</button>
        </div>
        <!-- Student Navigation -->
        <div v-else-if="userRole === 'student'" class="nav-menu">
          <router-link to="/student/dashboard" class="nav-link" @click="closeMenu"> Dashboard</router-link>
          <router-link to="/student/drives" class="nav-link" @click="closeMenu"> Placement Drives</router-link>
          <router-link to="/student/applications" class="nav-link" @click="closeMenu"> My Applications</router-link>
          <router-link to="/student/history" class="nav-link" @click="closeMenu"> Placement History</router-link>
          <router-link to="/student/profile" class="nav-link" @click="closeMenu"> My Profile</router-link>
          <button class="nav-link nav-link-btn" @click="logout"> Logout</button>
        </div>
      </div>
    </div>
  </nav>
  <!-- Overlay to close menu when clicking outside -->
  <div v-if="menuOpen" class="nav-overlay" @click="closeMenu"></div>
</template>

<script>
import { authState } from '@/stores/auth'

export default {
  name: 'NavBar',
  data() {
    return {
      menuOpen: false
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
  methods: {
    toggleMenu() {
      this.menuOpen = !this.menuOpen
    },
    closeMenu() {
      this.menuOpen = false
    },
    logout() {
      this.closeMenu()
      authState.clearAuth()
      this.$router.push('/')
    }
  }
}
</script>
