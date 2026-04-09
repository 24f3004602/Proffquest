# Proffquest - Campus Placement Management System

Proffquest is a comprehensive web-based campus placement management system that connects students, companies, and administrators in a streamlined recruitment process. The platform enables verified companies to post job opportunities, allows students to apply for positions, and provides administrators with complete oversight and management capabilities.

## 📁 Project Structure

```
Proffquest/
├── backend/
│   ├── resources/                # API resource classes (one per domain)
│   │   ├── admin.py              # Admin endpoints (dashboard, companies, students, drives)
│   │   ├── analytics.py          # Public statistics & chart data
│   │   ├── auth.py               # Login & registration
│   │   ├── company.py            # Company dashboard, drives, interviews, results
│   │   ├── exports.py            # Async CSV export & report downloads
│   │   └── student.py            # Student dashboard, drives, applications
│   ├── utils/
│   │   ├── cache.py              # Flask-Caching with Redis (init, clear, key builder)
│   │   ├── decorators.py         # @role_required JWT decorator
│   │   └── notifications.py      # Email (SMTP) & Google Chat webhook helpers
│   ├── exports/                  # Generated CSV export files (per user)
│   ├── instance/                 # SQLite database file (app.db)
│   ├── reports/                  # Generated monthly reports (HTML/PDF)
│   ├── app.py                    # Flask app setup, route registration, extensions
│   ├── celery_app.py             # Celery configuration & beat schedule
│   ├── models.py                 # SQLAlchemy models (8 tables)
│   ├── tasks.py                  # Celery tasks (reminders, exports, reports)
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── assets/               # Static assets (logo, global CSS)
│   │   ├── router/index.js       # Vue Router with role-based guards
│   │   ├── services/api.js       # Axios instance with JWT interceptor
│   │   ├── stores/auth.js        # Reactive auth state store (localStorage-backed)
│   │   ├── views/
│   │   │   ├── admin/            # Admin pages (dashboard, companies, students, drives, applications)
│   │   │   ├── company/          # Company pages (dashboard, drives, interviews, results, profile)
│   │   │   ├── student/          # Student pages (dashboard, drives, applications, profile, history)
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   ├── App.vue               # Root component
│   │   ├── Home.vue              # Public landing page with charts
│   │   ├── main.js               # Vue app entry point
│   │   └── NavBar.vue            # Navigation bar (role-aware)
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Vue.js 3, Vue Router, Axios, Chart.js, Vite
- **Backend**: Flask, Flask-RESTful, SQLAlchemy ORM
- **Database**: SQLite (configured by default), Flask-Migrate integrated
- **Caching**: Flask-Caching with Redis backend (5-min TTL)
- **Authentication**: JWT (Flask-JWT-Extended), role-based access control
- **Background Jobs**: Celery with Redis broker, Celery Beat scheduler
- **Notifications**: SMTP email, Google Chat webhooks

### System Overview
```
Frontend (Vue.js + Vite) ─── REST API ──→ Backend (Flask)
                                              │
                              ┌────────────────┼────────────────┐
                              ▼                ▼                ▼
                        SQLite/PostgreSQL   Redis Cache    Celery + Redis
                                          (Flask-Caching)  (async tasks)
                                                                │
                                                    ┌───────────┼───────────┐
                                                    ▼           ▼           ▼
                                              Email (SMTP)  Google Chat  CSV/PDF
                                                            Webhooks    Reports
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 20.19+ (or 22.12+)
- Redis

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```env
   JWT_SECRET_KEY=your-secret-key
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   SMTP_HOST=localhost
   SMTP_PORT=1025
   EMAIL_SENDER=noreply@proffquest.local
   GCHAT_WEBHOOK_URL=your-webhook-url
   ```
4. Start the Flask application (tables are auto-created on startup via `db.create_all()`):
   ```bash
   python app.py
   ```

### Background Jobs Setup
1. Start Redis server:
   ```bash
   redis-server
   ```
