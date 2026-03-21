<template>
  <div class="create-drive-page">
    <div class="page-header">
      <h1>{{ editing ? 'Edit Placement Drive' : 'Create Placement Drive' }}</h1>
      <router-link to="/company/dashboard" class="back-link">← Back to Dashboard</router-link>
    </div>

    <div class="card">
      <form @submit.prevent="createDrive">
        <div class="form-row">
          <div class="form-group">
            <label for="job_title">Job Title:</label>
            <input v-model="driveData.job_title" type="text" id="job_title" required>
          </div>
          <div class="form-group">
            <label for="role">Role:</label>
            <input v-model="driveData.role" type="text" id="role" placeholder="e.g., Software Developer">
          </div>
          <div class="form-group">
            <label for="package_offered">Package Offered:</label>
            <input v-model="driveData.package_offered" type="text" id="package_offered" required>
          </div>
          <div class="form-group">
            <label for="location">Location:</label>
            <input v-model="driveData.location" type="text" id="location" required>
          </div>
          <div class="form-group">
            <label for="job_type">Job Type:</label>
            <select v-model="driveData.job_type" id="job_type" required>
              <option value="Full-time">Full-time</option>
              <option value="Internship">Internship</option>
              <option value="Internship + PPO">Internship + PPO</option>
              <option value="Part-time">Part-time</option>
              <option value="Contract">Contract</option>
            </select>
          </div>
          <div class="form-group">
            <label for="max_applicants">Max Applicants (optional):</label>
            <input v-model.number="driveData.max_applicants" type="number" id="max_applicants" min="1">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="rounds">Number of Rounds:</label>
            <input v-model.number="driveData.rounds" type="number" id="rounds" min="1" placeholder="e.g., 3">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="application_deadline">Application Deadline:</label>
            <input v-model="driveData.application_deadline" type="datetime-local" id="application_deadline" required>
          </div>
          <div class="form-group">
            <label for="drive_date">Drive Date:</label>
            <input v-model="driveData.drive_date" type="datetime-local" id="drive_date" required>
          </div>
        </div>

        <div class="form-group">
          <label for="job_description">Job Description:</label>
          <textarea v-model="driveData.job_description" id="job_description" required rows="4"></textarea>
        </div>

        <div class="form-group">
          <label for="skills_required">Skills Required:</label>
          <input v-model="driveData.skills_required" type="text" id="skills_required" placeholder="e.g., Java, Python, SQL, REST APIs">
        </div>

        <div class="eligibility-section">
          <h3 v-if="driveData.eligibility.length > 0">Eligibility Criteria</h3>
          <div v-for="(el, index) in driveData.eligibility" :key="index" class="card eligibility-item">
            <div class="form-row">
              <div class="form-group">
                <label :for="'branch_' + index">Branch:</label>
                <input v-model="el.branch" type="text" :id="'branch_' + index" required>
              </div>
              <div class="form-group">
                <label :for="'min_cgpa_' + index">Min CGPA:</label>
                <input v-model.number="el.min_cgpa" type="number" step="0.1" min="0" max="10" :id="'min_cgpa_' + index" required>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label :for="'student_status_' + index">Student Status (optional):</label>
                <select v-model="el.student_status" :id="'student_status_' + index">
                  <option value="">Any</option>
                  <option value="studying">Studying</option>
                  <option value="passed">Passed</option>
                </select>
              </div>
              <div class="form-group">
                <label>Backlog Allowed</label>
                <button type="button" class="backlog1" :class="{ active: el.backlog_allowed === true }" @click="el.backlog_allowed = true">YES</button>
                <button type="button" class="backlog2" :class="{ active: el.backlog_allowed === false }" @click="el.backlog_allowed = false">NO</button>
              </div>
            </div>

            <div class="form-group">
              <label :for="'additional_' + index">Additional Criteria:</label>
              <textarea v-model="el.additional_criteria" :id="'additional_' + index" rows="2"></textarea>
            </div>

            <button type="button" @click="removeEligibility(index)" class="btn">Remove Criteria</button>
          </div>

          <button type="button" @click="addEligibility" class="btn">Add Eligibility Criteria</button>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn" :disabled="loading">
            {{ loading ? (editing ? 'Updating...' : 'Creating...') : (editing ? 'Update Drive' : 'Create Drive') }}
          </button>
          <button type="button" class="btn" @click="goToDashboard">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'CreateDrive',
  data() {
    return {
      loading: false,
      editing: false,
      editId: null,
      driveData: {
        job_title: '',
        role: '',
        job_description: '',
        package_offered: '',
        location: '',
        job_type: 'Full-time',
        skills_required: '',
        application_deadline: '',
        drive_date: '',
        max_applicants: null,
        rounds: null,
        eligibility: [{ branch: '', min_cgpa: 0.0, student_status: '', backlog_allowed: false, additional_criteria: '' }]
      }
    }
  },
  async mounted() {
    const editId = this.$route.query.edit
    if (editId) {
      this.editing = true
      this.editId = editId
      this.loading = true
      try {
        const { data } = await api.get(`/company/drive/${editId}`)
        this.driveData = { ...data.drive }
        // Ensure eligibility array has at least one entry
        if (!this.driveData.eligibility || this.driveData.eligibility.length === 0) {
          this.driveData.eligibility = [this.newEligibility()]
        }
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to load drive for editing')
      } finally {
        this.loading = false
      }
    }
  },
  methods: {
    newEligibility() {
      return { branch: '', min_cgpa: 0.0, student_status: '', backlog_allowed: false, additional_criteria: '' }
    },
    goToDashboard() { this.$router.push('/company/dashboard') },
    addEligibility() { this.driveData.eligibility.push(this.newEligibility()) },
    removeEligibility(index) {
      if (this.driveData.eligibility.length >= 1) {
        this.driveData.eligibility.splice(index, 1)
      }
    },
    async createDrive() {
      this.loading = true
      try {
        if (this.editing && this.editId) {
          await api.put(`/company/drive/${this.editId}`, this.driveData)
        } else {
          await api.post('/company/create_drive', this.driveData)
        }
        this.$router.push('/company/dashboard')
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to save drive')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>