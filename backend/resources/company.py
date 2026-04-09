from flask import request, Response
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from models import db, Company, Placement_drive, Application, Student, Drive_eligibility
from datetime import datetime
import csv
from io import StringIO
from utils.decorators import role_required
from utils.cache import cache
from utils.notifications import notify, send_gchat, GCHAT_URL
import json

class CompanyDashboard(Resource):
    @role_required('company')
    @cache.cached(timeout=300)
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
        interview_count = 0
        offer_count = 0
        placed_count = 0

        for drive in drives:
            applications = Application.query.filter_by(drive_id=drive.id).all()
            applicant_count = len(applications)
            total_applications += applicant_count

            # Count shortlisted, interviews, offers, and placements
            for app in applications:
                if app.status == 'Shortlisted':
                    shortlisted_count += 1
                elif app.status == 'Interview':
                    interview_count += 1
                elif app.status in ['Offer', 'Selected']:
                    offer_count += 1
                elif app.status == 'Placed':
                    placed_count += 1

            drives_data.append({
                'id': drive.id,
                'job_title': drive.job_title,
                'job_description': drive.job_description,
                'package_offered': drive.package_offered,
                'role': drive.role,
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
                'email': company.email,
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
                'interview': interview_count,
                'offer': offer_count,
                'placed': placed_count
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
            role=data.get('role'),
            job_description=data['job_description'],
            package_offered=data['package_offered'],
            location=data['location'],
            job_type=data.get('job_type', 'Full-time'),
            skills_required=data.get('skills_required'),
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
                student_status=el.get('student_status', 'studying'),
                passing_year=el.get('passing_year'),
                backlog_allowed=el.get('backlog_allowed', False),
                additional_criteria=el.get('additional_criteria', '')
            )
            db.session.add(eligibility)

        db.session.commit()
        cache.clear()
        send_gchat(GCHAT_URL, f'New Placement Drive Created: "{new_drive.job_title}" by {company.company_name} (pending approval)')
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
                'role': drive.role,
                'job_description': drive.job_description,
                'package_offered': drive.package_offered,
                'location': drive.location,
                'job_type': drive.job_type,
                'skills_required': drive.skills_required,
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
                'interview_at': app.interview_at.isoformat() if app.interview_at else None,
                'offer_at': app.offer_at.isoformat() if app.offer_at else None,
                'placed_at': app.placed_at.isoformat() if app.placed_at else None,
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

        if status not in ['Applied', 'Shortlisted', 'Interview', 'Offer', 'Rejected', 'Placed', 'Selected']:
            return {'message': 'Invalid status'}, 400

        if status == 'Selected':
            status = 'Offer'

        application = Application.query.filter_by(id=application_id).first()
        if not application:
            return {'message': 'Application not found'}, 404

        drive = Placement_drive.query.filter_by(id=application.drive_id, company_id=company.id).first()
        if not drive:
            return {'message': 'Unauthorized'}, 403

        current_status = application.status
        if current_status == 'Selected':
            current_status = 'Offer'

        allowed_transitions = {
            'Applied': {'Shortlisted', 'Rejected'},
            'Shortlisted': {'Interview', 'Rejected'},
            'Interview': {'Offer', 'Rejected'},
            'Offer': {'Placed'}
        }

        if status != current_status:
            valid_next = allowed_transitions.get(current_status, set())
            if status not in valid_next:
                if current_status in ['Rejected', 'Placed']:
                    return {'message': f'Cannot update application once it is {current_status.lower()}'}, 400
                return {
                    'message': f'Invalid status transition from {current_status} to {status}'
                }, 400

        application.status = status
        if status == 'Shortlisted':
            application.shortlisted_at = application.shortlisted_at or datetime.utcnow()
        elif status == 'Interview':
            application.interview_at = application.interview_at or datetime.utcnow()
        elif status == 'Offer':
            application.offer_at = application.offer_at or datetime.utcnow()
            application.selected_at = application.selected_at or application.offer_at
        elif status == 'Placed':
            application.placed_at = application.placed_at or datetime.utcnow()
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
        cache.clear()

        # Send notification to student about status change
        student = Student.query.get(application.student_id)
        drive = Placement_drive.query.get(application.drive_id)
        if student and drive:
            status_messages = {
                'Shortlisted': f'Congratulations! You have been shortlisted for "{drive.job_title}" at {company.company_name}.',
                'Interview': f'You have been scheduled for an interview for "{drive.job_title}" at {company.company_name}.' + (f' Interview: {interview_schedule}' if interview_schedule else ''),
                'Offer': f'Congratulations! You have received an offer for "{drive.job_title}" at {company.company_name}!',
                'Rejected': f'Your application for "{drive.job_title}" at {company.company_name} was not selected.',
                'Placed': f'Congratulations! You have been placed at {company.company_name} for "{drive.job_title}"!',
            }
            msg = status_messages.get(status, f'Your application status for "{drive.job_title}" has been updated to {status}.')
            notify(student.email, f'Application Update - {status}', msg)

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
        cache.clear()
        if status == 'closed':
            send_gchat(GCHAT_URL, f'Drive Closed: "{drive.job_title}" by {company.company_name} has been closed.')
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
            Application.status.in_(['Shortlisted', 'Interview'])
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
        cache.clear()
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
        cache.clear()
        send_gchat(GCHAT_URL, f'Company Approval Request: "{company.company_name}" has submitted for admin approval.')
        return {'message': 'Submitted for admin approval'}


class CompanyStudentProfile(Resource):
    @role_required('company')
    def get(self, student_id):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.status != 'approved':
            return {'message': 'Company not approved yet'}, 403

        has_application = Application.query.join(Placement_drive).filter(
            Placement_drive.company_id == company.id,
            Application.student_id == student_id
        ).first()
        if not has_application:
            return {'message': 'Student not found for this company'}, 404

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
            'resume_url': student.resume_url
        }


