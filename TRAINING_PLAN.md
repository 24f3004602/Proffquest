# ProffQuest - 7-Day Expert Training Plan

> **Goal:** Master every file in your placement management system (Frontend + Backend)  
> **Daily Commitment:** 4-6 hours of focused study  
> **Approach:** Theory → Code Reading → Practice → Mini-Projects

---

## 📋 Project Overview

| Layer | Technology | Files |
|-------|------------|-------|
| Backend | Flask, SQLAlchemy, Celery, JWT | 14 Python files |
| Frontend | Vue.js 3, Vue Router, Axios | 24 Vue/JS files |
| Database | SQLite (SQLAlchemy ORM) | 7 Models |

---

## 🗓️ DAY 1: Foundation & Core Architecture

### Morning Session (2-3 hours) - Backend Core

#### 1. `backend/app.py` - The Heart of Your Application
**Concepts to Master:**
- Flask application factory pattern
- Flask-RESTful API resource registration
- Flask extensions initialization (SQLAlchemy, JWT, CORS, Migrate)
- Route organization and namespacing

**Study Tasks:**
```python
# Understand these patterns in app.py:
1. How Flask app is configured (lines 1-60)
2. How extensions are initialized (db, jwt, api, cors)
3. How API routes are registered with api.add_resource()
4. The relationship between URL paths and Resource classes
```

**Practice Exercise:**
- Draw a diagram showing all API endpoints grouped by role (admin/company/student)
- Create a spreadsheet mapping each `api.add_resource()` to its HTTP methods

#### 2. `backend/models.py` - Database Schema
**Concepts to Master:**
- SQLAlchemy ORM basics
- Model relationships (one-to-many, many-to-one)
- Database constraints (UniqueConstraint, ForeignKey)
- Column types and defaults

**Study Each Model:**
| Model | Purpose | Key Relationships |
|-------|---------|-------------------|
| `Admin` | Admin users | None |
| `Student` | Student profiles | → Applications |
| `Company` | Company profiles | → Placement_drives |
| `Application` | Job applications | → Student, → Placement_drive |
| `Placement_drive` | Job postings | → Company, → Eligibilities, → Applications |
| `Drive_eligibility` | Eligibility criteria | → Placement_drive |
| `ExportJob` | Export tracking | None |
| `PlacementReport` | Reports | → Company |

**Practice Exercise:**
- Create an ER diagram (Entity-Relationship) of all models
- Write 10 sample SQLAlchemy queries (filter, join, aggregate)

---

### Afternoon Session (2-3 hours) - Frontend Core

