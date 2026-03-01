<template>
  <div class="ats-screener-page">
    <div class="container">
      <h1 class="page-title">ATS Resume Screener</h1>
      <p class="page-subtitle">
        Analyze your resume against job descriptions to improve your chances of getting shortlisted.
      </p>

      <div class="screener-grid">
        <!-- Input Section -->
        <div class="input-section">
          <div class="input-card">
            <h3>Resume Content</h3>
            <p class="input-hint">Paste your resume text below</p>
            <textarea 
              v-model="resumeText" 
              placeholder="Paste your resume content here... Include your skills, experience, education, and achievements."
              class="input-textarea"
              rows="12"
            ></textarea>
          </div>

          <div class="input-card">
            <h3>Job Description</h3>
            <p class="input-hint">Paste the job description you want to match against</p>
            <input 
              v-model="jobTitle" 
              type="text" 
              placeholder="Job Title (optional)"
              class="input-field"
            />
            <textarea 
              v-model="jobDescription" 
              placeholder="Paste the job description here... Include required skills, qualifications, and responsibilities."
              class="input-textarea"
              rows="10"
            ></textarea>
          </div>

          <button 
            @click="analyzeResume" 
            :disabled="!canAnalyze || loading"
            class="analyze-btn"
          >
            <span v-if="loading">Analyzing...</span>
            <span v-else>Analyze Resume</span>
          </button>
        </div>

        <!-- Results Section -->
        <div class="results-section" v-if="result">
          <!-- Score Card -->
          <div class="score-card" :class="getScoreClass(result.score)">
            <div class="score-circle">
              <div class="score-value">{{ result.score }}</div>
              <div class="score-max">/100</div>
            </div>
            <div class="score-grade">Grade: {{ result.grade }}</div>
            <p class="score-message">{{ result.grade_message }}</p>
          </div>

          <!-- Score Breakdown -->
          <div class="breakdown-card">
            <h3>Score Breakdown</h3>
            <div class="breakdown-items">
              <div class="breakdown-item" v-for="(data, key) in result.breakdown" :key="key">
                <div class="breakdown-label">{{ formatLabel(key) }}</div>
                <div class="breakdown-bar">
                  <div 
                    class="breakdown-fill" 
                    :style="{ width: getPercentage(data.score, data.max) + '%' }"
                  ></div>
                </div>
                <div class="breakdown-score">{{ data.score }}/{{ data.max }}</div>
              </div>
            </div>
          </div>

          <!-- Skills Analysis -->
          <div class="skills-card">
            <h3>Skills Analysis</h3>
            
            <div class="skills-section matched" v-if="result.matched_skills?.length">
              <h4>Matched Skills</h4>
              <div class="skills-tags">
                <span class="skill-tag matched" v-for="skill in result.matched_skills" :key="skill">
                  {{ skill }}
                </span>
              </div>
            </div>

            <div class="skills-section missing" v-if="result.missing_skills?.length">
              <h4>Missing Skills</h4>
              <p class="skills-hint">Consider adding these skills to your resume if applicable:</p>
              <div class="skills-tags">
                <span class="skill-tag missing" v-for="skill in result.missing_skills" :key="skill">
                  {{ skill }}
                </span>
              </div>
            </div>
          </div>

          <!-- Feedback -->
          <div class="feedback-card" v-if="result.feedback?.length">
            <h3>Detailed Feedback</h3>
            <div class="feedback-list">
              <div 
                class="feedback-item" 
                v-for="(item, index) in result.feedback" 
                :key="index"
                :class="item.type"
              >
                <span class="feedback-icon">
                  {{ item.type === 'positive' ? '✓' : item.type === 'warning' ? '⚠' : item.type === 'negative' ? '✗' : '💡' }}
                </span>
                <span class="feedback-message">{{ item.message }}</span>
              </div>
            </div>
          </div>

          <!-- Resume Analysis -->
          <div class="analysis-card" v-if="result.resume_analysis">
            <h3>Resume Analysis</h3>
            <div class="analysis-grid">
              <div class="analysis-item">
                <div class="analysis-label">Total Skills Found</div>
                <div class="analysis-value">{{ result.resume_analysis.total_skills_found }}</div>
              </div>
              <div class="analysis-item">
                <div class="analysis-label">Experience Level</div>
                <div class="analysis-value">{{ result.resume_analysis.experience_years || 0 }} years</div>
              </div>
              <div class="analysis-item">
                <div class="analysis-label">Education Level</div>
                <div class="analysis-value">{{ result.resume_analysis.education_level || 'Not detected' }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div class="results-section empty" v-else-if="!loading">
          <div class="empty-state">
            <div class="empty-icon">📄</div>
            <h3>Ready to Analyze</h3>
            <p>Paste your resume and job description to get started.</p>
            <ul class="tips-list">
              <li>Include all relevant skills and technologies</li>
              <li>Mention years of experience clearly</li>
              <li>List your education qualifications</li>
              <li>Use keywords from the job description</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Skills Analyzer Tool -->
      <div class="skills-analyzer-section">
        <h2>Quick Skills Analyzer</h2>
        <p>Extract and categorize skills from any text</p>
        <div class="analyzer-input">
          <textarea 
            v-model="skillsText" 
            placeholder="Paste any text to extract skills..."
            class="input-textarea"
            rows="4"
          ></textarea>
          <button @click="analyzeSkills" :disabled="!skillsText.trim()" class="analyze-btn secondary">
            Extract Skills
          </button>
        </div>
        <div class="extracted-skills" v-if="extractedSkills">
          <h4>Extracted Skills</h4>
          <div class="skills-categories">
            <div 
              class="skill-category" 
              v-for="(skills, category) in extractedSkills.skills" 
              :key="category"
              v-show="skills.length > 0"
            >
              <h5>{{ formatLabel(category) }}</h5>
              <div class="skills-tags">
                <span class="skill-tag" v-for="skill in skills" :key="skill">{{ skill }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/services/api'

const resumeText = ref('')
const jobDescription = ref('')
const jobTitle = ref('')
const result = ref(null)
const loading = ref(false)
const error = ref(null)

const skillsText = ref('')
const extractedSkills = ref(null)

const canAnalyze = computed(() => {
  return resumeText.value.trim().length > 50 && jobDescription.value.trim().length > 20
})

const analyzeResume = async () => {
  if (!canAnalyze.value) return
  
  loading.value = true
  error.value = null
  result.value = null
  
  try {
    const response = await api.post('/ats/screen', {
      resume_text: resumeText.value,
      job_description: jobDescription.value,
      job_title: jobTitle.value || undefined
    })
    result.value = response.data
  } catch (err) {
    console.error('Analysis failed:', err)
    error.value = err.response?.data?.message || 'Analysis failed. Please try again.'
  } finally {
    loading.value = false
  }
}

const analyzeSkills = async () => {
  if (!skillsText.value.trim()) return
  
  try {
    const response = await api.post('/ats/analyze-skills', {
      text: skillsText.value
    })
    extractedSkills.value = response.data
  } catch (err) {
    console.error('Skills analysis failed:', err)
  }
}

const getScoreClass = (score) => {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'fair'
  return 'poor'
}

const getPercentage = (score, max) => {
  return Math.round((score / max) * 100)
}

const formatLabel = (key) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}
</script>
