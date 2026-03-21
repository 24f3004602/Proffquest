from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from models import db, Student, Placement_drive, Application, Drive_eligibility
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from utils.decorators import role_required
from utils.cache import cache
from utils.notifications import notify
import json


def _serialize_eligibility(eligibilities):
    return [{
        'branch': el.branch,
        'min_cgpa': el.min_cgpa,
        'student_status': el.student_status,
        'passing_year': el.passing_year,
        'backlog_allowed': el.backlog_allowed,
        'additional_criteria': el.additional_criteria
    } for el in eligibilities]


def _is_profile_complete(student):
    required_fields = [
        student.full_name,
        student.email,
        student.roll_number,
        student.branch,
        student.cgpa,
        student.year,
        student.resume_url
    ]
    return all(required_fields)


class StudentDashboard(Resource):
    @role_required('student')
    @cache.cached(timeout=300)
    def get(self):
        identity = json.loads(get_jwt_identity())
        student_id = identity['id']
        student = Student.query.get_or_404(student_id)

        if student.is_blacklisted:
            return {'message': 'Your account has been blacklisted'}, 403

        # Count stats
        applications = Application.query.filter_by(student_id=student.id).all()
        total_applied = len(applications)
        shortlisted = sum(1 for a in applications if a.status == 'Shortlisted')
        interview = sum(1 for a in applications if a.status == 'Interview')
        offer = sum(1 for a in applications if a.status in ['Offer', 'Selected'])
        placed = sum(1 for a in applications if a.status == 'Placed')
        rejected = sum(1 for a in applications if a.status == 'Rejected')

        # Upcoming interviews
        upcoming_interviews = []
        for app in applications:
            if app.interview_schedule and app.status in ['Shortlisted', 'Interview']:
                drive = Placement_drive.query.get(app.drive_id)
                if drive:
                    upcoming_interviews.append({
                        'application_id': app.id,
                        'job_title': drive.job_title,
                        'company_name': drive.company.company_name,
                        'interview_schedule': app.interview_schedule.isoformat(),
                        'interview_notes': app.interview_notes
                    })

        # Recent applications (last 5)
        recent_apps = Application.query.filter_by(student_id=student.id)\
            .order_by(Application.applied_at.desc()).limit(5).all()
        recent_data = []
        for app in recent_apps:
            drive = Placement_drive.query.get(app.drive_id)
            if drive:
                recent_data.append({
                    'application_id': app.id,
                    'job_title': drive.job_title,
                    'company_name': drive.company.company_name,
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat() if app.applied_at else None
                })

        # Upcoming drives (approved, active, deadline not passed)
        upcoming_drives = Placement_drive.query.filter(
            Placement_drive.is_approved == True,
            Placement_drive.is_active == True,
            Placement_drive.application_deadline >= datetime.utcnow()
        ).order_by(Placement_drive.application_deadline.asc()).limit(5).all()

        drives_data = []
        for drive in upcoming_drives:
            # Check if already applied
            already_applied = Application.query.filter_by(
                student_id=student.id, drive_id=drive.id
            ).first() is not None

            deadline_passed = drive.application_deadline < datetime.utcnow()
            eligibilities = Drive_eligibility.query.filter_by(drive_id=drive.id).all()
            eligibility_info = _serialize_eligibility(eligibilities)

            drives_data.append({
                'id': drive.id,
                'job_title': drive.job_title,
                'company_name': drive.company.company_name,
                'package_offered': drive.package_offered,
                'application_deadline': drive.application_deadline.isoformat(),
                'already_applied': already_applied,
                'is_active': drive.is_active,
                'deadline_passed': deadline_passed,
                'eligibility': eligibility_info
            })

        return {
            'student': {
                'id': student.id,
                'full_name': student.full_name,
                'email': student.email,
                'college': student.college,
                'branch': student.branch,
                'year': student.year,
                'cgpa': student.cgpa
            },
            'stats': {
                'total_applied': total_applied,
                'shortlisted': shortlisted,
                'interview': interview,
                'offer': offer,
                'placed': placed,
                'rejected': rejected
            },
            'upcoming_interviews': upcoming_interviews,
            'recent_applications': recent_data,
            'upcoming_drives': drives_data
        }


class StudentProfile(Resource):
    @role_required('student')
    def get(self):
        identity = json.loads(get_jwt_identity())
        student_id = identity['id']
        student = Student.query.get_or_404(student_id)

        return {
            'id': student.id,
            'full_name': student.full_name,
            'email': student.email,
            'roll_number': student.roll_number,
            'college': student.college,
            'branch': student.branch,
            'cgpa': student.cgpa,
            'year': student.year,
            'resume_url': student.resume_url,
            'is_blacklisted': student.is_blacklisted
        }

    @role_required('student')
    def put(self):
        identity = json.loads(get_jwt_identity())
        student_id = identity['id']
        student = Student.query.get_or_404(student_id)

        if student.is_blacklisted:
            return {'message': 'Your account has been blacklisted'}, 403

        data = request.get_json()

        # Only allow updating certain fields
        if 'full_name' in data:
            student.full_name = data['full_name']
        if 'college' in data:
            student.college = data['college']
        if 'branch' in data:
            student.branch = data['branch']
        if 'cgpa' in data:
            student.cgpa = float(data['cgpa'])
        if 'year' in data:
            student.year = int(data['year'])
        if 'resume_url' in data:
            student.resume_url = data['resume_url']
        if 'roll_number' in data:
            # Check uniqueness
            existing = Student.query.filter(
                Student.roll_number == data['roll_number'],
                Student.id != student.id
            ).first()
            if existing:
                return {'message': 'Roll number already exists'}, 400
            student.roll_number = data['roll_number']

        db.session.commit()
        cache.clear()
        return {'message': 'Profile updated successfully'}