2. Start Celery worker (from the `backend` directory):
   ```bash
   celery -A app.celery worker --pool=solo --loglevel=info
   ```
3. Start Celery Beat scheduler (from the `backend` directory):
   ```bash
   celery -A app.celery beat --loglevel=info
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start development server:
   ```bash
   npm run dev
   ```

### Default Admin Credentials (for existing local `backend/instance/app.db` only)
- **Email**: admin@1234
- **Password**: admin1234

## 👥 User Roles & Features

### 🎓 Students
#### Profile Management
- Complete academic profile (CGPA, year, branch, college)
- Upload resume and personal details
- Roll number verification

#### Job Applications
- Browse available placement drives
- Filter drives by eligibility criteria
- Apply to multiple drives with a single click
- Track application status in real-time
- View application history and timeline

#### Application Status Tracking
- **Applied**: Initial application submitted
- **Shortlisted**: Selected for next round
- **Interview**: Interview scheduled
- **Offer**: Job offer received
- **Placed**: Successfully placed
- **Rejected**: Application rejected

#### Data Export
- Export application history to CSV
- Async export processing for large datasets
- Download status tracking

### 🏢 Companies
#### Company Verification
- Company registration with business details
- Admin approval workflow
- Status tracking (pending, approved, rejected)
- Verification badges

#### Placement Drive Management
- Create detailed job postings with:
  - Job title, description, and requirements
  - Package details and location
  - Application deadline and drive date
  - Maximum applicant limits
  - Required skills and qualifications

#### Eligibility Criteria Configuration
- Branch-specific requirements
- Minimum CGPA thresholds
- Year/passing year specifications
- Backlog policies
- Custom additional criteria

#### Application Management
- View all applicants for drives
- Filter and search applications
- Update application status
- Schedule interviews with notifications
- Bulk status updates

#### Interview Management
- Schedule interview slots
- Set interview mode (online/offline)
- Add interview location and notes
- Automatic reminder notifications

#### Analytics & Reporting
- Real-time dashboard statistics
- Application analytics
- Monthly placement reports (HTML/PDF)
- Export applicant data to CSV
- Placement success metrics

#### Drive Status Management
- **Pending**: Awaiting admin approval
- **Approved**: Live and accepting applications
- **Rejected**: Rejected by admin
- **Closed**: Completed or manually closed

### 👑 Administrators
#### Company Management
- Review and approve company registrations
- Verify company credentials
- Blacklist/activate companies
- Remove companies from platform
- Search and filter companies

#### Student Management
- View student profiles and details
- Monitor application activities
- Blacklist/activate student accounts
- Search students by various criteria

#### Placement Drive Oversight
- Review and approve drive postings
- Reject inappropriate drives
- Monitor drive statistics
- Ensure compliance with policies

#### Application Monitoring
- View all applications across platform
- Monitor application trends
- Generate detailed reports
- Track placement success rates

#### Analytics & Reports
- Platform-wide statistics dashboard
- Detailed CSV reports
- User activity monitoring
- Performance metrics

#### Search & Filter Capabilities
- Advanced search for companies and students
- Filter by status, dates, criteria
- Bulk operations support

## 🔄 Background Job System

### Automated Tasks
#### Interview Reminders
- **Schedule**: Managed by Celery Beat (`tasks.send_interview_reminders`, currently default `crontab()` i.e., every minute)
- **Function**: Sends reminder notifications for upcoming interviews
- **Channels**: Email and Google Chat notifications
- **Logic**: Checks for interviews scheduled within 24 hours

#### Deadline Reminders
- **Schedule**: Managed by Celery Beat (`tasks.send_deadline_reminders`, currently default `crontab()` i.e., every minute)
- **Function**: Sends reminders for drives with deadlines in the next 3 days
- **Channels**: Email and Google Chat notifications

#### CSV Export Processing
- **Trigger**: User-initiated export requests
- **Processing**: Runs synchronously by default; async dispatch when `CELERY_EXPORT_ASYNC=1`
- **Status Tracking**: Queued → Processing → Completed/Failed
- **Notification**: Email/Chat when export is ready

#### Monthly Placement Reports
- **Schedule**: Managed by Celery Beat (`tasks.generate_monthly_placement_reports`, currently default `crontab()` i.e., every minute)
- **Formats**: HTML and PDF reports
- **Content**: Company-specific placement statistics
- **Delivery**: Available for download in company dashboard

#### Monthly Admin Activity Report
- **Schedule**: Managed by Celery Beat (`tasks.generate_admin_monthly_report`, currently default `crontab()` i.e., every minute)
- **Format**: HTML report (saved under `backend/reports/admin/...`)
- **Delivery**: Notified to admins via email and Google Chat

### Notification System
#### Email Notifications
- SMTP-based email delivery
- Configurable email templates
- Failed delivery handling
- Support for MailHog development setup

#### Google Chat Integration
- Webhook-based notifications
- Real-time status updates
- Export completion alerts
- Interview reminders

## 🛡️ Security Features

### Authentication & Authorization
- JWT-based stateless authentication
- Role-based access control (RBAC)
- Token expiration management
- Secure password hashing (Werkzeug)

### Data Protection
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- Cross-origin resource sharing (CORS) configuration
- Secure file upload handling

### Account Security
- Account blacklisting for misconduct
- Admin-controlled company verification
- Session management
- Rate limiting considerations

## 📊 Database Schema

### Core Models
- **Admin**: System administrators
- **Student**: Student profiles and academic data
- **Company**: Company profiles and verification status
- **Placement_drive**: Job posting details and requirements
- **Application**: Student applications to drives
- **Drive_eligibility**: Detailed eligibility criteria per drive
- **ExportJob**: Async export job tracking
- **PlacementReport**: Monthly report generation tracking

### Key Relationships
- Students ↔ Applications ↔ Placement Drives ↔ Companies
- Drive Eligibility → Placement Drives
- Export Jobs → Users (Students/Companies)
- Placement Reports → Companies

## 🔧 API Endpoints

### Authentication
- `POST /api/login` - User authentication
- `POST /api/register/student` - Student registration
- `POST /api/register/company` - Company registration

### Student APIs
- `GET /api/student/dashboard` - Dashboard statistics
- `GET /api/student/profile` - Profile management
- `GET /api/student/drives` - Available placement drives
- `POST /api/student/apply/<drive_id>` - Apply to drive
- `GET /api/student/applications` - Application history
- `POST /api/student/exports` - Request CSV export
- `GET /api/student/exports/jobs` - List export jobs
- `GET /api/student/exports/<job_id>/download` - Download completed export

### Company APIs
- `GET /api/company/dashboard` - Company dashboard
- `POST /api/company/create_drive` - Create placement drive
- `GET /api/company/drives` - Manage drives
- `GET /api/company/drive/<drive_id>/applicants` - View applicants
- `GET /api/company/drive/<drive_id>` - Drive details
- `PUT /api/company/application/<id>/status` - Update application status
- `GET /api/company/interviews` - Interview management
- `GET /api/company/results` - Placement results
- `GET /api/company/results/csv` - Export placement results CSV
- `POST /api/company/exports` - Request applications export
- `GET /api/company/exports/jobs` - List export jobs
- `GET /api/company/exports/<job_id>/download` - Download completed export
- `GET /api/company/reports` - List generated monthly reports
- `GET /api/company/reports/<report_id>/download` - Download report file

### Admin APIs
- `GET /api/admin/dashboard_stats` - Platform statistics
- `POST /api/admin/approve_company/<id>` - Approve companies
- `GET /api/admin/companies` - Company management
- `GET /api/admin/student` - Student management
- `GET /api/admin/student/<student_id>` - Single student profile
- `GET /api/admin/placement_drives` - Drive oversight
- `GET /api/admin/applications` - Application monitoring

### Public APIs
- `GET /api/public/stats` - Public platform statistics

## 🔧 Configuration

### Environment Variables
```env
# JWT Authentication
JWT_SECRET_KEY=your-secure-secret-key

