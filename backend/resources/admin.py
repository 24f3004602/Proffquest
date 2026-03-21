from flask_restful import Resource
from models import *
from utils.decorators import role_required
from utils.cache import cache, make_search_cache_key
from utils.notifications import notify
from flask import request, Response
from sqlalchemy import or_
from datetime import datetime
import csv
from io import StringIO


def _serialize_company(company):
    return {
        'id': company.id,
        'company_name': company.company_name,
        'status': company.status,
        'is_blacklisted': company.is_blacklisted,
        'email': company.email,
        'hr_name': company.hr_name,
        'website': company.website,
        'description': company.description
    }


def _serialize_student(student):
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


class AdminDashboardStats(Resource):
    @role_required('admin')
    @cache.cached(timeout=300)
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
            cache.clear()
            notify(
                company.email,
                'Company Approved',
                f'Your company "{company.company_name}" has been approved. You can now create placement drives.'
            )
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
            cache.clear()
            notify(
                company.email,
                'Company Registration Rejected',
                f'Your company "{company.company_name}" registration has been rejected by the admin.'
            )
            return {'message':'Company rejected successfully'},200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to reject company', 'error': str(e)}, 500
    
class AdminCompaniesList(Resource):
    @role_required('admin')
    @cache.cached(timeout=300)
    def get(self):
        companies=Company.query.all()
        return [_serialize_company(c) for c in companies], 200
    
class BlacklistCompany(Resource):
    @role_required('admin')
    def post(self,company_id):
        company=Company.query.get_or_404(company_id)
        company.is_blacklisted=True
        db.session.commit()
        cache.clear()
        notify(
            company.email,
            'Company Blacklisted',
            f'Your company "{company.company_name}" has been blacklisted. Contact admin for details.'
        )
        return {'message':'Company blacklisted successfully'},200

class ActiveCompany(Resource):
    @role_required('admin')
    def post(self,company_id):
        company=Company.query.get_or_404(company_id)
        company.is_blacklisted=False
        db.session.commit()
        cache.clear()
        notify(
            company.email,
            'Company Activated',
            f'Your company "{company.company_name}" has been re-activated. You can now use the platform again.'
        )
        return {'message':'Company activated successfully'},200

class SearchCompanies(Resource):
    @role_required('admin')
    @cache.cached(timeout=300, make_cache_key=make_search_cache_key)
    def get(self):
        query = request.args.get('q', '')
        companies = Company.query.filter(
            or_(
                Company.company_name.ilike(f'%{query}%'),
                Company.description.ilike(f'%{query}%'),
                Company.email.ilike(f'%{query}%')
            )
        ).all()
        return [_serialize_company(c) for c in companies], 200


class RemoveCompany(Resource):
    @role_required('admin')
    def delete(self, company_id):
        company = Company.query.get_or_404(company_id)
        try:
            drives = Placement_drive.query.filter_by(company_id=company_id).all()
            drive_ids = [drive.id for drive in drives]

            PlacementReport.query.filter_by(company_id=company_id).delete(synchronize_session=False)
            ExportJob.query.filter_by(requester_role='company', requester_id=company_id).delete(synchronize_session=False)

            if drive_ids:
                Drive_eligibility.query.filter(Drive_eligibility.drive_id.in_(drive_ids)).delete(synchronize_session=False)
                Application.query.filter(Application.drive_id.in_(drive_ids)).delete(synchronize_session=False)
            Placement_drive.query.filter_by(company_id=company_id).delete(synchronize_session=False)

            db.session.delete(company)
            db.session.commit()
            cache.clear()
            return {'message': 'Company removed successfully'}, 200
        except Exception as exc:
            db.session.rollback()
            return {'message': 'Failed to remove company', 'error': str(exc)}, 500

class SearchStudents(Resource):
    @role_required('admin')
    @cache.cached(timeout=300, make_cache_key=make_search_cache_key)
    def get(self):
        query = request.args.get('q', '')
        students = Student.query.filter(
            or_(
                Student.full_name.ilike(f'%{query}%'),
                Student.roll_number.ilike(f'%{query}%'),
                Student.email.ilike(f'%{query}%')
            )
        ).all()
        return [_serialize_student(s) for s in students], 200


class AdminPlacementDrives(Resource):
    @role_required('admin')
    @cache.cached(timeout=300)
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
        cache.clear()
        company = drive.company
        notify(
            company.email,
            'Placement Drive Approved',
            f'Your placement drive "{drive.job_title}" has been approved and is now visible to students.'
        )
        return {'message':'Placement drive approved successfully'},200

