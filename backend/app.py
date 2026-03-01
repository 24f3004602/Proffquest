import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS

from models import db
from celery_app import make_celery
from resources.auth import *
from resources.admin import *
from resources.company import *
from resources.student import *
from resources.exports import *
from resources.analytics import *
from resources.resume_screener import *

# ---------------------------------------------------------------------------
# App & config
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "secret-key"
app.config["EXPORT_ROOT"] = os.path.join(app.root_path, "exports")
app.config["REPORT_ROOT"] = os.path.join(app.root_path, "reports")

# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
api = Api(app)
CORS(app, supports_credentials=True)

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
celery = make_celery(app)
import tasks  

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
# Auth
api.add_resource(Login, "/api/login")
api.add_resource(StudentRegister, "/api/register/student")
api.add_resource(CompanyRegister, "/api/register/company")

# Admin
api.add_resource(ApproveCompany, "/api/admin/approve_company/<int:company_id>")
api.add_resource(RejectCompany, "/api/admin/cancel_company/<int:company_id>")
api.add_resource(BlacklistCompany, "/api/admin/blacklist_company/<int:company_id>")
api.add_resource(AdminCompaniesList, "/api/admin/companies")
api.add_resource(AdminDashboardStats, "/api/admin/dashboard_stats")
api.add_resource(ActiveCompany, "/api/admin/activate_company/<int:company_id>")
api.add_resource(SearchCompanies, "/api/admin/search_companies")
api.add_resource(SearchStudents, "/api/admin/search_students")
api.add_resource(AdminPlacementDrives, "/api/admin/placement_drives")
api.add_resource(ApprovePlacementDrive, "/api/admin/approve_drive/<int:drive_id>")
api.add_resource(RejectPlacementDrive, "/api/admin/reject_drive/<int:drive_id>")
api.add_resource(AdminApplications, "/api/admin/applications")
api.add_resource(BlacklistStudent, "/api/admin/blacklist_student/<int:student_id>")
api.add_resource(ActivateStudent, "/api/admin/activate_student/<int:student_id>")
api.add_resource(AdminStudentProfile, "/api/admin/student/<int:student_id>")
api.add_resource(AdminStudentApplications, "/api/admin/student/<int:student_id>/applications")

# Company
api.add_resource(CompanyDashboard, "/api/company/dashboard")
api.add_resource(CreatePlacementDrive, "/api/company/create_drive")
api.add_resource(CompanyDrives, "/api/company/drives")
api.add_resource(DriveApplicants, "/api/company/drive/<int:drive_id>/applicants")
api.add_resource(UpdateApplicationStatus, "/api/company/application/<int:application_id>/status")
api.add_resource(UpdateDriveStatus, "/api/company/drive/<int:drive_id>/status")
api.add_resource(CompanyInterviews, "/api/company/interviews")
api.add_resource(CompanySelectedStudents, "/api/company/selected")
api.add_resource(CompanyProfile, "/api/company/profile")
api.add_resource(CompanySubmitApproval, "/api/company/profile/submit")
api.add_resource(CompanyResults, "/api/company/results")
api.add_resource(CompanyStudentProfile, "/api/company/student/<int:student_id>")
api.add_resource(CompanyStudentApplications, "/api/company/student/<int:student_id>/applications")
api.add_resource(CompanyExportApplications, "/api/company/exports")
api.add_resource(CompanyExportJobs, "/api/company/exports/jobs")
api.add_resource(CompanyExportDownload, "/api/company/exports/<int:job_id>/download")
api.add_resource(CompanyReportsList, "/api/company/reports")
api.add_resource(CompanyReportDownload, "/api/company/reports/<int:report_id>/download")

# Student
api.add_resource(StudentDashboard, "/api/student/dashboard")
api.add_resource(StudentProfile, "/api/student/profile")
api.add_resource(StudentDrives, "/api/student/drives")
api.add_resource(StudentDriveDetail, "/api/student/drive/<int:drive_id>")
api.add_resource(StudentApply, "/api/student/apply/<int:drive_id>")
api.add_resource(StudentApplications, "/api/student/applications")
api.add_resource(StudentExportApplications, "/api/student/exports")
api.add_resource(StudentExportJobs, "/api/student/exports/jobs")
api.add_resource(StudentExportDownload, "/api/student/exports/<int:job_id>/download")

# Public API (no auth required)
api.add_resource(PublicStats, "/api/public/stats")

# Analytics
api.add_resource(AnalyticsPlacementTrends, "/api/analytics/placement-trends")
api.add_resource(AnalyticsJobDemand, "/api/analytics/job-demand")
api.add_resource(AnalyticsApplicationFunnel, "/api/analytics/funnel")
api.add_resource(AnalyticsCompanyPerformance, "/api/company/analytics")
api.add_resource(AnalyticsStudentPerformance, "/api/student/analytics")

# ATS Resume Screener
api.add_resource(ATSResumeScreener, "/api/ats/screen")
api.add_resource(ATSStudentResumeCheck, "/api/student/ats/check/<int:drive_id>")
api.add_resource(ATSCompanyBulkScreen, "/api/company/ats/bulk-screen/<int:drive_id>")
api.add_resource(ATSSkillsAnalyzer, "/api/ats/analyze-skills")

# ---------------------------------------------------------------------------
# Create tables
# ---------------------------------------------------------------------------
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)