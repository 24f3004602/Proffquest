from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Company, Placement_drive, Application, Student, Drive_eligibility
from datetime import datetime
from utils.decorators import role_required
import json

class CompanyDashboard(Resource):
    @role_required('company')
    def get(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.is_blacklisted:
            return {'message': 'Company is blacklisted'}, 403

        drives = Placement_drive.query.filter_by(company_id=company.id).all()
        drives_data = []
        total_applications = 0
        shortlisted_count = 0
        selected_count = 0

        for drive in drives:
            applications = Application.query.filter_by(drive_id=drive.id).all()
            applicant_count = len(applications)
            total_applications += applicant_count

            # Count shortlisted and selected
            for app in applications:
                if app.status == 'Shortlisted':
                    shortlisted_count += 1
                elif app.status == 'Selected':
                    selected_count += 1

            drives_data.append({
                'id': drive.id,
                'job_title': drive.job_title,
                'job_description': drive.job_description,
                'package_offered': drive.package_offered,
                'location': drive.location,
                'rounds': drive.rounds,
                'application_deadline': drive.application_deadline.isoformat(),
                'drive_date': drive.drive_date.isoformat(),
                'max_applicants': drive.max_applicants,
                'is_approved': drive.is_approved,
                'is_active': drive.is_active,
                'status': drive.status,
                'created_at': drive.created_at.isoformat(),
                'applicant_count': applicant_count
            })

        # Get recent applications (last 10)
        recent_applications = Application.query.join(Placement_drive).filter(
            Placement_drive.company_id == company.id
        ).order_by(Application.applied_at.desc()).limit(10).all()

        recent_apps_data = []
        for app in recent_applications:
            student = Student.query.get(app.student_id)
            drive = Placement_drive.query.get(app.drive_id)
            if student and drive:
                recent_apps_data.append({
                    'application_id': app.id,
                    'student': {
                        'id': student.id,
                        'full_name': student.full_name,
                        'email': student.email
                    },
                    'placement_drive': {
                        'id': drive.id,
                        'job_title': drive.job_title
                    },
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat(),
                    'interview_schedule': app.interview_schedule.isoformat() if app.interview_schedule else None,
                    'feedback': app.interview_notes
                })

        return {
            'company': {
                'id': company.id,
                'company_name': company.company_name,
                'hr_name': company.hr_name,
                'website': company.website,
                'description': company.description,
                'address': company.address,
                'status': company.status
            },
            'stats': {
                'totalDrives': len(drives),
                'totalApplications': total_applications,
                'shortlisted': shortlisted_count,
                'selected': selected_count
            },
            'drives': drives_data,
            'recentApplications': recent_apps_data
        }

class CreatePlacementDrive(Resource):
    @role_required('company')
    def post(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.is_blacklisted:
            return {'message': 'Company is blacklisted'}, 403
        if company.status != 'approved':
            return {'message': 'Company not approved yet'}, 403

        data = request.get_json()
        required_fields = ['job_title', 'job_description', 'package_offered', 'location', 'application_deadline', 'drive_date']
        for field in required_fields:
            if field not in data:
                return {'message': f'{field} is required'}, 400

        try:
            deadline = datetime.fromisoformat(data['application_deadline'])
            drive_date = datetime.fromisoformat(data['drive_date'])
        except ValueError:
            return {'message': 'Invalid date format'}, 400

        new_drive = Placement_drive(
            company_id=company.id,
            job_title=data['job_title'],
            job_description=data['job_description'],
            package_offered=data['package_offered'],
            location=data['location'],
            rounds=data.get('rounds'),
            application_deadline=deadline,
            drive_date=drive_date,
            max_applicants=data.get('max_applicants'),
            status='pending'
        )
        db.session.add(new_drive)
        db.session.flush()  # To get the drive.id

        # Add eligibility criteria
        eligibility_data = data.get('eligibility', [])
        for el in eligibility_data:
            eligibility = Drive_eligibility(
                drive_id=new_drive.id,
                branch=el.get('branch'),
                min_cgpa=el.get('min_cgpa', 0.0),
                passing_year=el.get('passing_year'),
                backlog_allowed=el.get('backlog_allowed', False),
                additional_criteria=el.get('additional_criteria', '')
            )
            db.session.add(eligibility)

        db.session.commit()
        return {'message': 'Placement drive created successfully', 'drive_id': new_drive.id}, 201

class CompanyDrives(Resource):
    @role_required('company')
    def get(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.is_blacklisted:
            return {'message': 'Company is blacklisted'}, 403

        drives = Placement_drive.query.filter_by(company_id=company.id).all()
        drives_data = []
        for drive in drives:
            applicant_count = Application.query.filter_by(drive_id=drive.id).count()
            drives_data.append({
                'id': drive.id,
                'job_title': drive.job_title,
                'job_description': drive.job_description,
                'package_offered': drive.package_offered,
                'location': drive.location,
                'rounds': drive.rounds,
                'application_deadline': drive.application_deadline.isoformat() if drive.application_deadline else None,
                'drive_date': drive.drive_date.isoformat() if drive.drive_date else None,
                'status': drive.status,
                'is_active': drive.is_active,
                'created_at': drive.created_at.isoformat(),
                'applicant_count': applicant_count
            })
        return {
            'company_status': company.status,
            'drives': drives_data
        }

class DriveApplicants(Resource):
    @role_required('company')
    def get(self, drive_id):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.status != 'approved':
            return {'message': 'Company not approved yet'}, 403

        drive = Placement_drive.query.filter_by(id=drive_id, company_id=company.id).first()
        if not drive:
            return {'message': 'Drive not found'}, 404

        applications = Application.query.filter_by(drive_id=drive_id).all()
        applicants_data = []
        for app in applications:
            student = app.student
            applicants_data.append({
                'application_id': app.id,
                'student_id': student.id,
                'full_name': student.full_name,
                'email': student.email,
                'roll_number': student.roll_number,
                'college': student.college,
                'branch': student.branch,
                'cgpa': student.cgpa,
                'year': student.year,
                'resume_url': student.resume_url,
                'status': app.status,
                'applied_at': app.applied_at.isoformat(),
                'shortlisted_at': app.shortlisted_at.isoformat() if app.shortlisted_at else None,
                'selected_at': app.selected_at.isoformat() if app.selected_at else None,
                'interview_schedule': app.interview_schedule.isoformat() if app.interview_schedule else None,
                'interview_mode': app.interview_mode,
                'interview_location': app.interview_location,
                'interview_notes': app.interview_notes
            })
        return {'applicants': applicants_data}

class UpdateApplicationStatus(Resource):
    @role_required('company')
    def put(self, application_id):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.status != 'approved':
            return {'message': 'Company not approved yet'}, 403

        data = request.get_json()
        status = data.get('status')
        feedback = data.get('feedback', '')
        interview_schedule = data.get('interview_schedule')
        interview_mode = data.get('interview_mode')
        interview_location = data.get('interview_location')

        if status not in ['Applied', 'Shortlisted', 'Selected', 'Rejected']:
            return {'message': 'Invalid status'}, 400

        application = Application.query.filter_by(id=application_id).first()
        if not application:
            return {'message': 'Application not found'}, 404

        drive = Placement_drive.query.filter_by(id=application.drive_id, company_id=company.id).first()
        if not drive:
            return {'message': 'Unauthorized'}, 403

        application.status = status
        if status == 'Shortlisted':
            application.shortlisted_at = datetime.utcnow()
        elif status == 'Selected':
            application.selected_at = datetime.utcnow()
        if interview_schedule:
            try:
                application.interview_schedule = datetime.fromisoformat(interview_schedule)
            except ValueError:
                return {'message': 'Invalid interview schedule date'}, 400
        if interview_mode:
            if interview_mode not in ['Online', 'Offline']:
                return {'message': 'Invalid interview mode'}, 400
            application.interview_mode = interview_mode
        if interview_location is not None:
            application.interview_location = interview_location
        application.interview_notes = feedback

        db.session.commit()
        return {'message': 'Application status updated successfully'}

class UpdateDriveStatus(Resource):
    @role_required('company')
    def put(self, drive_id):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.status != 'approved':
            return {'message': 'Company not approved yet'}, 403

        data = request.get_json()
        status = data.get('status')
        is_active = data.get('is_active')

        drive = Placement_drive.query.filter_by(id=drive_id, company_id=company.id).first()
        if not drive:
            return {'message': 'Drive not found'}, 404

        if status:
            if status not in ['closed']:
                return {'message': 'Companies can only close drives. Status changes like approval are admin-only.'}, 400
            drive.status = status
        if is_active is not None:
            drive.is_active = is_active

        db.session.commit()
        return {'message': 'Drive status updated successfully'}


class CompanyInterviews(Resource):
    @role_required('company')
    def get(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.status != 'approved':
            return {'message': 'Company not approved yet'}, 403

        # Get all shortlisted applications with interview schedules across all company drives
        applications = Application.query.join(Placement_drive).filter(
            Placement_drive.company_id == company.id,
            Application.status == 'Shortlisted'
        ).order_by(Application.interview_schedule.asc()).all()

        interviews = []
        for app in applications:
            student = Student.query.get(app.student_id)
            drive = Placement_drive.query.get(app.drive_id)
            if student and drive:
                interviews.append({
                    'application_id': app.id,
                    'student': {
                        'id': student.id,
                        'full_name': student.full_name,
                        'email': student.email,
                        'roll_number': student.roll_number,
                        'college': student.college,
                        'branch': student.branch,
                        'cgpa': student.cgpa,
                        'year': student.year,
                        'resume_url': student.resume_url
                    },
                    'drive': {
                        'id': drive.id,
                        'job_title': drive.job_title,
                        'package_offered': drive.package_offered
                    },
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                    'shortlisted_at': app.shortlisted_at.isoformat() if app.shortlisted_at else None,
                    'interview_schedule': app.interview_schedule.isoformat() if app.interview_schedule else None,
                    'interview_mode': app.interview_mode,
                    'interview_location': app.interview_location,
                    'interview_notes': app.interview_notes
                })

        return {'interviews': interviews}


class CompanySelectedStudents(Resource):
    @role_required('company')
    def get(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.status != 'approved':
            return {'message': 'Company not approved yet'}, 403

        # Get all selected applications across all company drives
        applications = Application.query.join(Placement_drive).filter(
            Placement_drive.company_id == company.id,
            Application.status == 'Selected'
        ).order_by(Application.selected_at.desc()).all()

        selected = []
        for app in applications:
            student = Student.query.get(app.student_id)
            drive = Placement_drive.query.get(app.drive_id)
            if student and drive:
                selected.append({
                    'application_id': app.id,
                    'student': {
                        'id': student.id,
                        'full_name': student.full_name,
                        'email': student.email,
                        'roll_number': student.roll_number,
                        'college': student.college,
                        'branch': student.branch,
                        'cgpa': student.cgpa,
                        'year': student.year,
                        'resume_url': student.resume_url
                    },
                    'drive': {
                        'id': drive.id,
                        'job_title': drive.job_title,
                        'package_offered': drive.package_offered
                    },
                    'selected_at': app.selected_at.isoformat() if app.selected_at else None,
                    'interview_mode': app.interview_mode,
                    'interview_location': app.interview_location,
                    'interview_notes': app.interview_notes
                })

        return {'selected': selected}


class CompanyProfile(Resource):
    @role_required('company')
    def get(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.is_blacklisted:
            return {'message': 'Company is blacklisted'}, 403

        return {
            'id': company.id,
            'company_name': company.company_name,
            'email': company.email,
            'hr_name': company.hr_name,
            'website': company.website,
            'description': company.description,
            'address': company.address,
            'status': company.status
        }

    @role_required('company')
    def put(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.is_blacklisted:
            return {'message': 'Company is blacklisted'}, 403

        data = request.get_json()

        if 'company_name' in data and data['company_name'] != company.company_name:
            existing = Company.query.filter_by(company_name=data['company_name']).first()
            if existing:
                return {'message': 'Company name already exists'}, 400
            company.company_name = data['company_name']

        if 'website' in data and data['website'] != company.website:
            existing = Company.query.filter_by(website=data['website']).first()
            if existing:
                return {'message': 'Website already exists'}, 400
            company.website = data['website']

        if 'hr_name' in data:
            company.hr_name = data['hr_name']
        if 'description' in data:
            company.description = data['description']
        if 'address' in data:
            company.address = data['address']

        db.session.commit()
        return {'message': 'Profile updated successfully'}


class CompanySubmitApproval(Resource):
    @role_required('company')
    def post(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.is_blacklisted:
            return {'message': 'Company is blacklisted'}, 403

        if company.status == 'approved':
            return {'message': 'Company already approved'}, 200

        company.status = 'pending'
        db.session.commit()
        return {'message': 'Submitted for admin approval'}


class CompanyResults(Resource):
    @role_required('company')
    def get(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.status != 'approved':
            return {'message': 'Company not approved yet'}, 403

        applications = Application.query.join(Placement_drive).filter(
            Placement_drive.company_id == company.id,
            Application.status.in_(['Shortlisted', 'Selected', 'Rejected'])
        ).order_by(Application.applied_at.desc()).all()

        results = []
        for app in applications:
            student = Student.query.get(app.student_id)
            drive = Placement_drive.query.get(app.drive_id)
            if student and drive:
                results.append({
                    'application_id': app.id,
                    'status': app.status,
                    'student': {
                        'id': student.id,
                        'full_name': student.full_name,
                        'email': student.email,
                        'roll_number': student.roll_number,
                        'college': student.college,
                        'branch': student.branch,
                        'cgpa': student.cgpa,
                        'year': student.year,
                        'resume_url': student.resume_url
                    },
                    'drive': {
                        'id': drive.id,
                        'job_title': drive.job_title,
                        'package_offered': drive.package_offered
                    },
                    'selected_at': app.selected_at.isoformat() if app.selected_at else None,
                    'interview_notes': app.interview_notes
                })

        return {'results': results}