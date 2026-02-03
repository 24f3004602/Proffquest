from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models import *
from utils.decorators import role_required
from flask import request
from sqlalchemy import or_
    
class AdminDashboardStats(Resource):
    @role_required('admin')
    def get(self):
        return {
            'Total_Students':Student.query.count(),
            'Total_Companies':Company.query.count(),
            'Total_Placement_drives':Placement_drive.query.count(),
            'Total_applications':Application.query.count()
        },200
    
class ApproveCompany(Resource):
    @role_required('admin')
    def post(self,company_id):
        try:
            company=Company.query.get_or_404(company_id)
            company.status='approved'
            db.session.commit()
            return {'message':'Company approved successfully'},200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to approve company', 'error': str(e)}, 500
    
class RejectCompany(Resource):
    @role_required('admin')
    def post(self,company_id):
        try:
            company=Company.query.get_or_404(company_id)
            company.status='rejected'
            db.session.commit()
            return {'message':'Company rejected successfully'},200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to reject company', 'error': str(e)}, 500
    
class AdminCompaniesList(Resource):
    @role_required('admin')
    def get(self):
        companies=Company.query.all()
        return [
            {
                'id':company.id,
                'company_name':company.company_name,
                'status':company.status,
                'is_blacklisted':company.is_blacklisted,
                'email':company.email,
                'hr_name':company.hr_name,
                'website':company.website,
                'description':company.description
            } for company in companies
        ],200
    
class BlacklistCompany(Resource):
    @role_required('admin')
    def post(self,company_id):
        company=Company.query.get_or_404(company_id)
        company.is_blacklisted=True
        db.session.commit()
        return {'message':'Company blacklisted successfully'},200

class ActiveCompany(Resource):
    @role_required('admin')
    def post(self,company_id):
        company=Company.query.get_or_404(company_id)
        company.is_blacklisted=False
        db.session.commit()
        return {'message':'Company activated successfully'},200

class SearchCompanies(Resource):
    @role_required('admin')
    def get(self):
        query = request.args.get('q', '')
        companies = Company.query.filter(
            or_(
                Company.company_name.ilike(f'%{query}%'),
                Company.description.ilike(f'%{query}%'),
                Company.email.ilike(f'%{query}%')
            )
        ).all()
        return [
            {
                'id':company.id,
                'company_name':company.company_name,
                'status':company.status,
                'is_blacklisted':company.is_blacklisted,
                'email':company.email,
                'hr_name':company.hr_name,
                'website':company.website,
                'description':company.description
            } for company in companies
        ],200

class SearchStudents(Resource):
    @role_required('admin')
    def get(self):
        query = request.args.get('q', '')
        students = Student.query.filter(
            or_(
                Student.full_name.ilike(f'%{query}%'),
                Student.roll_number.ilike(f'%{query}%'),
                Student.email.ilike(f'%{query}%')
            )
        ).all()
        return [
            {
                'id':student.id,
                'full_name':student.full_name,
                'roll_number':student.roll_number,
                'email':student.email,
                'college':student.college,
                'branch':student.branch,
                'cgpa':student.cgpa,
                'year':student.year,
                'is_blacklisted':student.is_blacklisted
            } for student in students
        ],200

class AdminPlacementDrives(Resource):
    @role_required('admin')
    def get(self):
        drives = Placement_drive.query.all()
        return [
            {
                'id':drive.id,
                'company_name':drive.company.company_name,
                'job_title':drive.job_title,
                'job_description':drive.job_description,
                'package_offered':drive.package_offered,
                'location':drive.location,
                'application_deadline':drive.application_deadline.isoformat() if drive.application_deadline else None,
                'drive_date':drive.drive_date.isoformat() if drive.drive_date else None,
                'status':drive.status,
                'is_approved':drive.is_approved,
                'is_active':drive.is_active,
                'max_applicants':drive.max_applicants
            } for drive in drives
        ],200

class ApprovePlacementDrive(Resource):
    @role_required('admin')
    def post(self,drive_id):
        drive=Placement_drive.query.get_or_404(drive_id)
        drive.status='approved'
        drive.is_approved=True
        db.session.commit()
        return {'message':'Placement drive approved successfully'},200

class RejectPlacementDrive(Resource):
    @role_required('admin')
    def post(self,drive_id):
        drive=Placement_drive.query.get_or_404(drive_id)
        drive.status='rejected'
        drive.is_approved=False
        db.session.commit()
        return {'message':'Placement drive rejected successfully'},200

class AdminApplications(Resource):
    @role_required('admin')
    def get(self):
        applications = Application.query.all()
        return [
            {
                'id':app.id,
                'student_name':app.student.full_name,
                'student_roll':app.student.roll_number,
                'company_name':app.placement_drive.company.company_name,
                'job_title':app.placement_drive.job_title,
                'status':app.status,
                'applied_at':app.applied_at.isoformat() if app.applied_at else None,
                'shortlisted_at':app.shortlisted_at.isoformat() if app.shortlisted_at else None,
                'selected_at':app.selected_at.isoformat() if app.selected_at else None
            } for app in applications
        ],200

class BlacklistStudent(Resource):
    @role_required('admin')
    def post(self,student_id):
        student=Student.query.get_or_404(student_id)
        student.is_blacklisted=True
        db.session.commit()
        return {'message':'Student blacklisted successfully'},200

class ActivateStudent(Resource):
    @role_required('admin')
    def post(self,student_id):
        student=Student.query.get_or_404(student_id)
        student.is_blacklisted=False
        db.session.commit()
        return {'message':'Student activated successfully'},200