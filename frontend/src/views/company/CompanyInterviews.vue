<template>
  <div class="interviews-page">
    <div class="page-header">
      <h1>Interviews</h1>
    </div>

    <div v-if="loading" class="loading">Loading interviews...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ interviews.length }}</div>
            <div class="stat-label">Total Shortlisted</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ scheduledCount }}</div>
            <div class="stat-label">Interviews Scheduled</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ pendingCount }}</div>
            <div class="stat-label">Pending Schedule</div>
          </div>
        </div>
      </div>

      <!-- Filter -->
       <div class="interview-filter">
            <div class="filter-sec">
        <div class="form-group">
          <label for="drive-filter">Filter by Drive:</label>
          <select v-model="selectedDrive" id="drive-filter">
            <option value="">All Drives</option>
            <option v-for="d in uniqueDrives" :key="d.id" :value="d.id">{{ d.job_title }}</option>
          </select>
        </div>
        <div class="form-group">
          <label for="schedule-filter">Filter by Schedule:</label>
          <select v-model="scheduleFilter" id="schedule-filter">
            <option value="">All</option>
            <option value="scheduled">Scheduled</option>
            <option value="unscheduled">Not Scheduled</option>
          </select>
        </div>
            </div>
      </div>

      <div v-if="filteredInterviews.length === 0" class="no-data">No shortlisted students found.</div>

      <!-- Interviews Table -->
      <div v-else class="content-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Roll No</th>
              <th>Branch</th>
              <th>CGPA</th>
              <th>Drive</th>
              <th>Interview Date</th>
              <th>Mode</th>
              <th>Link / Venue</th>
              <th>Notes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredInterviews" :key="item.application_id">
              <td>
                <div>
                  <strong>{{ item.student.full_name }}</strong>
                  <div class="text-small">{{ item.student.email }}</div>
                </div>
              </td>
              <td>{{ item.student.roll_number }}</td>
              <td>{{ item.student.branch }}</td>
              <td>{{ item.student.cgpa }}</td>
              <td>
                <div>
                  <strong>{{ item.drive.job_title }}</strong>
                  <div class="text-small">{{ item.drive.package_offered }}</div>
                </div>
              </td>
              <td>
                <span v-if="item.interview_schedule">{{ formatDateTime(item.interview_schedule) }}</span>
                <span v-else class="text-muted">Not scheduled</span>
              </td>
              <td>{{ item.interview_mode || 'N/A' }}</td>
              <td>{{ item.interview_location || 'N/A' }}</td>
              <td>{{ item.interview_notes || 'N/A' }}</td>
              <td class="actions">
                <button @click="openScheduleModal(item)" class="action-btn">
                  {{ item.interview_schedule ? 'Reschedule' : 'Schedule' }}
                </button>
                <button @click="selectStudent(item)" class="action-btn btn-approve" :disabled="item.processing">
                  Select
                </button>
                <button @click="rejectStudent(item)" class="action-btn btn-reject" :disabled="item.processing">
                  Reject
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Schedule Interview Modal -->
    <div v-if="modal.visible" class="modal" @click.self="closeModal">
      <div class="card modal-content">
        <h3>Schedule Interview</h3>
        <p><strong>Student:</strong> {{ modal.interview?.student.full_name }}</p>
        <p><strong>Drive:</strong> {{ modal.interview?.drive.job_title }}</p>
        <div class="form-group">
          <label for="interview-dt">Interview Date & Time:</label>
          <input v-model="modal.date" type="datetime-local" id="interview-dt">
        </div>
        <div class="form-group">
          <label for="interview-mode">Mode:</label>
          <select v-model="modal.mode" id="interview-mode">
            <option value="Online">Online</option>
            <option value="Offline">Offline</option>
          </select>
        </div>
        <div class="form-group">
          <label for="interview-location">Meeting Link / Venue:</label>
          <input v-model="modal.location" type="text" id="interview-location" placeholder="https://meet... or Room 301">
        </div>
        <div class="form-group">
          <label for="interview-notes">Notes (optional):</label>
          <textarea v-model="modal.notes" id="interview-notes" rows="3" placeholder="Any instructions for the interview..."></textarea>
        </div>
        <div class="form-actions">
          <button class="btn" @click="submitSchedule" :disabled="modal.saving || !modal.date">
            {{ modal.saving ? 'Saving...' : 'Save Schedule' }}
          </button>
          <button class="btn btn-secondary" @click="closeModal">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'CompanyInterviews',
  data() {
    return {
      loading: true,
      error: null,
      interviews: [],
      selectedDrive: '',
      scheduleFilter: '',
      modal: { visible: false, interview: null, date: '', mode: 'Online', location: '', notes: '', saving: false }
    }
  },
  computed: {
    uniqueDrives() {
      const map = new Map()
      this.interviews.forEach(i => {
        if (!map.has(i.drive.id)) map.set(i.drive.id, i.drive)
      })
      return Array.from(map.values())
    },
    filteredInterviews() {
      let list = this.interviews
      if (this.selectedDrive) {
        list = list.filter(i => i.drive.id === parseInt(this.selectedDrive))
      }
      if (this.scheduleFilter === 'scheduled') {
        list = list.filter(i => i.interview_schedule)
      } else if (this.scheduleFilter === 'unscheduled') {
        list = list.filter(i => !i.interview_schedule)
      }
      return list
    },
    scheduledCount() {
      return this.interviews.filter(i => i.interview_schedule).length
    },
    pendingCount() {
      return this.interviews.filter(i => !i.interview_schedule).length
    }
  },
  async mounted() {
    await this.fetchInterviews()
  },
  methods: {
    formatDateTime(d) { return new Date(d).toLocaleString() },
    async fetchInterviews() {
      try {
        const { data } = await api.get('/company/interviews')
        this.interviews = data.interviews.map(i => ({ ...i, processing: false }))
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load interviews'
      } finally {
        this.loading = false
      }
    },
    openScheduleModal(item) {
      const existing = item.interview_schedule ? new Date(item.interview_schedule).toISOString().slice(0, 16) : ''
      this.modal = {
        visible: true,
        interview: item,
        date: existing,
        mode: item.interview_mode || 'Online',
        location: item.interview_location || '',
        notes: item.interview_notes || '',
        saving: false
      }
    },
    closeModal() {
      this.modal = { visible: false, interview: null, date: '', mode: 'Online', location: '', notes: '', saving: false }
    },
    async submitSchedule() {
      const m = this.modal
      if (!m.interview || !m.date) return
      m.saving = true
      try {
        await api.put(`/company/application/${m.interview.application_id}/status`, {
          status: 'Shortlisted',
          interview_schedule: m.date,
          interview_mode: m.mode,
          interview_location: m.location,
          feedback: m.notes
        })
        m.interview.interview_schedule = m.date
        m.interview.interview_mode = m.mode
        m.interview.interview_location = m.location
        m.interview.interview_notes = m.notes
        this.closeModal()
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to schedule interview')
      } finally {
        m.saving = false
      }
    },
    async selectStudent(item) {
      if (!confirm(`Select ${item.student.full_name} for ${item.drive.job_title}?`)) return
      item.processing = true
      try {
        await api.put(`/company/application/${item.application_id}/status`, {
          status: 'Selected',
          feedback: item.interview_notes
        })
        // Remove from interviews list (they're now in Selected page)
        this.interviews = this.interviews.filter(i => i.application_id !== item.application_id)
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to select student')
      } finally {
        item.processing = false
      }
    },
    async rejectStudent(item) {
      if (!confirm(`Reject ${item.student.full_name} for ${item.drive.job_title}?`)) return
      item.processing = true
      try {
        await api.put(`/company/application/${item.application_id}/status`, {
          status: 'Rejected',
          feedback: item.interview_notes
        })
        // Remove from interviews list
        this.interviews = this.interviews.filter(i => i.application_id !== item.application_id)
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to reject student')
      } finally {
        item.processing = false
      }
    }
  }
}
</script>