#### 3. `frontend/src/main.js` - Vue Entry Point
**Concepts to Master:**
- Vue 3 application creation with `createApp()`
- Plugin registration (router)
- CSS imports
- Mount point (#app)

#### 4. `frontend/src/App.vue` - Root Component
**Concepts to Master:**
- Vue Single File Component structure (template/script/style)
- Component registration and usage
- Router-view for page rendering

#### 5. `frontend/src/router/index.js` - Navigation System
**Concepts to Master:**
- Vue Router 4 configuration
- Route definitions with meta information
- Navigation guards (`beforeEach`)
- Role-based access control
- `createWebHistory()` vs hash mode

**Study Tasks:**
```javascript
// Understand these patterns:
1. How routes are protected with meta.requiresAuth
2. How role checking works in navigation guards
3. Component lazy loading vs eager loading
```

**Practice Exercise:**
- Create a route map showing all paths and their protection levels
- Add a new protected route for a "Settings" page

#### 6. `frontend/src/stores/auth.js` - State Management
**Concepts to Master:**
- Vue 3 Reactivity API (`reactive`)
- Computed getters
- localStorage persistence
- Authentication state management

#### 7. `frontend/src/services/api.js` - HTTP Client
**Concepts to Master:**
- Axios instance creation
- Request interceptors (adding JWT tokens)
- Response interceptors (handling 401 errors)
- Automatic auth header injection

---

### Day 1 Homework:
1. ✅ Draw complete architecture diagram
2. ✅ List all API endpoints with their HTTP methods
3. ✅ Create ER diagram of database models
4. ✅ Test each route manually using Postman/Thunder Client

---

## 🗓️ DAY 2: Authentication & Authorization System

### Morning Session (2-3 hours) - Backend Auth

#### 1. `backend/resources/auth.py` - Authentication APIs
**Concepts to Master:**
- Flask-RESTful Resource class
- Password hashing with Werkzeug (`generate_password_hash`, `check_password_hash`)
- JWT token creation with Flask-JWT-Extended
- Multi-role authentication (Admin, Student, Company)
- Input validation patterns

**Deep Dive into Classes:**
| Class | Endpoint | Purpose |
|-------|----------|---------|
| `Login` | POST /api/login | Authenticate all user types |
| `StudentRegister` | POST /api/register/student | Register new students |
| `CompanyRegister` | POST /api/register/company | Register new companies |

**Study Tasks:**
```python
# Understand these security patterns:
1. How login checks multiple user tables
2. How blacklisted users are blocked
3. How company approval status affects login
4. How JWT identity is encoded with role + id
```

#### 2. `backend/utils/decorators.py` - Authorization
**Concepts to Master:**
- Python decorators with `functools.wraps`
- JWT identity extraction
- Role-based access control decorator
- Chaining decorators (`@jwt_required` + custom)

**Practice Exercise:**
```python
# Create these custom decorators:
1. @admin_required - shortcut for role_required('admin')
2. @student_required - shortcut for role_required('student')
3. @company_approved_required - check company is approved
```

---

### Afternoon Session (2-3 hours) - Frontend Auth

#### 3. `frontend/src/views/Login.vue` - Login Page
**Concepts to Master:**
- Vue form handling with v-model
- Form validation
- API integration for login
- Token storage after successful login
- Router navigation after auth

**Study the Flow:**
```
User Input → Form Submit → API Call → Store Token → Redirect to Dashboard
```

#### 4. `frontend/src/views/Register.vue` - Registration Page
**Concepts to Master:**
- Multi-step or multi-type registration
- Form validation (email, required fields)
- Conditional rendering based on user type
- Success/error handling

#### 5. `frontend/src/NavBar.vue` - Navigation Component
**Concepts to Master:**
- Conditional rendering based on auth state
- Dynamic navigation links per role
- Logout functionality
- Responsive navigation

---

### Day 2 Homework:
1. ✅ Trace complete login flow from frontend to backend
2. ✅ Implement "Remember Me" feature
3. ✅ Add password strength validation
4. ✅ Test all auth edge cases (wrong password, blacklisted, etc.)

---

## 🗓️ DAY 3: Student Module

### Morning Session (2-3 hours) - Backend

#### 1. `backend/resources/student.py` - Student APIs
**Concepts to Master:**
- Reading student data from JWT identity
- Profile CRUD operations
- Drive listing with eligibility filtering
- Application submission flow
- Application status tracking

**API Endpoints to Master:**
| Class | Purpose |
|-------|---------|
| `StudentDashboard` | Dashboard statistics |
| `StudentProfile` | GET/PUT profile data |
| `StudentDrives` | List eligible drives |
| `StudentDriveDetail` | Single drive details |
| `StudentApply` | Submit application |
| `StudentApplications` | List applications |

---

### Afternoon Session (2-3 hours) - Frontend

#### 2. `frontend/src/views/student/studentDashboard.vue`
**Concepts to Master:**
- Dashboard layout patterns
- Statistics cards
- Data fetching on mount
- Computed properties for metrics
- Conditional rendering

#### 3. `frontend/src/views/student/StudentProfile.vue`
**Concepts to Master:**
- Profile form with pre-filled data
- File upload (resume)
- Profile update API integration
- Form validation

#### 4. `frontend/src/views/student/StudentDrives.vue`
**Concepts to Master:**
- List rendering with v-for
- Filtering and sorting
- Pagination patterns
- Drive detail modal/expansion
- Apply button logic

#### 5. `frontend/src/views/student/StudentApplications.vue`
**Concepts to Master:**
- Application list display
- Status badges/chips
- Timeline or history view
- Filtering by status

#### 6. `frontend/src/views/student/StudentHistory.vue`
**Concepts to Master:**
- Historical data display
- Date formatting
- Activity timeline
- Export functionality

#### 7. `frontend/src/views/student/StudentAnalytics.vue`
**Concepts to Master:**
- Analytics visualization
- Chart integration (if any)
- Statistics calculation
- Performance metrics

---

### Day 3 Homework:
1. ✅ Build complete student user journey flowchart
2. ✅ Add new feature: "Save Drive" functionality
3. ✅ Implement drive filtering by branch/CGPA
4. ✅ Test all student workflows end-to-end

---

## 🗓️ DAY 4: Company Module

### Morning Session (2-3 hours) - Backend

#### 1. `backend/resources/company.py` - Company APIs
**Concepts to Master:**
- Company-specific data access
- Placement drive CRUD operations
- Applicant management
- Interview scheduling
- Status updates (shortlist, reject, offer)

**API Classes to Master:**
| Class | Purpose |
|-------|---------|
| `CompanyDashboard` | Company statistics |
| `CompanyProfile` | Profile management |
| `CreatePlacementDrive` | Create new drives |
| `CompanyDrives` | List company's drives |
| `DriveApplicants` | View drive applicants |
| `UpdateApplicationStatus` | Change application status |
| `UpdateDriveStatus` | Change drive status |
| `CompanyInterviews` | Interview management |
| `CompanySelectedStudents` | View selected students |
| `CompanyResults` | Results/offers |
| `CompanySubmitApproval` | Submit for admin approval |

---

### Afternoon Session (2-3 hours) - Frontend

#### 2. `frontend/src/views/company/CompanyDashboard.vue`
**Concepts to Master:**
- Company-specific dashboard
- Drive statistics
- Recent activity display
- Quick action buttons

#### 3. `frontend/src/views/company/CompanyProfile.vue`
**Concepts to Master:**
- Company profile editing
- Logo upload
- Status display (approved/pending)

#### 4. `frontend/src/views/company/CompanyDrivesPage.vue`
**Concepts to Master:**
- Drive list management
- Drive status badges
- Edit/Delete actions
- Status filters

#### 5. `frontend/src/views/company/CreateDrive.vue`
**Concepts to Master:**
- Multi-step form
- Dynamic eligibility criteria
- Date pickers
- Form validation
- Draft saving

#### 6. `frontend/src/views/company/CompanyApplications.vue`
**Concepts to Master:**
- Applicant list per drive
- Bulk actions
- Status updates
- Resume viewing

#### 7. `frontend/src/views/company/CompanyInterviews.vue`
**Concepts to Master:**
- Interview scheduling
- Calendar integration
- Interview mode (online/offline)
- Interview notes

#### 8. `frontend/src/views/company/CompanyResults.vue`
**Concepts to Master:**
- Final results display
- Offer management
- Selection confirmation

#### 9. `frontend/src/views/company/CompanyAnalytics.vue`
**Concepts to Master:**
- Hiring analytics
- Conversion rates
- Drive performance metrics

---

### Day 4 Homework:
1. ✅ Document complete company hiring workflow
2. ✅ Add bulk shortlist feature
3. ✅ Implement interview calendar view
4. ✅ Test drive creation with all eligibility options

---

## 🗓️ DAY 5: Admin Module & Analytics

### Morning Session (2-3 hours) - Backend

#### 1. `backend/resources/admin.py` - Admin APIs
**Concepts to Master:**
- Admin dashboard statistics
- Company approval workflow
- Student management (blacklist/activate)
- Drive approval system
- Search functionality
- Global application oversight

**API Classes to Master:**
| Class | Purpose |
|-------|---------|
| `AdminDashboardStats` | Platform statistics |
| `AdminCompaniesList` | List all companies |
| `ApproveCompany` | Approve company registration |
| `RejectCompany` | Reject company |
| `BlacklistCompany` | Blacklist company |
| `ActiveCompany` | Reactivate company |
| `SearchCompanies` | Search companies |
| `SearchStudents` | Search students |
| `AdminPlacementDrives` | All drives |
| `ApprovePlacementDrive` | Approve drive |
| `RejectPlacementDrive` | Reject drive |
| `AdminApplications` | All applications |
| `BlacklistStudent` | Blacklist student |
| `ActivateStudent` | Activate student |
| `AdminStudentProfile` | View student profile |
| `AdminStudentApplications` | Student's applications |

#### 2. `backend/resources/analytics.py` - Analytics APIs
**Concepts to Master:**
- Aggregate queries with SQLAlchemy
- Data transformation for charts
- Placement trends calculation
- Job demand analysis
- Application funnel metrics

---

### Afternoon Session (2-3 hours) - Frontend

#### 3. `frontend/src/views/admin/dashboard.vue`
**Concepts to Master:**
- Admin overview dashboard
- Key metrics display
- Pending approvals count
- Recent activity

#### 4. `frontend/src/views/admin/AdminStudents.vue`
**Concepts to Master:**
- Student list with search
- Blacklist/activate actions
- Student profile viewing
- Pagination

#### 5. `frontend/src/views/admin/AdminCompanies.vue`
**Concepts to Master:**
- Company management
- Approval actions
- Status filtering
- Company details modal

#### 6. `frontend/src/views/admin/AdminDrives.vue`
**Concepts to Master:**
- Drive approval workflow
- Drive status management
- Bulk operations

#### 7. `frontend/src/views/admin/AdminApplications.vue`
**Concepts to Master:**
- All applications view
- Cross-company/student filtering
- Status overview

#### 8. `frontend/src/views/admin/AdminAnalytics.vue`
**Concepts to Master:**
- Platform-wide analytics
- Trend visualization
- Export reports
- Dashboard customization

---

### Day 5 Homework:
1. ✅ Map complete admin approval workflow
2. ✅ Add admin notification system
3. ✅ Implement advanced search filters
4. ✅ Create custom analytics dashboard widget

---

## 🗓️ DAY 6: Advanced Features (Celery, Exports, ATS)

### Morning Session (2-3 hours) - Background Tasks & Exports

#### 1. `backend/celery_app.py` - Task Queue Configuration
**Concepts to Master:**
- Celery configuration with Flask
- Broker setup (Redis)
- Flask application context in tasks
- Beat scheduler for periodic tasks
- Crontab scheduling patterns

**Scheduled Tasks:**
| Task | Schedule | Purpose |
|------|----------|---------|
| `send_interview_reminders` | Every hour | Remind about upcoming interviews |
| `send_deadline_reminders` | Daily 9 AM | Remind about deadlines |
| `generate_monthly_placement_reports` | Monthly (1st) | Generate reports |
| `generate_admin_monthly_report` | Monthly (1st) | Admin activity report |

#### 2. `backend/tasks.py` - Background Tasks
**Concepts to Master:**
- Celery task definition with `@celery.task`
- Email/notification sending
- CSV export generation
- PDF report generation (ReportLab)
- File handling and storage
- Error handling in async tasks

**Study Each Task:**
```python
# Key tasks to understand:
1. send_interview_reminders() - Notification logic
2. export_student_applications() - CSV generation
3. export_company_applications() - Bulk export
4. generate_monthly_placement_reports() - PDF generation
5. send_deadline_reminders() - Deadline tracking
```

#### 3. `backend/resources/exports.py` - Export APIs
**Concepts to Master:**
- Triggering async export jobs
- Job status polling
- File download endpoints
- Report generation requests

**API Classes to Study:**
| Class | Purpose |
|-------|---------|
| `CompanyExportApplications` | Trigger company export |
| `CompanyExportJobs` | List export jobs |
| `CompanyExportDownload` | Download export file |
| `CompanyReportsList` | List reports |
| `CompanyReportDownload` | Download report |
| `StudentExportApplications` | Student export |
| `StudentExportJobs` | Student job list |
| `StudentExportDownload` | Student download |

---

### Afternoon Session (2-3 hours) - ATS & Utilities

#### 4. `backend/resources/resume_screener.py` - ATS System
**Concepts to Master:**
- Resume parsing logic
- Skills extraction
- ATS scoring algorithm
- Bulk screening for companies
- PDF/DOC handling

**API Classes:**
| Class | Purpose |
|-------|---------|
| `ATSResumeScreener` | Single resume analysis |
| `ATSStudentResumeCheck` | Student self-check |
| `ATSCompanyBulkScreen` | Bulk screening |
| `ATSSkillsAnalyzer` | Skills extraction |

#### 5. `frontend/src/views/ATSScreener.vue`
**Concepts to Master:**
- File upload interface
- Progress indication
- Results display
- Skills visualization

#### 6. `backend/utils/cache.py` - Caching
**Concepts to Master:**
- Cache implementation
- Cache key strategies
- Cache invalidation
- Performance optimization

#### 7. `backend/utils/notifications.py` - Notifications
**Concepts to Master:**
- Google Chat webhook integration
- Notification formatting
- Error handling for webhooks

---

### Day 6 Homework:
1. ✅ Set up Redis locally and run Celery worker
2. ✅ Trigger an export and trace the entire flow
3. ✅ Upload a resume and analyze ATS scoring
4. ✅ Add a new scheduled task (weekly summary)

---

## 🗓️ DAY 7: Integration, Testing & Documentation

### Morning Session (2-3 hours) - Full Integration

#### 1. Migration System
**Files:** `backend/migrations/` directory
**Concepts to Master:**
- Alembic migration basics
- Flask-Migrate commands
- Migration versioning
- Database upgrades/downgrades

**Key Commands:**
```bash
flask db init      # Initialize migrations
flask db migrate   # Create migration
flask db upgrade   # Apply migration
flask db downgrade # Revert migration
```

#### 2. `backend/default_admin.py` - Initial Setup
**Concepts to Master:**
- Database seeding
- Default admin creation
- Initial data setup

#### 3. Complete Data Flow Analysis
**Study Task:** Trace these complete flows:
```
Flow 1: Student Registration → Login → Apply → Interview → Placed
Flow 2: Company Registration → Approval → Create Drive → Select Students
Flow 3: Admin Login → Approve Company → View Analytics → Generate Report
```

---

### Afternoon Session (2-3 hours) - Testing & Documentation

#### 4. CSS & Styling
**File:** `frontend/src/assets/style.css`
**Study:** Understanding the design system, class naming conventions, responsive patterns

#### 5. Configuration Files
| File | Purpose |
|------|---------|
| `frontend/vite.config.js` | Vite build configuration |
| `frontend/jsconfig.json` | JavaScript path aliases |
| `frontend/package.json` | Dependencies & scripts |
| `backend/requirements.txt` | Python dependencies |

#### 6. Create Your Own Documentation
**Tasks:**
- Write API documentation for all endpoints
- Create user manual for each role
- Document deployment process
- Create troubleshooting guide

---

## 📝 Daily Checklist Template

Use this for each day:

```
[ ] Read assigned files completely (every line)
[ ] Understand all imports and dependencies
[ ] Document key concepts learned
[ ] Complete practice exercises
[ ] Make at least one code modification
[ ] Test changes thoroughly
[ ] Ask yourself: "Can I explain this to someone else?"
```

---

## 🎯 Mastery Assessment

### Knowledge Test After Day 7:
1. Can you explain the complete authentication flow?
2. Can you add a new API endpoint with proper auth?
3. Can you create a new Vue component with API integration?
4. Can you modify the database schema and migrate?
5. Can you create a new Celery task?
6. Can you debug any issue in the system?

### Final Project Ideas:
1. **Add Email Notifications** - Replace GChat with email
2. **Add Student Resume Builder** - In-app resume creation
3. **Add Company Feedback System** - Post-placement feedback
4. **Add Admin Dashboard Widgets** - Customizable dashboard
5. **Add API Rate Limiting** - Prevent abuse

---

## 📚 Reference Commands

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask db upgrade
python app.py

# Celery
celery -A celery_app.celery worker --loglevel=info
celery -A celery_app.celery beat --loglevel=info

# Frontend
cd frontend
npm install
npm run dev
```

---

## 🏆 Completion Certificate

After completing this 7-day plan, you will have:
- ✅ Read and understood 100% of the codebase
- ✅ Mastered Flask-RESTful API development
- ✅ Mastered Vue.js 3 frontend development
- ✅ Understood authentication & authorization
- ✅ Learned background task processing with Celery
- ✅ Gained experience with database design & migrations
- ✅ Built new features independently

**Congratulations! You are now a ProffQuest Expert! 🎉**