class CompanyStudentApplications(Resource):
    @role_required('company')
    def get(self, student_id):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.status != 'approved':
            return {'message': 'Company not approved yet'}, 403

        applications = Application.query.join(Placement_drive).filter(
            Placement_drive.company_id == company.id,
            Application.student_id == student_id
        ).order_by(Application.applied_at.desc()).all()

        if not applications:
            return {'message': 'No applications found for this student'}, 404

        apps_data = []
        for app in applications:
            drive = Placement_drive.query.get(app.drive_id)
            if drive:
                apps_data.append({
                    'application_id': app.id,
                    'drive_id': drive.id,
                    'job_title': drive.job_title,
                    'package_offered': drive.package_offered,
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                    'shortlisted_at': app.shortlisted_at.isoformat() if app.shortlisted_at else None,
                    'interview_at': app.interview_at.isoformat() if app.interview_at else None,
                    'interview_schedule': app.interview_schedule.isoformat() if app.interview_schedule else None,
                    'offer_at': app.offer_at.isoformat() if app.offer_at else None,
                    'placed_at': app.placed_at.isoformat() if app.placed_at else None,
                    'interview_notes': app.interview_notes
                })

        return {'applications': apps_data}


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
            Application.status.in_(['Shortlisted', 'Interview', 'Offer', 'Rejected', 'Placed', 'Selected'])
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
                    'offer_at': app.offer_at.isoformat() if app.offer_at else None,
                    'placed_at': app.placed_at.isoformat() if app.placed_at else None,
                    'interview_notes': app.interview_notes
                })

        return {'results': results}


