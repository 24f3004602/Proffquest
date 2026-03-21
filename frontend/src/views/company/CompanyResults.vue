<template>
  <div class="results-page">
    <div class="page-header">
      <h1>Results</h1>
    </div>

    <div v-if="loading" class="loading">Loading results...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <div style="display:flex;justify-content:flex-end;margin-bottom:12px;">
        <button class="action-btn btn-approve" @click="downloadResultsCsv">Download CSV</button>
      </div>
      <div class="tab-row">
        <button class="tab-btn" :class="{ active: activeTab === 'Shortlisted' }" @click="activeTab = 'Shortlisted'">Shortlisted</button>
        <button class="tab-btn" :class="{ active: activeTab === 'Interview' }" @click="activeTab = 'Interview'">Interview</button>
        <button class="tab-btn" :class="{ active: activeTab === 'Offer' }" @click="activeTab = 'Offer'">Offer</button>
        <button class="tab-btn" :class="{ active: activeTab === 'Placed' }" @click="activeTab = 'Placed'">Placed</button>
        <button class="tab-btn" :class="{ active: activeTab === 'Rejected' }" @click="activeTab = 'Rejected'">Rejected</button>
      </div>
      <div v-if="filteredResults.length === 0" class="no-data">No results for this tab.</div>
      <div v-else class="content-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Drive</th>
              <th>Final Status</th>
              <th>Offer Sent</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredResults" :key="item.application_id">
              <td>
                <div>
                  <strong>{{ item.student.full_name }}</strong>
                  <div class="text-small">{{ item.student.roll_number }} | {{ item.student.branch }}</div>
                </div>
              </td>
              <td>
                <div>
                  <strong>{{ item.drive.job_title }}</strong>
                  <div class="text-small">{{ item.drive.package_offered }}</div>
                </div>
              </td>
              <td><span :class="'status-badge status-' + item.status.toLowerCase()">{{ item.status }}</span></td>
              <td>
                <span v-if="item.status === 'Offer' || item.status === 'Placed'">Yes</span>
                <span v-else>No</span>
              </td>
              <td class="actions">
                <button
                  v-for="action in getStatusActions(item.status)"
                  :key="`${item.application_id}-${action.status}`"
                  class="action-btn"
                  :class="action.type === 'reject' ? 'btn-reject' : 'btn-approve'"
                  @click="setStatus(item, action.status)"
                >
                  {{ action.label }}
                </button>
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
import { getStatusActions } from '@/utils/formatters'

export default {
  name: 'CompanyResults',
  data() {
    return {
      loading: true,
      error: null,
      results: [],
      activeTab: 'Offer'
    }
  },
  computed: {
    filteredResults() {
      return this.results.filter(r => r.status === this.activeTab)
    }
  },
  async mounted() {
    await this.fetchResults()
  },
  methods: {
    getStatusActions,
    async fetchResults() {
      try {
        const { data } = await api.get('/company/results')
        this.results = data.results
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load results'
      } finally {
        this.loading = false
      }
    },
    async setStatus(item, status) {
      try {
        await api.put(`/company/application/${item.application_id}/status`, { status })
        item.status = status
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to update status')
      }
    },
    async downloadResultsCsv() {
      try {
        const response = await api.get('/company/results/csv', { responseType: 'blob' })
        const blobUrl = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = blobUrl
        link.setAttribute('download', `company_results_${new Date().toISOString().slice(0, 10)}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(blobUrl)
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to download CSV'
      }
    }
  }
}
</script>