# Redis (used for both caching and Celery)
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TIMEZONE=UTC

# Email Configuration
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USERNAME=user
SMTP_PASSWORD=pass
SMTP_USE_TLS=false
EMAIL_SENDER=noreply@proffquest.local

# Google Chat Integration
GCHAT_WEBHOOK_URL=your-webhook-url
```

### Caching System (Flask-Caching + Redis)

All frequently-read endpoints are cached for **5 minutes** using `Flask-Caching` with a Redis backend. When Redis is unavailable the app automatically falls back to an in-process `SimpleCache` so pages still load.

**Cached endpoints** (charts, home page, search bars, dashboards):
| Endpoint | What it powers |
|----------|----------------|
| `GET /api/public/stats` | Home page statistics & Chart.js graphs |
| `GET /api/admin/dashboard_stats` | Admin dashboard stat cards |
| `GET /api/admin/applications` | Admin applications-by-status chart |
| `GET /api/admin/companies` | Admin companies-by-status chart |
| `GET /api/admin/placement_drives` | Admin drives list |
| `GET /api/admin/search_companies` | Company search bar |
| `GET /api/admin/search_students` | Student search bar |
| `GET /api/company/dashboard` | Company dashboard stats & charts |
| `GET /api/student/dashboard` | Student dashboard cards and stats |
| `GET /api/student/drives` | Student drives listing |

**Cache invalidation**: Write endpoints clear cached data explicitly using `cache.clear()` after updates. If you add a new mutating endpoint, add cache invalidation there as well.

## 📈 Performance Features

### Optimization Strategies
- **Flask-Caching** with Redis: 5-minute TTL on all read-heavy endpoints
- Graceful fallback to SimpleCache when Redis is down
- Explicit cache invalidation in mutating endpoints (`cache.clear()`)
- Lazy loading for SQLAlchemy relationships
- Async processing via Celery for heavy operations (CSV exports, PDF reports)

### Monitoring & Analytics
- Application performance tracking
- User activity monitoring
- Error logging and handling
- Background job status monitoring

## 🔄 Development Workflow

### Database Migrations
- Flask-Migrate is configured in `backend/app.py`
- Migration files are not currently included in this repository snapshot
- The app also creates tables at startup using `db.create_all()`

### Code Organization
- Modular backend structure with resources
- Component-based frontend architecture
- Utility modules for common functionality
- Decorators for authentication and caching

### Testing
- Unit tests for critical functionality
- API endpoint testing
- Cache performance testing

## 📝 Development Notes

### Database Relationships
- **backref**: Single-sided relationship definition (use in one model)
- **back_populates**: Two-sided relationship definition (use in both models)

### JWT Implementation
- Role and ID embedded in token payload
- Stateless authentication for scalability
- Automatic token validation on protected routes

### Celery Task Management
- Task retry mechanisms
- Error handling and logging
- Job status tracking and notifications

## 🚦 Getting Started Checklist

1. **Environment Setup**
   - [ ] Install Python 3.8+, Node.js 20.19+ (or 22.12+), Redis
   - [ ] Clone repository
   - [ ] Set up virtual environment

2. **Backend Configuration**
   - [ ] Install pip dependencies
   - [ ] Configure environment variables
   - [ ] Start Flask app once to initialize SQLite tables
   - [ ] Start Redis server
   - [ ] Run Flask application

3. **Background Jobs**
   - [ ] Start Celery worker
   - [ ] Start Celery beat scheduler
   - [ ] Verify job processing

4. **Frontend Setup**
   - [ ] Install npm dependencies
   - [ ] Start development server
   - [ ] Verify API connectivity

5. **Testing**
   - [ ] Login with an existing admin account in your local database
   - [ ] Test student and company registration
   - [ ] Create test placement drive
   - [ ] Test application workflow



**Proffquest** - Streamlining campus placement, one connection at a time. 🎯

