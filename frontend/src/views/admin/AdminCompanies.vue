<template>
  <div class="admin-page">
    <div class="page-header">
      <h1>Company Management</h1>
      <router-link to="/admin/dashboard" class="back-link">← Back to Dashboard</router-link>
    </div>

    <div class="search-section">
      <input v-model="searchQuery" @input="searchCompanies" type="text" placeholder="Search companies by name, email, or description...">
    </div>

    <div class="content-section">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Company Name</th>
            <th>HR Name</th>
            <th>Email</th>
            <th>Website</th>
            <th>Status</th>
            <th>Blacklisted</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="company in filteredCompanies" :key="company.id">
            <td>{{ company.id }}</td>
            <td>{{ company.company_name }}</td>
            <td>{{ company.hr_name }}</td>
            <td>{{ company.email }}</td>
            <td><a :href="company.website" target="_blank" rel="noopener noreferrer">{{ company.website }}</a></td>
            <td>{{ company.status }}</td>
            <td>{{ company.is_blacklisted ? 'Yes' : 'No' }}</td>
            <td class="actions">
              <button v-if="company.status === 'pending'" @click="approveCompany(company.id)" class="action-btn btn-approve">Approve</button>
              <button v-if="company.status === 'pending'" @click="rejectCompany(company.id)" class="action-btn btn-reject">Reject</button>
              <button v-if="!company.is_blacklisted" @click="blacklistCompany(company.id)" class="blacklist-btn">Blacklist</button>
              <button v-else @click="activateCompany(company.id)" class="activate-btn">Activate</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'AdminCompanies',
  data() {
    return {
      companies: [],
      searchQuery: '',
      filteredCompanies: []
    }
  },
  async mounted() {
    await this.loadCompanies()
  },
  methods: {
    async loadCompanies() {
      try {
        const res = await api.get('/admin/companies')
        this.companies = res.data
        this.filteredCompanies = res.data
      } catch (error) {
        console.error('Error loading companies:', error)
      }
    },
    async searchCompanies() {
      if (this.searchQuery.trim() === '') {
        this.filteredCompanies = this.companies
      } else {
        try {
          const res = await api.get(`/admin/search_companies?q=${encodeURIComponent(this.searchQuery)}`)
          this.filteredCompanies = res.data
        } catch (error) {
          console.error('Error searching companies:', error)
        }
      }
    },
    async approveCompany(companyId) {
      try {
        await api.post(`/admin/approve_company/${companyId}`)
        await this.loadCompanies()
      } catch (error) {
        console.error('Error approving company:', error)
      }
    },
    async rejectCompany(companyId) {
      try {
        await api.post(`/admin/cancel_company/${companyId}`)
        await this.loadCompanies()
      } catch (error) {
        console.error('Error rejecting company:', error)
      }
    },
    async blacklistCompany(companyId) {
      if (confirm('Are you sure you want to blacklist this company?')) {
        try {
          await api.post(`/admin/blacklist_company/${companyId}`)
          await this.loadCompanies()
        } catch (error) {
          console.error('Error blacklisting company:', error)
        }
      }
    },
    async activateCompany(companyId) {
      try {
        await api.post(`/admin/activate_company/${companyId}`)
        await this.loadCompanies()
      } catch (error) {
        console.error('Error activating company:', error)
      }
    }
  }
}
</script>

