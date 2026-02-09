<template>
  <div class="student-shell">
    <div class="student-hero">
      <div>
        <h1 class="student-eyebrow">Dashboard</h1>
        <h2 class="student-title">Welcome back, {{ student.full_name}}.</h2>
        <p class="student-subtitle">Track your applications, stay on top of deadlines, and apply faster.</p>
        <div class="student-hero-actions">
          <button class="btn" @click="$router.push('/student/drives')">Browse Drives</button>
          <button class="btn" @click="$router.push('/student/profile')">Update Profile</button>
        </div>
      </div>
      <div class="student-hero-card">
        <p class="hero-card-title">Placement Info</p>
        <div class="hero-card-metric">{{ stats.shortlisted + stats.offer + stats.placed }}</div>
        <p class="hero-card-subtitle">Shortlisted + Offers</p>
        <div class="hero-card-meta">
          <span>{{ stats.total_applied }} total applications</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading dashboard...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else class="student-grid">
      <section class="student-main">
        <div class="student-stat-grid">
          <div class="student-stat-card">
            <p class="stat-label">Applied Drives</p>
            <h3 class="stat-number">{{ stats.total_applied }}</h3>
            <span class="stat-chip warning">In Progress</span>
          </div>
          <div class="student-stat-card">
            <p class="stat-label">Shortlisted</p>
            <h3 class="stat-number">{{ stats.shortlisted }}</h3>
            <span class="stat-chip info">Interview Ready</span>
          </div>
          <div class="student-stat-card">
            <p class="stat-label">Interviews</p>
            <h3 class="stat-number">{{ stats.interview }}</h3>
            <span class="stat-chip">Scheduled</span>
          </div>
          <div class="student-stat-card">
            <p class="stat-label">Offers</p>
            <h3 class="stat-number">{{ stats.offer }}</h3>
            <span class="stat-chip success">Offer</span>
          </div>
          <div class="student-stat-card">
            <p class="stat-label">Placed</p>
            <h3 class="stat-number">{{ stats.placed }}</h3>
            <span class="stat-chip success">Placed</span>
          </div>
        </div>

        <div class="student-section">
          <div class="section-header">
            <h3>Recommended / Latest Drives</h3>
            <button class="btn" @click="$router.push('/student/drives')">View All</button>
          </div>
          <div v-if="recommendedDrives.length === 0" class="no-data">No upcoming drives at the moment.</div>
          <div v-else class="student-drive-grid">
            <div v-for="drive in recommendedDrives" :key="drive.id" class="student-drive-card">
              <div class="drive-card-top">
                <div class="drive-company">
                  <div class="drive-logo">{{ drive.company_name?.charAt(0) || 'C' }}</div>
                  <div>
                    <p class="drive-company-name">{{ drive.company_name }}</p>
                    <p class="drive-role">{{ drive.job_title }}</p>
                  </div>
                </div>
                <span class="status-badge" :class="driveStatusClass(drive)">{{ driveStatusLabel(drive) }}</span>
              </div>
              <div class="drive-meta">
                <span>CTC / Stipend: {{ drive.package_offered }}</span>
                <span>Eligibility: {{ eligibilitySummary(drive) }}</span>
                <span>Deadline: {{ formatDate(drive.application_deadline) }}</span>
              </div>
              <div class="drive-actions">
                <button class="btn" @click="$router.push('/student/drives')">Apply Now</button>
                <button class="btn" @click="$router.push('/student/drives')">View Details</button>
              </div>
            </div>
          </div>
        </div>

        <div class="student-section">
          <div class="section-header">
            <h3>Recent Applications</h3>
            <button class="btn" @click="$router.push('/student/applications')">View All</button>
          </div>
          <div v-if="recentApplications.length === 0" class="no-data">No applications yet.</div>
          <div v-else class="recent-list">
            <div v-for="app in recentApplications" :key="app.application_id" class="card recent-item">
              <div class="recent-header">
                <h4>{{ app.job_title }}</h4>
                <span :class="'status-badge status-' + app.status.toLowerCase()">{{ app.status }}</span>
              </div>
              <p><strong>Company:</strong> {{ app.company_name }}</p>
              <p><strong>Applied:</strong> {{ formatDate(app.applied_at) }}</p>
            </div>
          </div>
        </div>
      </section>

      <aside class="student-side">
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
        <div class="card student-side-alert">
          <div class="side-card-header">
            <h4>Alerts</h4>
          </div>
          <ul class="alert-list">
          <div class="alert-items">
            <div class="alert-items-text">
            <li v-if="!resumeUploaded">Upload your Resume to Enhance your profile.</li>
            <li v-if="recommendedDrives.length > 0">New drive from {{ recommendedDrives[0].company_name }} opened.</li>
            <li v-if="upcomingInterviews.length > 0">Interview schedule updated for {{ upcomingInterviews[0].company_name }}.</li>
            </div>
          </div>
          </ul>
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'StudentDashboard',
  data() {
    return {
      loading: true,
      error: null,
      student: {},
      profile:{},
      stats: { total_applied: 0, shortlisted: 0, interview: 0, offer: 0, placed: 0, rejected: 0 },
      upcomingInterviews: [],
      recentApplications: [],
      upcomingDrives: []
    }
  },
  computed: {
    profileData() {
      return Object.keys(this.profile || {}).length ? this.profile : this.student
    },
    profileCompletion() {
      const fields = ['full_name', 'email', 'roll_number', 'branch', 'cgpa', 'year', 'resume_url']
      const filled = fields.filter(key => this.profileData && this.profileData[key]).length
      return Math.round((filled / fields.length) * 100)
    },
    resumeUploaded() {
      return !!this.profileData?.resume_url
    },
    recommendedDrives() {
      return this.upcomingDrives.slice(0, 4)
    }
  },
  async mounted() {
    await this.fetchDashboard()
  },
  methods: {
    formatDate(d) { return new Date(d).toLocaleDateString() },
    eligibilitySummary(drive) {
      if (!drive.eligibility || drive.eligibility.length === 0) return 'Open to all'
      const minCgpa = Math.min(...drive.eligibility.map(el => el.min_cgpa || 0))
      const branches = drive.eligibility.map(el => el.branch).filter(Boolean)
      const branchText = branches.length ? branches.slice(0, 2).join(', ') : 'All branches'
      return `CGPA ${minCgpa}+ • ${branchText}`
    },
    driveStatusLabel(drive) {
      if (drive.deadline_passed) return 'Closed'
      if (drive.already_applied) return 'Applied'
      return 'Not Applied'
    },
    driveStatusClass(drive) {
      if (drive.deadline_passed) return 'status-closed'
      if (drive.already_applied) return 'status-applied'
      return 'status-pending'
    },
    async fetchDashboard() {
      try {
        const { data } = await api.get('/student/dashboard')
        this.student = data.student
        this.stats = data.stats
        this.upcomingInterviews = data.upcoming_interviews
        this.recentApplications = data.recent_applications
        this.upcomingDrives = data.upcoming_drives
        try {
          const profileRes = await api.get('/student/profile')
          this.profile = profileRes.data
        } catch {
          this.profile = {}
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load dashboard'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
