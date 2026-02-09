<template>
  <div class="student-shell">
    <div class="student-page-header">
      <div>
        <h1 class="student-eyebrow">Placement History</h1>
        <h2 class="student-title">Your Placement Journey</h2>
        <p class="page-subtitle">Track outcomes across internships and full-time roles.</p>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading placement history...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <div v-if="historyRows.length === 0" class="no-data">No placement history yet.</div>
      <div v-else class="content-section student-table-card">
        <table class="data-table student-table">
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Year</th>
              <th>Result</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in historyRows" :key="row.application_id">
              <td><strong>{{ row.company_name }}</strong></td>
              <td>{{ row.job_title }}</td>
              <td>{{ formatYear(row.selected_at || row.applied_at) }}</td>
              <td>
                <span :class="'status-badge status-' + row.status.toLowerCase()">{{ row.status }}</span>
              </td>
              <td class="student-table-actions">
                <button class="btn btn-ghost" @click="viewDetails(row)">View Details</button>
                <a
                  v-if="row.offer_letter_url"
                  :href="row.offer_letter_url"
                  class="btn"
                  target="_blank"
                >Download Offer</a>
                <button v-else class="btn btn-ghost" disabled>Offer Letter</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'StudentHistory',
  data() {
    return {
      loading: true,
      error: null,
      applications: []
    }
  },
  computed: {
    historyRows() {
      return this.applications.filter(a => a.status === 'Offer' || a.status === 'Placed' || a.status === 'Selected' || a.status === 'Rejected')
    }
  },
  async mounted() {
    await this.fetchHistory()
  },
  methods: {
    formatYear(d) {
      if (!d) return '—'
      return new Date(d).getFullYear()
    },
    viewDetails() {
      this.$router.push('/student/applications')
    },
    async fetchHistory() {
      try {
        const { data } = await api.get('/student/applications')
        this.applications = data.applications
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load placement history'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