class RejectPlacementDrive(Resource):
    @role_required('admin')
    def post(self,drive_id):
        drive=Placement_drive.query.get_or_404(drive_id)
        drive.status='rejected'
        drive.is_approved=False
        db.session.commit()
        cache.clear()
        company = drive.company
        notify(
            company.email,
            'Placement Drive Rejected',
            f'Your placement drive "{drive.job_title}" has been rejected by the admin.'
        )
        return {'message':'Placement drive rejected successfully'},200

class AdminApplications(Resource):
    @role_required('admin')
    @cache.cached(timeout=300)
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
                'interview_at':app.interview_at.isoformat() if app.interview_at else None,
                'offer_at':app.offer_at.isoformat() if app.offer_at else None,
                'placed_at':app.placed_at.isoformat() if app.placed_at else None,
                'selected_at':app.selected_at.isoformat() if app.selected_at else None
            } for app in applications
        ],200


class AdminStudentProfile(Resource):
    @role_required('admin')
    def get(self, student_id=None):
        if student_id is None:
            students = Student.query.all()
            return [_serialize_student(s) for s in students], 200

        student = Student.query.get_or_404(student_id)
        return _serialize_student(student), 200

    @role_required('admin')
    def delete(self, student_id):
        student = Student.query.get_or_404(student_id)
        try:
            Application.query.filter_by(student_id=student_id).delete(synchronize_session=False)
            db.session.delete(student)
            db.session.commit()
            cache.clear()
            return {'message': 'Student removed successfully'}, 200
        except Exception as exc:
            db.session.rollback()
            return {'message': 'Failed to remove student', 'error': str(exc)}, 500


class AdminStudentApplications(Resource):
    @role_required('admin')
    def get(self, student_id):
        applications = Application.query.filter_by(student_id=student_id)
        apps_data = []
        for app in applications.order_by(Application.applied_at.desc()).all():
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
                    'interview_schedule': app.interview_schedule.isoformat() if app.interview_schedule else None,
                    'offer_at': app.offer_at.isoformat() if app.offer_at else None,
                    'placed_at': app.placed_at.isoformat() if app.placed_at else None
                })

        return {'applications': apps_data}, 200

class BlacklistStudent(Resource):
    @role_required('admin')
    def post(self,student_id):
        student=Student.query.get_or_404(student_id)
        student.is_blacklisted=True
        db.session.commit()
        cache.clear()
        notify(
            student.email,
            'Account Blacklisted',
            f'Your student account ({student.full_name}) has been blacklisted. Contact admin for details.'
        )
        return {'message':'Student blacklisted successfully'},200

class ActivateStudent(Resource):
    @role_required('admin')
    def post(self,student_id):
        student=Student.query.get_or_404(student_id)
        student.is_blacklisted=False
        db.session.commit()
        cache.clear()
        notify(
            student.email,
            'Account Activated',
            f'Your student account ({student.full_name}) has been re-activated. You can now use the platform again.'
        )
        return {'message':'Student activated successfully'},200


class AdminDetailedReportCSV(Resource):
    @role_required('admin')
    def get(self):
        applications = Application.query.order_by(Application.applied_at.desc()).all()

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
            'company_id',
            'company_name',
            'company_email',
            'drive_id',
            'job_title',
            'package_offered',
            'location',
            'drive_status',
            'applied_at',
            'shortlisted_at',
            'interview_at',
            'interview_schedule',
            'offer_at',
            'placed_at',
            'selected_at',
            'interview_mode',
            'interview_location',
            'interview_notes',
        ])

        for app in applications:
            student = app.student
            drive = app.placement_drive
            company = drive.company if drive else None

            writer.writerow([
                app.id,
                app.status,
                student.id if student else '',
                student.full_name if student else '',
                student.email if student else '',
                student.roll_number if student else '',
                student.college if student else '',
                student.branch if student else '',
                student.cgpa if student else '',
                student.year if student else '',
                company.id if company else '',
                company.company_name if company else '',
                company.email if company else '',
                drive.id if drive else '',
                drive.job_title if drive else '',
                drive.package_offered if drive else '',
                drive.location if drive else '',
                drive.status if drive else '',
                app.applied_at.isoformat() if app.applied_at else '',
                app.shortlisted_at.isoformat() if app.shortlisted_at else '',
                app.interview_at.isoformat() if app.interview_at else '',
                app.interview_schedule.isoformat() if app.interview_schedule else '',
                app.offer_at.isoformat() if app.offer_at else '',
                app.placed_at.isoformat() if app.placed_at else '',
                app.selected_at.isoformat() if app.selected_at else '',
                app.interview_mode or '',
                app.interview_location or '',
                app.interview_notes or '',
            ])

        filename = f"admin_detailed_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        return Response(
            stream.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'},
        )