<template>
  <div class="student-shell">
    <div class="student-page-header">
      <div>
        <h1 class="student-eyebrow">My Profile</h1>
        <h2 class="student-title">Showcase Your Strengths</h2>
        <p class="page-subtitle">Keep your profile updated to unlock more drives.</p>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading profile...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else class="profile-grid">
      <div class="card profile-main">
        <div v-if="!editing" class="profile-view">
          <div class="profile-header">
            <div>
              <h2>{{ profile.full_name }}</h2>
              <p class="text-muted">{{ profile.branch }} • CGPA {{ profile.cgpa }}</p>
            </div>
            <span v-if="profile.is_blacklisted" class="status-badge status-rejected">Blacklisted</span>
          </div>

          <div class="profile-section">
            <h3>Personal Info</h3>
            <div class="profile-details">
              <div class="detail-row"><span class="detail-label">Email:</span> {{ profile.email }}</div>
              <div class="detail-row"><span class="detail-label">Roll No:</span> {{ profile.roll_number || 'Not set' }}</div>
              <div class="detail-row"><span class="detail-label">Phone:</span> {{ profile.phone || 'Not set' }}</div>
            </div>
          </div>

          <div class="profile-section">
            <h3>Academic Details</h3>
            <div class="profile-details">
              <div class="detail-row"><span class="detail-label">College:</span> {{ profile.college }}</div>
              <div class="detail-row"><span class="detail-label">Branch:</span> {{ profile.branch }}</div>
              <div class="detail-row"><span class="detail-label">Year:</span> {{ profile.year }}</div>
            </div>
          </div>

          <div class="profile-section">
            <h3>Resume</h3>
            <div class="profile-details">
              <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span v-if="profile.resume_url">Uploaded</span>
                <span v-else class="text-muted">Not uploaded</span>
              </div>
            </div>
          </div>
          <button @click="startEdit" class="btn">Edit Profile</button>
        </div>

        <div v-else class="profile-edit">
          <h3>Edit Profile</h3>
          <form @submit.prevent="saveProfile">
            <div class="form-row">
              <div class="form-group">
                <label for="full_name">Full Name:</label>
                <input v-model="editData.full_name" type="text" id="full_name" required>
              </div>
              <div class="form-group">
                <label for="roll_number">Roll Number:</label>
                <input v-model="editData.roll_number" type="text" id="roll_number">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="college">College:</label>
                <input v-model="editData.college" type="text" id="college" required>
              </div>
              <div class="form-group">
                <label for="branch">Branch:</label>
                <input v-model="editData.branch" type="text" id="branch" required>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="cgpa">CGPA:</label>
                <input v-model.number="editData.cgpa" type="number" id="cgpa" step="0.01" min="0" max="10" required>
              </div>
              <div class="form-group">
                <label for="year">Year:</label>
                <input v-model.number="editData.year" type="number" id="year" min="1" max="4" required>
              </div>
            </div>
            <div class="form-group">
              <label for="resume_url">Resume URL:</label>
              <input v-model="editData.resume_url" type="url" id="resume_url" placeholder="https://drive.google.com/your-resume">
            </div>
            <div class="form-actions">
              <button type="submit" class="btn" :disabled="saving">
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
              <button type="button" class="btn btn-secondary" @click="cancelEdit">Cancel</button>
            </div>
          </form>
        </div>
      </div>

      <aside class="profile-side">
        <div class="card student-side-card">
          <div class="side-card-header">
            <h4>Profile Completion</h4>
            <span class="side-card-metric">{{ profileCompletion }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: profileCompletion + '%' }"></div>
          </div>
          <p class="text-small">Complete your profile to unlock more drives.</p>
        </div>

        <div class="card student-side-profile">
          <h4>Quick Actions</h4>
          <button class="btn1" @click="$router.push('/student/drives')">Browse Drives</button>
          <button class="btn2" @click="$router.push('/student/applications')">View Applications</button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'StudentProfile',
  data() {
    return {
      loading: true,
      error: null,
      profile: {},
      editing: false,
      saving: false,
      editData: {},
      historyLoading: true,
      historyError: null,
      applications: []
    }
  },
  computed: {
    profileCompletion() {
      const fields = ['full_name', 'email', 'roll_number', 'branch', 'cgpa', 'year', 'resume_url']
      const filled = fields.filter(key => this.profile && this.profile[key]).length
      return Math.round((filled / fields.length) * 100)
    }
  },
  async mounted() {
    await this.fetchProfile()
    await this.fetchHistory()
  },
  methods: {
    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString()
    },
    async fetchProfile() {
      try {
        const { data } = await api.get('/student/profile')
        this.profile = data
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load profile'
      } finally {
        this.loading = false
      }
    },
    async fetchHistory() {
      this.historyLoading = true
      try {
        const { data } = await api.get('/student/applications')
        this.applications = (data.applications || []).map(app => ({
          ...app,
          last_update: app.placed_at || app.offer_at || app.interview_at || app.shortlisted_at || app.selected_at || app.applied_at
        }))
      } catch (err) {
        this.historyError = err.response?.data?.message || 'Failed to load history'
      } finally {
        this.historyLoading = false
      }
    },
    startEdit() {
      this.editData = { ...this.profile }
      this.editing = true
    },
    cancelEdit() {
      this.editing = false
      this.editData = {}
    },
    async saveProfile() {
      this.saving = true
      try {
        await api.put('/student/profile', {
          full_name: this.editData.full_name,
          roll_number: this.editData.roll_number,
          college: this.editData.college,
          branch: this.editData.branch,
          cgpa: this.editData.cgpa,
          year: this.editData.year,
          resume_url: this.editData.resume_url
        })
        this.profile = { ...this.profile, ...this.editData }
        this.editing = false
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to update profile')
      } finally {
        this.saving = false
      }
    }
  }
}
</script>
