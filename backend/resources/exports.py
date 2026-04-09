import json
import os
from flask import send_file
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from tasks import export_student_applications,export_company_applications
from models import db, ExportJob, PlacementReport
from utils.decorators import role_required


def _should_use_async_exports():
    return os.getenv("CELERY_EXPORT_ASYNC", "0").strip().lower() in {"1", "true", "yes", "on"}


def _dispatch_export_task(task, job):
    if _should_use_async_exports():
        try:
            task.delay(job.id)
            return
        except Exception:
            pass

    task(job.id)


class StudentExportApplications(Resource):
    @role_required('student')
    def post(self):
        identity = json.loads(get_jwt_identity())
        student_id = identity['id']

        job = ExportJob(
            requester_role='student',
            requester_id=student_id,
            job_type='student_applications',
            status='queued'
        )
        db.session.add(job)
        db.session.commit()

        _dispatch_export_task(export_student_applications, job)
        db.session.refresh(job)
        return {
            'job_id': job.id,
            'status': job.status,
            'file_path': job.file_path,
            'error': job.error,
        }, 202


class CompanyExportApplications(Resource):
    @role_required('company')
    def post(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']

        job = ExportJob(
            requester_role='company',
            requester_id=company_id,
            job_type='company_applications',
            status='queued'
        )
        db.session.add(job)
        db.session.commit()

        _dispatch_export_task(export_company_applications, job)
        db.session.refresh(job)
        return {
            'job_id': job.id,
            'status': job.status,
            'file_path': job.file_path,
            'error': job.error,
        }, 202


class StudentExportJobs(Resource):
    @role_required('student')
    def get(self):
        identity = json.loads(get_jwt_identity())
        student_id = identity['id']

        jobs = ExportJob.query.filter_by(
            requester_role='student', requester_id=student_id
        ).order_by(ExportJob.created_at.desc()).all()

        return {
            'jobs': [
                {
                    'id': job.id,
                    'job_type': job.job_type,
                    'status': job.status,
                    'file_path': job.file_path,
                    'error': job.error,
                    'created_at': job.created_at.isoformat() if job.created_at else None,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                }
                for job in jobs
            ]
        }


class CompanyExportJobs(Resource):
    @role_required('company')
    def get(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']

        jobs = ExportJob.query.filter_by(
            requester_role='company', requester_id=company_id
        ).order_by(ExportJob.created_at.desc()).all()

        return {
            'jobs': [
                {
                    'id': job.id,
                    'job_type': job.job_type,
                    'status': job.status,
                    'file_path': job.file_path,
                    'error': job.error,
                    'created_at': job.created_at.isoformat() if job.created_at else None,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                }
                for job in jobs
            ]
        }


class StudentExportDownload(Resource):
    @role_required('student')
    def get(self, job_id):
        identity = json.loads(get_jwt_identity())
        student_id = identity['id']

        job = ExportJob.query.filter_by(
            id=job_id, requester_role='student', requester_id=student_id
        ).first_or_404()

        if job.status != 'completed' or not job.file_path:
            return {'message': 'Export not ready'}, 400
        if not os.path.exists(job.file_path):
            return {'message': 'Export file missing'}, 404

        return send_file(job.file_path, as_attachment=True)


class CompanyExportDownload(Resource):
    @role_required('company')
    def get(self, job_id):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']

        job = ExportJob.query.filter_by(
            id=job_id, requester_role='company', requester_id=company_id
        ).first_or_404()

        if job.status != 'completed' or not job.file_path:
            return {'message': 'Export not ready'}, 400
        if not os.path.exists(job.file_path):
            return {'message': 'Export file missing'}, 404

        return send_file(job.file_path, as_attachment=True)


class CompanyReportsList(Resource):
    @role_required('company')
    def get(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']

        reports = PlacementReport.query.filter_by(
            company_id=company_id
        ).order_by(PlacementReport.created_at.desc()).all()

        return {
            'reports': [
                {
                    'id': report.id,
                    'month': report.report_month,
                    'year': report.report_year,
                    'status': report.status,
                    'html_path': report.html_path,
                    'pdf_path': report.pdf_path,
                    'error': report.error,
                    'created_at': report.created_at.isoformat() if report.created_at else None,
                    'completed_at': report.completed_at.isoformat() if report.completed_at else None,
                }
                for report in reports
            ]
        }


class CompanyReportDownload(Resource):
    @role_required('company')
    def get(self, report_id):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']

        report = PlacementReport.query.filter_by(
            id=report_id, company_id=company_id
        ).first_or_404()

        file_path = report.pdf_path or report.html_path
        if report.status != 'completed' or not file_path:
            return {'message': 'Report not ready'}, 400
        if not os.path.exists(file_path):
            return {'message': 'Report file missing'}, 404

        return send_file(file_path, as_attachment=True)