class CompanyResultsCSV(Resource):
    @role_required('company')
    def get(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        if company.status != 'approved':
            return {'message': 'Company not approved yet'}, 403

        applications = Application.query.join(Placement_drive).filter(
            Placement_drive.company_id == company.id,
            Application.status.in_(['Shortlisted', 'Interview', 'Offer', 'Rejected', 'Placed', 'Selected'])
        ).order_by(Application.applied_at.desc()).all()

        stream = StringIO()
        writer = csv.writer(stream)
        writer.writerow([
            'application_id',
            'status',
            'student_id',
            'student_name',
            'student_email',
            'roll_number',
            'college',
            'branch',
            'cgpa',
            'year',
            'drive_id',
            'job_title',
            'package_offered',
            'applied_at',
            'shortlisted_at',
            'interview_at',
            'offer_at',
            'placed_at',
            'selected_at',
            'interview_mode',
            'interview_location',
            'interview_notes',
        ])

        for app in applications:
            student = Student.query.get(app.student_id)
            drive = Placement_drive.query.get(app.drive_id)
            if not student or not drive:
                continue

            writer.writerow([
                app.id,
                app.status,
                student.id,
                student.full_name,
                student.email,
                student.roll_number,
                student.college,
                student.branch,
                student.cgpa,
                student.year,
                drive.id,
                drive.job_title,
                drive.package_offered,
                app.applied_at.isoformat() if app.applied_at else '',
                app.shortlisted_at.isoformat() if app.shortlisted_at else '',
                app.interview_at.isoformat() if app.interview_at else '',
                app.offer_at.isoformat() if app.offer_at else '',
                app.placed_at.isoformat() if app.placed_at else '',
                app.selected_at.isoformat() if app.selected_at else '',
                app.interview_mode or '',
                app.interview_location or '',
                app.interview_notes or '',
            ])

        filename = f"company_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        return Response(
            stream.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'},
        )


class DriveDetail(Resource):
    @role_required('company')
    def get(self, drive_id):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        
        drive = Placement_drive.query.filter_by(id=drive_id, company_id=company.id).first()
        if not drive:
            return {'message': 'Drive not found'}, 404

        eligibilities = Drive_eligibility.query.filter_by(drive_id=drive.id).all()
        eligibility_data = [{
            'branch': el.branch,
            'min_cgpa': el.min_cgpa,
            'student_status': el.student_status,
            'passing_year': el.passing_year,
            'backlog_allowed': el.backlog_allowed,
            'additional_criteria': el.additional_criteria
        } for el in eligibilities]

        return {
            'drive': {
                'id': drive.id,
                'job_title': drive.job_title,
                'role': drive.role,
                'job_description': drive.job_description,
                'package_offered': drive.package_offered,
                'location': drive.location,
                'job_type': drive.job_type,
                'skills_required': drive.skills_required,
                'rounds': drive.rounds,
                'application_deadline': drive.application_deadline.isoformat() if drive.application_deadline else None,
                'drive_date': drive.drive_date.isoformat() if drive.drive_date else None,
                'max_applicants': drive.max_applicants,
                'eligibility': eligibility_data
            }
        }

    @role_required('company')
    def put(self, drive_id):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        company = Company.query.get_or_404(company_id)
        
        drive = Placement_drive.query.filter_by(id=drive_id, company_id=company.id).first()
        if not drive:
            return {'message': 'Drive not found'}, 404

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

        # Update drive fields
        drive.job_title = data['job_title']
        drive.role = data.get('role')
        drive.job_description = data['job_description']
        drive.package_offered = data['package_offered']
        drive.location = data['location']
        drive.job_type = data.get('job_type', 'Full-time')
        drive.skills_required = data.get('skills_required')
        drive.rounds = data.get('rounds')
        drive.application_deadline = deadline
        drive.drive_date = drive_date
        drive.max_applicants = data.get('max_applicants')

        # Update eligibility criteria - delete old ones and add new ones
        Drive_eligibility.query.filter_by(drive_id=drive.id).delete()
        
        eligibility_data = data.get('eligibility', [])
        for el in eligibility_data:
            eligibility = Drive_eligibility(
                drive_id=drive.id,
                branch=el.get('branch'),
                min_cgpa=el.get('min_cgpa', 0.0),
                student_status=el.get('student_status', ''),
                passing_year=el.get('passing_year'),
                backlog_allowed=el.get('backlog_allowed', False),
                additional_criteria=el.get('additional_criteria', '')
            )
            db.session.add(eligibility)

        db.session.commit()
        cache.clear()
        return {'message': 'Drive updated successfully'}, 200