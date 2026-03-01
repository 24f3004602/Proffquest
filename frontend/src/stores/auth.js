import { reactive } from 'vue'

export const authState = reactive({
  accessToken: localStorage.getItem('access_token') || null,
  userRole: localStorage.getItem('role') || null,

  get isLoggedIn() {
    return !!this.accessToken  
  },
  get role() {
    return this.userRole
  },
  setAuth(token, role) {
    this.accessToken = token
    this.userRole = role
    localStorage.setItem('access_token', token)
    localStorage.setItem('role', role)
  },
  clearAuth() {
    this.accessToken = null
    this.userRole = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('role')
  }
})