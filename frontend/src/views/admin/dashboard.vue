<template>
  <div class="admin-dashboard">

    <div class="dashboard-content">
      <div class="dashboard-header">
        <h1><i class="fas fa-tachometer-alt"></i> Admin Dashboard</h1>
        <p class="dashboard-subtitle">Manage your placement system efficiently</p>
      </div>

      <!-- Stats Section -->
      <div class="stats-section">
        <h2><i class="fas fa-chart-bar"></i> System Statistics</h2>
        <div class="stats-grid">
          <div v-for="item in statItems" :key="item.key" class="stat-card">
            <div class="stat-content">
              <h3>{{ item.label }}</h3>
              <p class="stat-number">{{ item.value }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <h2><i class="fas fa-chart-pie"></i> Data Visualization</h2>
        <div class="chart-container">
          <div class="chart-card">
            <h3><i class="fas fa-clipboard-list"></i> Applications by Status</h3>
            <div class="chart-placeholder-content">
              <div class="status-item">
                <span class="status-label">Applied:</span>
                <span class="status-value">{{ chartData.applied }}</span>
              </div>
              <div class="status-item">
                <span class="status-label">Shortlisted:</span>
                <span class="status-value">{{ chartData.shortlisted }}</span>
              </div>
              <div class="status-item">
                <span class="status-label">Interview:</span>
                <span class="status-value">{{ chartData.interview }}</span>
              </div>
              <div class="status-item">
                <span class="status-label">Offer:</span>
                <span class="status-value">{{ chartData.offer }}</span>
              </div>
              <div class="status-item">
                <span class="status-label">Placed:</span>
                <span class="status-value">{{ chartData.placed }}</span>
              </div>
              <div class="status-item">
                <span class="status-label">Selected (legacy):</span>
                <span class="status-value">{{ chartData.selected }}</span>
              </div>
              <div class="status-item">
                <span class="status-label">Rejected:</span>
                <span class="status-value">{{ chartData.rejected }}</span>
              </div>
            </div>
          </div>
          <div class="chart-card">
            <h3><i class="fas fa-building"></i> Companies by Status</h3>
            <div class="chart-placeholder-content">
              <div class="status-item">
                <span class="status-label">Approved:</span>
                <span class="status-value approved">{{ chartData.companiesApproved }}</span>
              </div>
              <div class="status-item">
                <span class="status-label">Pending:</span>
                <span class="status-value pending">{{ chartData.companiesPending }}</span>
              </div>
              <div class="status-item">
                <span class="status-label">Rejected:</span>
                <span class="status-value rejected">{{ chartData.companiesRejected }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <h2><i class="fas fa-bolt"></i> Quick Actions</h2>
        <div class="actions-grid">
          <router-link to="/admin/companies" class="action-card">
            <div >
              <i class="fas fa-building"></i>
            </div>
            <div class="action-content">
              <h3>Manage Companies</h3>
              <p>Approve, reject, or blacklist companies</p>
            </div>
            <i class="fas fa-arrow-right"></i>
          </router-link>
          <router-link to="/admin/students" class="action-card">
            <div >
              <i class="fas fa-user-graduate"></i>
            </div>
            <div class="action-content">
              <h3>Manage Students</h3>
              <p>View and manage student accounts</p>
            </div>
            <i class="fas fa-arrow-right"></i>
          </router-link>
          <router-link to="/admin/drives" class="action-card">
            <div >
              <i class="fas fa-calendar-alt"></i>
            </div>
            <div class="action-content">
              <h3>Manage Drives</h3>
              <p>Approve placement drives and job postings</p>
            </div>
            <i class="fas fa-arrow-right"></i>
          </router-link>
          <router-link to="/admin/applications" class="action-card">
            <div>
              <i class="fas fa-clipboard-check"></i>
            </div>
            <div class="action-content">
              <h3>View Applications</h3>
              <p>Monitor all student applications</p>
            </div>
            <i class="fas fa-arrow-right"></i>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import NavBar from '@/NavBar.vue'

export default {
  name: 'AdminDashboard',
  components: {
    NavBar
  },
  data() {
    return {
      stats: {},
      statMap: [
        { key: 'Total_Students', label: 'Total Students'},
        { key: 'Total_Companies', label: 'Total Companies'},
        { key: 'Total_Placement_drives', label: 'Total Drives'},
        { key: 'Total_applications', label: 'Total Applications'}
      ],
      chartData: {
        applied: 0,
        shortlisted: 0,
        interview: 0,
        offer: 0,
        placed: 0,
        selected: 0,
        rejected: 0,
        companiesApproved: 0,
        companiesPending: 0,
        companiesRejected: 0
      }
    }
  },
  async mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/login');
      return;
    }
    await this.loadStats()
    await this.loadChartData()
  },
  computed: {
    statItems() {
      // Build items with current values from stats
      return this.statMap.map(m => ({
        ...m,
        value: this.stats[m.key] ?? 0
      }))
    }
  },
  methods: {
    async loadStats() {
      try {
        const res = await api.get('/admin/dashboard_stats')
        this.stats = res.data
      } catch (error) {
        console.error('Error loading stats:', error)
        if (error.response && error.response.status === 422) {
          this.$router.push('/login')
        }
      }
    },

    async loadChartData() {
      try {
        // Load applications data for chart
        const appsRes = await api.get('/admin/applications')
        const applications = appsRes.data

        this.chartData.applied = applications.filter(app => app.status === 'Applied').length
        this.chartData.shortlisted = applications.filter(app => app.status === 'Shortlisted').length
        this.chartData.interview = applications.filter(app => app.status === 'Interview').length
        this.chartData.offer = applications.filter(app => app.status === 'Offer').length
        this.chartData.placed = applications.filter(app => app.status === 'Placed').length
        this.chartData.selected = applications.filter(app => app.status === 'Selected').length
        this.chartData.rejected = applications.filter(app => app.status === 'Rejected').length

        // Load companies data for chart
        const compRes = await api.get('/admin/companies')
        const companies = compRes.data

        this.chartData.companiesApproved = companies.filter(comp => comp.status === 'approved').length
        this.chartData.companiesPending = companies.filter(comp => comp.status === 'pending').length
        this.chartData.companiesRejected = companies.filter(comp => comp.status === 'rejected').length

      } catch (error) {
        console.error('Error loading chart data:', error)
        if (error.response && error.response.status === 422) {
          this.$router.push('/login')
        }
      }
    }
  }
}
</script>
