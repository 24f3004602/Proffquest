# ProffQuest - File Mastery Checklist

Use this checklist to track your progress as you study each file.

---

## BACKEND FILES (Python/Flask)

### Core Application
- [ ] `backend/app.py` - Main Flask application & route registration
- [ ] `backend/models.py` - SQLAlchemy database models (7 models)
- [ ] `backend/celery_app.py` - Celery configuration & scheduled tasks
- [ ] `backend/tasks.py` - Background tasks (exports, reminders, reports)
- [ ] `backend/default_admin.py` - Initial admin setup
- [ ] `backend/requirements.txt` - Python dependencies

### Resources (API Endpoints)
- [ ] `backend/resources/auth.py` - Login, StudentRegister, CompanyRegister
- [ ] `backend/resources/admin.py` - Admin management APIs (15+ endpoints)
- [ ] `backend/resources/company.py` - Company management APIs (12+ endpoints)
- [ ] `backend/resources/student.py` - Student APIs (6 endpoints)
- [ ] `backend/resources/analytics.py` - Analytics & statistics APIs
- [ ] `backend/resources/exports.py` - Export & report download APIs
- [ ] `backend/resources/resume_screener.py` - ATS screening APIs

### Utilities
- [ ] `backend/utils/decorators.py` - role_required decorator
- [ ] `backend/utils/cache.py` - Caching utility
- [ ] `backend/utils/notifications.py` - GChat webhook notifications

### Database Migrations
- [ ] `backend/migrations/env.py` - Alembic environment setup
- [ ] `backend/migrations/versions/` - Migration files

---

## FRONTEND FILES (Vue.js 3)

### Core Application
- [ ] `frontend/src/main.js` - Vue app entry point
- [ ] `frontend/src/App.vue` - Root component
- [ ] `frontend/src/NavBar.vue` - Navigation component
- [ ] `frontend/src/home.vue` - Homepage component

### Configuration
- [ ] `frontend/src/router/index.js` - Vue Router configuration
- [ ] `frontend/src/stores/auth.js` - Auth state management
- [ ] `frontend/src/services/api.js` - Axios API service

### Auth Views
- [ ] `frontend/src/views/Login.vue` - Login page
- [ ] `frontend/src/views/Register.vue` - Registration page
- [ ] `frontend/src/views/ATSScreener.vue` - ATS resume checker

### Admin Views
- [ ] `frontend/src/views/admin/dashboard.vue` - Admin dashboard
- [ ] `frontend/src/views/admin/AdminStudents.vue` - Student management
- [ ] `frontend/src/views/admin/AdminCompanies.vue` - Company management
- [ ] `frontend/src/views/admin/AdminDrives.vue` - Drive approvals
- [ ] `frontend/src/views/admin/AdminApplications.vue` - All applications
- [ ] `frontend/src/views/admin/AdminAnalytics.vue` - Platform analytics

### Company Views
- [ ] `frontend/src/views/company/CompanyDashboard.vue` - Company dashboard
- [ ] `frontend/src/views/company/CompanyProfile.vue` - Profile management
- [ ] `frontend/src/views/company/CompanyDrivesPage.vue` - Drives list
- [ ] `frontend/src/views/company/CreateDrive.vue` - Create new drive
- [ ] `frontend/src/views/company/CompanyApplications.vue` - View applicants
- [ ] `frontend/src/views/company/CompanyInterviews.vue` - Interview scheduling
- [ ] `frontend/src/views/company/CompanyResults.vue` - Selection results
- [ ] `frontend/src/views/company/CompanyAnalytics.vue` - Hiring analytics

### Student Views
- [ ] `frontend/src/views/student/studentDashboard.vue` - Student dashboard
- [ ] `frontend/src/views/student/StudentProfile.vue` - Profile management
- [ ] `frontend/src/views/student/StudentDrives.vue` - Browse & apply
- [ ] `frontend/src/views/student/StudentApplications.vue` - My applications
- [ ] `frontend/src/views/student/StudentHistory.vue` - Application history
- [ ] `frontend/src/views/student/StudentAnalytics.vue` - Performance stats

### Styling
- [ ] `frontend/src/assets/style.css` - Global CSS styles

### Build Configuration
- [ ] `frontend/vite.config.js` - Vite configuration
- [ ] `frontend/package.json` - NPM dependencies
- [ ] `frontend/jsconfig.json` - JavaScript config

---

## PROGRESS TRACKER

| Day | Focus Area | Files | Status |
|-----|-----------|-------|--------|
| Day 1 | Foundation & Core | app.py, models.py, main.js, App.vue, router, stores, api | ⬜ |
| Day 2 | Authentication | auth.py, decorators.py, Login.vue, Register.vue, NavBar.vue | ⬜ |
| Day 3 | Student Module | student.py, studentDashboard.vue, StudentProfile.vue, StudentDrives.vue, StudentApplications.vue, StudentHistory.vue, StudentAnalytics.vue | ⬜ |
| Day 4 | Company Module | company.py, CompanyDashboard.vue, CompanyProfile.vue, CompanyDrivesPage.vue, CreateDrive.vue, CompanyApplications.vue, CompanyInterviews.vue, CompanyResults.vue, CompanyAnalytics.vue | ⬜ |
| Day 5 | Admin & Analytics | admin.py, analytics.py, dashboard.vue, AdminStudents.vue, AdminCompanies.vue, AdminDrives.vue, AdminApplications.vue, AdminAnalytics.vue | ⬜ |
| Day 6 | Advanced Features | celery_app.py, tasks.py, exports.py, resume_screener.py, ATSScreener.vue, cache.py, notifications.py | ⬜ |
| Day 7 | Integration & Testing | migrations, default_admin.py, style.css, configs, documentation | ⬜ |

---

## NOTES SECTION

### Day 1 Notes:
```
(Write your learnings here)
```

### Day 2 Notes:
```
(Write your learnings here)
```

### Day 3 Notes:
```
(Write your learnings here)
```

### Day 4 Notes:
```
(Write your learnings here)
```

### Day 5 Notes:
```
(Write your learnings here)
```

### Day 6 Notes:
```
(Write your learnings here)
```

### Day 7 Notes:
```
(Write your learnings here)
```

---

## QUESTIONS TO RESEARCH

Use this section to track questions that come up during your study:

1. 
2. 
3. 

---

**Total Files: 44** | **Backend: 17** | **Frontend: 27**
