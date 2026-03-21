<template>
  <div class="profile-page">
    <div class="page-header">
      <h1>Company Profile</h1>
    </div>

    <div v-if="loading" class="loading">Loading profile...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <div class="card">
        <div class="profile-header">
          <div class="profile-avatar">{{ companyInitial }}</div>
          <div>
            <h2>{{ profile.company_name }}</h2>
            <p class="text-muted">{{ profile.website }}</p>
          </div>
          <span :class="'status-badge status-' + profile.status">{{ profile.status }}</span>
        </div>

        <div v-if="!editing" class="profile-details">
          <div class="detail-row"><span class="detail-label">Email:</span> {{ profile.email }}</div>
          <div class="detail-row"><span class="detail-label">HR Contact:</span> {{ profile.hr_name }}</div>
          <div class="detail-row"><span class="detail-label">Location:</span> {{ profile.address || 'N/A' }}</div>
          <div class="detail-row">
            <span class="detail-label">Description:</span>
            <span>{{ profile.description || 'N/A' }}</span>
          </div>

          <div class="form-actions">
            <button class="btn" @click="startEdit">Edit Profile</button>
            <button
              v-if="profile.status !== 'approved'"
              class="btn btn-secondary"
              @click="submitForApproval"
              :disabled="submitting"
            >
              {{ submitting ? 'Submitting...' : 'Submit for Approval' }}
            </button>
          </div>
        </div>

        <div v-else class="profile-edit">
          <h3>Edit Profile</h3>
          <form @submit.prevent="saveProfile">
            <div class="form-row">
              <div class="form-group">
                <label for="company_name">Company Name</label>
                <input v-model="editData.company_name" id="company_name" type="text" required>
              </div>
              <div class="form-group">
                <label for="hr_name">HR Contact</label>
                <input v-model="editData.hr_name" id="hr_name" type="text" required>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="website">Website</label>
                <input v-model="editData.website" id="website" type="url" required>
              </div>
              <div class="form-group">
                <label for="address">Location</label>
                <input v-model="editData.address" id="address" type="text">
              </div>
            </div>
            <div class="form-group">
              <label for="description">Description</label>
              <textarea v-model="editData.description" id="description" rows="4"></textarea>
            </div>
            <div class="form-actions">
              <button type="submit" class="btn" :disabled="saving">{{ saving ? 'Saving...' : 'Save' }}</button>
              <button type="button" class="btn btn-secondary" @click="cancelEdit">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'CompanyProfile',
  data() {
    return {
      loading: true,
      error: null,
      profile: {},
      editing: false,
      saving: false,
      submitting: false,
      editData: {}
    }
  },
  computed: {
    companyInitial() {
      return this.profile.company_name ? this.profile.company_name.charAt(0).toUpperCase() : 'C'
    }
  },
  async mounted() {
    await this.fetchProfile()
  },
  methods: {
    async fetchProfile() {
      try {
        const { data } = await api.get('/company/profile')
        this.profile = data
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load profile'
      } finally {
        this.loading = false
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
        await api.put('/company/profile', {
          company_name: this.editData.company_name,
          hr_name: this.editData.hr_name,
          website: this.editData.website,
          address: this.editData.address,
          description: this.editData.description
        })
        this.profile = { ...this.profile, ...this.editData }
        this.editing = false
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to update profile')
      } finally {
        this.saving = false
      }
    },
    async submitForApproval() {
      this.submitting = true
      try {
        await api.post('/company/profile/submit')
        this.profile.status = 'pending'
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to submit for approval')
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>
