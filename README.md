# Proffquest
Proffquest is the web application to search jobs where verified company can advertise their vacant jobs and skilled users can apply for their role and company can hire them. The whole applicaton will handled by Admin where he can verify and blacklist companies as required.

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables: Copy `.env` file and update JWT_SECRET_KEY
4. (Optional) Configure email for notifications using SMTP_* and EMAIL_SENDER
5. Initialize the database: `python default_admin.py`
6. Run the application: `python app.py`

### Background Jobs (Celery + Redis)
1. Start Redis locally (default: `redis://localhost:6379/0`).
2. Run a Celery worker from the backend directory:
	`celery -A celery_app.celery_app worker --loglevel=info`
3. Run Celery Beat (scheduler) from the backend directory:
	`celery -A celery_app.celery_app beat --loglevel=info`

Environment variables:
- CELERY_BROKER_URL (default: redis://localhost:6379/0)
- CELERY_RESULT_BACKEND (default: redis://localhost:6379/0)
- CELERY_TIMEZONE (default: UTC)
- SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_USE_TLS, EMAIL_SENDER
- GCHAT_WEBHOOK_URL (optional)
- SMS_PHONE_NUMBER (placeholder)

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`

## Default Admin Credentials
- Email: admin@1234
- Password: admin1234

## Features
- Role-based authentication (Admin, Student, Company)
- Company verification system
- Job posting and application management
- Admin dashboard for oversight
- Interview reminder job (scheduled)
- Monthly placement reports (HTML + PDF)
- Async CSV export for students and companies

# Development Notes
1. create model for database, add relation[backref vs back_populates]
backref: can use in one model only like if we have relation btw admin and applications and we can use it in only one model for fetching admin.applications
back_populates: can use in both models for fetching
2. we add admin in different file(default_admin.py)
3. we setup jwt token for role based access

