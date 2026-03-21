<template>
  <div class="student-shell">
    <div class="student-page-header">
      <div>
        <h1 class="student-eyebrow">Placement Drives</h1>
        <h2 class="student-title">Discover Your Next Role</h2>
        <p class="page-subtitle">Browse and apply for approved placement drives.</p>
      </div>
      <div class="student-search-bar">
        <span class="search-icon">Search</span>
        <input v-model="searchQuery" type="text" placeholder="Search by company or role...">
      </div>
    </div>

    <div v-if="loading" class="loading">Loading drives...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <div class="student-filter-row">
        <div class="filter-pill">
          <label for="cgpa-filter">CGPA</label>
          <input v-model.number="cgpaFilter" type="number" id="cgpa-filter" step="0.1" min="0" max="10" placeholder="7.0">
        </div>
        <div class="filter-pill">
          <label for="branch-filter">Branch</label>
          <select v-model="branchFilter" id="branch-filter">
            <option value="">All</option>
            <option v-for="branch in uniqueBranches" :key="branch" :value="branch">{{ branch }}</option>
          </select>
        </div>
        <div class="filter-pill">
          <label for="applied-filter">Applied</label>
          <select v-model="appliedFilter" id="applied-filter">
            <option value="">All</option>
            <option value="applied">Applied</option>
            <option value="not-applied">Not Applied</option>
          </select>
        </div>
        <div class="filter-pill">
          <label for="deadline-filter">Deadline</label>
          <select v-model="deadlineFilter" id="deadline-filter">
            <option value="">All</option>
            <option value="open">Open</option>
            <option value="closed">Closed</option>
          </select>
        </div>
      </div>

      <div v-if="filteredDrives.length === 0" class="no-data">No drives found matching your criteria.</div>

      <div v-else class="student-drive-grid">
        <div v-for="drive in filteredDrives" :key="drive.id" class="student-drive-card">
          <div class="drive-card-top">
            <div class="drive-company">
              <div class="drive-logo">{{ drive.company_name?.charAt(0) || 'C' }}</div>
              <div>
                <p class="drive-company-name">{{ drive.company_name }}</p>
                <p class="drive-role">{{ drive.job_title }}</p>
              </div>
            </div>
            <div class="drive-badges">
              <span class="status-badge" :class="getDriveStatusClass(drive)">{{ getDriveStatusLabel(drive) }}</span>
              <span v-if="!isProfileComplete" class="status-badge status-rejected">Profile Incomplete</span>
            </div>
          </div>

          <div class="drive-meta">
            <span>Role: {{ drive.role || drive.job_title }}</span>
            <span>CTC / Stipend: {{ drive.package_offered }}</span>
            <span>Job Type: {{ drive.job_type || 'Full-time' }}</span>
            <span>Location: {{ drive.location }}</span>
            <span>Deadline: {{ formatDate(drive.application_deadline) }}</span>
          </div>

          <div class="drive-description" v-if="expandedDrive === drive.id">
            <p><strong>Description:</strong> {{ drive.job_description }}</p>
            <p v-if="drive.skills_required"><strong>Skills Required:</strong> {{ drive.skills_required }}</p>
            <div  class="eligibility-info">
              <p><strong>Eligibility Criteria:</strong></p>
              <ul>
                <li v-for="(el, idx) in drive.eligibility" :key="idx">
                  Branch: {{ el.branch }} | Min CGPA: {{ el.min_cgpa }}
                  <span v-if="el.additional_criteria"> | {{ el.additional_criteria }}</span>
                </li>
              </ul>
            </div>
          </div>

          <div class="drive-actions">
            <button @click="toggleExpand(drive.id)" class="btn btn-ghost">
              {{ expandedDrive === drive.id ? 'Show Less' : 'View Details' }}
            </button>
            <button
              v-if="drive.already_applied"
              class="btn btn-ghost"
              disabled
            >
              Applied
            </button>
            <button
              v-else
              @click="applyToDrive(drive)"
              class="btn"
              :disabled="drive.applying || !canApply(drive)"
              :title="applyDisabledReason(drive)"
            >
              {{ drive.applying ? 'Applying...' : 'Apply Now' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import { formatDate, driveStatusLabel, driveStatusClass } from '@/utils/formatters'

export default {
  name: 'StudentDrives',
  data() {
    return {
      loading: true,
      error: null,
      drives: [],
      profile: {},
      searchQuery: '',
      cgpaFilter: '',
      branchFilter: '',
      appliedFilter: '',
      deadlineFilter: '',
      expandedDrive: null
    }
  },
  computed: {
    isProfileComplete() {
      const requiredFields = ['full_name', 'email', 'roll_number', 'branch', 'cgpa', 'year', 'resume_url']
      return requiredFields.every(key => this.profile && this.profile[key])
    },
    filteredDrives() {
      let list = this.drives
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase()
        list = list.filter(d =>
          d.job_title.toLowerCase().includes(q) ||
          d.company_name.toLowerCase().includes(q)
        )
      }
      if (this.cgpaFilter) {
        const cgpa = Number(this.cgpaFilter)
        list = list.filter(d => this.meetsCgpaFilter(d, cgpa))
      }
      if (this.branchFilter) {
        list = list.filter(d => this.matchesBranchFilter(d, this.branchFilter))
      }
      if (this.appliedFilter === 'applied') {
        list = list.filter(d => d.already_applied)
      } else if (this.appliedFilter === 'not-applied') {
        list = list.filter(d => !d.already_applied)
      }
      if (this.deadlineFilter === 'open') {
        list = list.filter(d => !d.deadline_passed)
      } else if (this.deadlineFilter === 'closed') {
        list = list.filter(d => d.deadline_passed)
      }
      return list
    },
    uniqueBranches() {
      const branches = new Set()
      this.drives.forEach(d => {
        d.eligibility?.forEach(el => {
          if (el.branch) branches.add(el.branch)
        })
      })
      return Array.from(branches)
    }
  },
  watch: {
    '$route.query.q': {
      immediate: true,
      handler(value) {
        if (typeof value === 'string') {
          this.searchQuery = value
        }
      }
    }
  },
  async mounted() {
    await Promise.all([this.fetchDrives(), this.fetchProfile()])
  },
  methods: {
    formatDate,
    toggleExpand(driveId) {
      this.expandedDrive = this.expandedDrive === driveId ? null : driveId
    },
    meetsCgpaFilter(drive, cgpa) {
      if (!drive.eligibility || drive.eligibility.length === 0) return true
      return drive.eligibility.some(el => (el.min_cgpa || 0) <= cgpa)
    },
    matchesBranchFilter(drive, branch) {
      if (!drive.eligibility || drive.eligibility.length === 0) return true
      return drive.eligibility.some(el => el.branch === branch)
    },
    getDriveStatusLabel: driveStatusLabel,
    getDriveStatusClass: driveStatusClass,
    canApply(drive) {
      return this.isProfileComplete && !drive.deadline_passed && !drive.already_applied
    },
    applyDisabledReason(drive) {
      if (!this.isProfileComplete) return 'Complete your profile before applying'
      if (drive.deadline_passed) return 'Deadline passed'
      if (drive.already_applied) return 'Already applied'
      return ''
    },
    async fetchProfile() {
      try {
        const { data } = await api.get('/student/profile')
        this.profile = data || {}
      } catch {
        this.profile = {}
      }
    },
    async fetchDrives() {
      try {
        const { data } = await api.get('/student/drives')
        this.drives = data.drives.map(d => ({ ...d, applying: false }))
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load drives'
      } finally {
        this.loading = false
      }
    },
    async applyToDrive(drive) {
      if (!confirm(`Apply to "${drive.job_title}" at ${drive.company_name}?`)) return
      drive.applying = true
      try {
        await api.post(`/student/apply/${drive.id}`)
        drive.already_applied = true
        alert('Application submitted successfully!')
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to apply')
      } finally {
        drive.applying = false
      }
    }
  }
}
</script>
