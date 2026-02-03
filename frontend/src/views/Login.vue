<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="card">
        <div class="auth-header">
          <h2>Sign In</h2>
          <p>Welcome back! Please sign in to your account.</p>
        </div>

        <form @submit.prevent="login" class="login-form">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="Enter your email"
              required
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="Enter your password"
              required
            />
          </div>

          <button type="submit" class="login-btn" :disabled="loading">
            <span v-if="loading">Signing In...</span>
            <span v-else>Sign In</span>
          </button>
        </form>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div class="login-footer">
          <router-link to="/register" class="register-link">
            Don't have an account? <strong>Register here</strong>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import { authState } from '@/stores/auth'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      errorMessage: '',
      loading: false
    }
  },
  methods: {
    async login() {
      this.loading = true
      this.errorMessage = ''

      try {
        const response = await api.post('/login', {
          email: this.email,
          password: this.password
        })

        const access_token = response.data.access_token
        const payload = JSON.parse(atob(access_token.split('.')[1]))
        const sub = JSON.parse(payload.sub)
        const role = sub.role

        authState.setAuth(access_token, role)

        if (role === 'admin') {
          this.$router.push('/admin/dashboard')
        } else if (role === 'student') {
          this.$router.push('/student/dashboard')
        } else if (role === 'company') {
          this.$router.push('/company/dashboard')
        }
      } catch (error) {
        if (error.response && error.response.data && error.response.data.message) {
          this.errorMessage = error.response.data.message
        } else {
          this.errorMessage = 'Login failed. Please try again.'
        }
        console.error('Login error:', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
