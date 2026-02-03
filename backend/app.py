from flask import Flask, jsonify
from models import db
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.auth import Login, StudentRegister, CompanyRegister
from resources.admin import *
from flask_migrate import Migrate
from flask_cors import CORS
app = Flask(__name__)
jwt=JWTManager(app)
api=Api(app)
CORS(app,supports_credentials=True)

# SQLite configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JWT_SECRET_KEY'] = 'secret-key'

db.init_app(app)
migrate = Migrate(app, db)

api.add_resource(Login,'/api/login')
api.add_resource(StudentRegister,'/api/register/student')
api.add_resource(CompanyRegister,'/api/register/company')
api.add_resource(ApproveCompany,'/api/admin/approve_company/<int:company_id>')
api.add_resource(RejectCompany,'/api/admin/cancel_company/<int:company_id>')
api.add_resource(BlacklistCompany,'/api/admin/blacklist_company/<int:company_id>')
api.add_resource(AdminCompaniesList,'/api/admin/companies')
api.add_resource(AdminDashboardStats,'/api/admin/dashboard_stats')
api.add_resource(ActiveCompany,'/api/admin/activate_company/<int:company_id>')
api.add_resource(SearchCompanies,'/api/admin/search_companies')
api.add_resource(SearchStudents,'/api/admin/search_students')
api.add_resource(AdminPlacementDrives,'/api/admin/placement_drives')
api.add_resource(ApprovePlacementDrive,'/api/admin/approve_drive/<int:drive_id>')
api.add_resource(RejectPlacementDrive,'/api/admin/reject_drive/<int:drive_id>')
api.add_resource(AdminApplications,'/api/admin/applications')
api.add_resource(BlacklistStudent,'/api/admin/blacklist_student/<int:student_id>')
api.add_resource(ActivateStudent,'/api/admin/activate_student/<int:student_id>')
# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)