class StudentDrives(Resource):
    @role_required('student')
    @cache.cached(timeout=300)
    def get(self):
        identity = json.loads(get_jwt_identity())
        student_id = identity['id']
        student = Student.query.get_or_404(student_id)

        if student.is_blacklisted:
            return {'message': 'Your account has been blacklisted'}, 403

        # Get all approved and active drives
        drives = Placement_drive.query.filter(
            Placement_drive.is_approved == True,
            Placement_drive.is_active == True
        ).order_by(Placement_drive.application_deadline.asc()).all()

        drives_data = []
        for drive in drives:
            # Check if already applied
            already_applied = Application.query.filter_by(
                student_id=student.id, drive_id=drive.id
            ).first() is not None

            eligibilities = Drive_eligibility.query.filter_by(drive_id=drive.id).all()
            eligibility_info = _serialize_eligibility(eligibilities)
            eligible = _is_profile_complete(student)

            # Check if deadline passed
            deadline_passed = drive.application_deadline < datetime.utcnow()

            drives_data.append({
                'id': drive.id,
                'job_title': drive.job_title,
                'role': drive.role,
                'job_description': drive.job_description,
                'company_name': drive.company.company_name,
                'package_offered': drive.package_offered,
                'location': drive.location,
                'job_type': drive.job_type,
                'skills_required': drive.skills_required,
                'application_deadline': drive.application_deadline.isoformat(),
                'drive_date': drive.drive_date.isoformat(),
                'max_applicants': drive.max_applicants,
                'already_applied': already_applied,
                'eligible': eligible,
                'is_active': drive.is_active,
                'deadline_passed': deadline_passed,
                'eligibility': eligibility_info
            })

        return {'drives': drives_data}


class StudentApply(Resource):
    @role_required('student')
    def post(self, drive_id):
        identity = json.loads(get_jwt_identity())
        student_id = identity['id']
        student = Student.query.get_or_404(student_id)

        if student.is_blacklisted:
            return {'message': 'Your account has been blacklisted. You cannot apply.'}, 403

        drive = Placement_drive.query.get_or_404(drive_id)

        # Validations
        if not drive.is_approved or not drive.is_active:
            return {'message': 'This drive is not available for applications'}, 400

        if drive.application_deadline < datetime.utcnow():
            return {'message': 'Application deadline has passed'}, 400

        # Check duplicate application
        existing = Application.query.filter_by(
            student_id=student.id, drive_id=drive.id
        ).first()
        if existing:
            return {'message': 'You have already applied to this drive'}, 400

        # Check max applicants
        if drive.max_applicants:
            current_count = Application.query.filter_by(drive_id=drive.id).count()
            if current_count >= drive.max_applicants:
                return {'message': 'Maximum applicants reached for this drive'}, 400

        # Check eligibility (profile completion only)
        if not _is_profile_complete(student):
            return {'message': 'Complete your profile before applying'}, 400

        # Create application
        new_application = Application(
            student_id=student.id,
            drive_id=drive.id,
            status='Applied',
            resume_url=student.resume_url
        )
        try:
            db.session.add(new_application)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'message': 'You have already applied to this drive'}, 400

        cache.clear()

        # Notify student and company about the application
        notify(
            student.email,
            'Application Submitted',
            f'You have successfully applied to "{drive.job_title}" at {drive.company.company_name}.'
        )
        notify(
            drive.company.email,
            'New Application Received',
            f'{student.full_name} has applied to your drive "{drive.job_title}".'
        )

        return {'message': 'Application submitted successfully', 'application_id': new_application.id}, 201


class StudentApplications(Resource):
    @role_required('student')
    def get(self):
        identity = json.loads(get_jwt_identity())
        student_id = identity['id']
        student = Student.query.get_or_404(student_id)

        applications = Application.query.filter_by(student_id=student.id)\
            .order_by(Application.applied_at.desc()).all()

        apps_data = []
        for app in applications:
            drive = Placement_drive.query.get(app.drive_id)
            if drive:
                apps_data.append({
                    'application_id': app.id,
                    'drive_id': drive.id,
                    'job_title': drive.job_title,
                    'company_name': drive.company.company_name,
                    'package_offered': drive.package_offered,
                    'location': drive.location,
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                    'shortlisted_at': app.shortlisted_at.isoformat() if app.shortlisted_at else None,
                    'interview_at': app.interview_at.isoformat() if app.interview_at else None,
                    'offer_at': app.offer_at.isoformat() if app.offer_at else None,
                    'placed_at': app.placed_at.isoformat() if app.placed_at else None,
                    'selected_at': app.selected_at.isoformat() if app.selected_at else None,
                    'interview_schedule': app.interview_schedule.isoformat() if app.interview_schedule else None,
                    'interview_notes': app.interview_notes
                })

        return {'applications': apps_data}
