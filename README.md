# Proffquest
Proffquest is the web application to search jobs where verified company can advertise their vacant jobs and skilled users can apply for their role and company can hire them. The whole applicaton will handled by Admin where he can verify and blacklist companies as required.

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables: Copy `.env` file and update JWT_SECRET_KEY
4. Initialize the database: `python default_admin.py`
5. Run the application: `python app.py`

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

# Development Notes
1. create model for database, add relation[backref vs back_populates]
backref: can use in one model only like if we have relation btw admin and applications and we can use it in only one model for fetching admin.applications
back_populates: can use in both models for fetching
2. we add admin in different file(default_admin.py)
3. we setup jwt token for role based access

