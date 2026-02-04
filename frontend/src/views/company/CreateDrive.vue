<template>
  <div class="create-drive-page">
    <div class="page-header">
      <h1>Create Placement Drive</h1>
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
            <label for="package_offered">Package Offered:</label>
            <input v-model="driveData.package_offered" type="text" id="package_offered" required>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="location">Location:</label>
            <input v-model="driveData.location" type="text" id="location" required>
          </div>
          <div class="form-group">
            <label for="max_applicants">Max Applicants (optional):</label>
            <input v-model="driveData.max_applicants" type="number" id="max_applicants">
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

        <div class="eligibility-section">
          <h3 v-if="driveData.eligibility.length>0">Eligibility Criteria</h3>
          <div v-for="(el, index) in driveData.eligibility" :key="index" class="card eligibility-item">
            <div class="form-row">
              <div class="form-group">
                <label :for="'branch_' + index">Branch:</label>
                <input v-model="el.branch" type="text" :id="'branch_' + index" required>
              </div>
              <div class="form-group">
                <label :for="'min_cgpa_' + index">Min CGPA:</label>
                <input v-model="el.min_cgpa" type="number" step="0.1" :id="'min_cgpa_' + index" required>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label :for="'passing_year_' + index">Passing Year:</label>
                <input v-model="el.passing_year" type="number" :id="'passing_year_' + index">
              </div>
              <div class="form-group">
                <label> Backlog Allowed</label>
                  <button type="button" class="backlog1" :class="{active:el.backlog_allowed===true}" @click="el.backlog_allowed=true">YES</button>
                  <button type="button" class="backlog2" :class="{active:el.backlog_allowed===false}" @click="el.backlog_allowed=false">NO</button>
              </div>
            </div>

            <div class="form-group">
              <label :for="'additional_' + index">Additional Criteria:</label>
              <textarea v-model="el.additional_criteria" :id="'additional_' + index" rows="2"></textarea>
            </div>

            <button type="button" @click="removeEligibility(index)" class="btn ">Remove Criteria</button>
          </div>

          <button type="button" @click="addEligibility" class="btn">Add Eligibility Criteria</button>
        </div>

        <div class="form-actions">
          <button type="submit"  class="btn" :disabled="loading">
            {{ loading ? 'Creating...' : 'Create Drive' }}
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
      driveData: {
        job_title: '',
        job_description: '',
        package_offered: '',
        location: '',
        application_deadline: '',
        drive_date: '',
        max_applicants: null,
        eligibility: [
          {
            branch: '',
            min_cgpa: 0.0,
            passing_year: null,
            backlog_allowed: false,
            additional_criteria: ''
          }
        ]
      }
    }
  },
  methods: {
    goToDashboard(){
        this.$router.push('/company/dashboard')
    },
    addEligibility() {
      this.driveData.eligibility.push({
        branch: '',
        min_cgpa: 0.0,
        passing_year: null,
        backlog_allowed: false,
        additional_criteria: ''
      })
    },
    removeEligibility(index) {
      if (this.driveData.eligibility.length>=1) {
        this.driveData.eligibility.splice(index, 1)
        }
      },
    async createDrive() {
      this.loading = true
      console.log('Creating drive with data:', this.driveData)
      try {
        const response = await api.post('/company/create_drive', this.driveData)
        console.log('Drive created successfully:', response.data)
        this.$router.push('/company/dashboard')
      } catch (error) {
        console.error('Error creating drive:', error)
        alert(error.response?.data?.message || 'Failed to create drive')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>