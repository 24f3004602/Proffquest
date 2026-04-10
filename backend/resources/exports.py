import json
import os
import csv
from datetime import datetime

from flask import send_file
from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource

from models import Application, Company, Placement_drive, Student
from utils.decorators import role_required


_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_student_applications_export(student_id):
    student = Student.query.get(student_id)
    if not student:
        raise ValueError("Student not found")

    export_dir = os.path.join(_BASE_DIR, "exports", f"student_{student.id}")
    os.makedirs(export_dir, exist_ok=True)
    filename = f"applications_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    file_path = os.path.join(export_dir, filename)

    applications = Application.query.filter_by(student_id=student.id).order_by(
        Application.applied_at.desc()
    ).all()

    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "application_id",
            "job_title",
            "company_name",
            "status",
            "applied_at",
            "interview_schedule",
            "offer_at",
            "placed_at",
        ])
        for app in applications:
            drive = Placement_drive.query.get(app.drive_id)
            writer.writerow([
                app.id,
                drive.job_title if drive else "",
                drive.company.company_name if drive else "",
                app.status,
                app.applied_at.isoformat() if app.applied_at else "",
                app.interview_schedule.isoformat() if app.interview_schedule else "",
                app.offer_at.isoformat() if app.offer_at else "",
                app.placed_at.isoformat() if app.placed_at else "",
            ])

    return file_path


def generate_company_applications_export(company_id):
    company = Company.query.get(company_id)
    if not company:
        raise ValueError("Company not found")

    export_dir = os.path.join(_BASE_DIR, "exports", f"company_{company.id}")
    os.makedirs(export_dir, exist_ok=True)
    filename = f"applications_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    file_path = os.path.join(export_dir, filename)

    applications = Application.query.join(Placement_drive).filter(
        Placement_drive.company_id == company.id
    ).order_by(Application.applied_at.desc()).all()

    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "application_id",
            "student_name",
            "student_email",
            "drive_title",
            "status",
            "applied_at",
            "interview_schedule",
            "offer_at",
            "placed_at",
        ])
        for app in applications:
            student = Student.query.get(app.student_id)
            drive = Placement_drive.query.get(app.drive_id)
            writer.writerow([
                app.id,
                student.full_name if student else "",
                student.email if student else "",
                drive.job_title if drive else "",
                app.status,
                app.applied_at.isoformat() if app.applied_at else "",
                app.interview_schedule.isoformat() if app.interview_schedule else "",
                app.offer_at.isoformat() if app.offer_at else "",
                app.placed_at.isoformat() if app.placed_at else "",
            ])

    return file_path


def _company_report_folder(company_id):
    return os.path.join(_BASE_DIR, "reports", f"company_{company_id}")


def _list_company_reports_from_files(company_id):
    folder = _company_report_folder(company_id)
    if not os.path.isdir(folder):
        return []

    reports = []
    for item in os.listdir(folder):
        report_dir = os.path.join(folder, item)
        if not os.path.isdir(report_dir):
            continue

        parts = item.split("_")
        if len(parts) != 2:
            continue

        try:
            year = int(parts[0])
            month = int(parts[1])
        except ValueError:
            continue

        if month < 1 or month > 12:
            continue

        html_path = os.path.join(report_dir, "report.html")
        pdf_path = os.path.join(report_dir, "report.pdf")
        has_html = os.path.exists(html_path)
        has_pdf = os.path.exists(pdf_path)

        if not has_html and not has_pdf:
            continue

        completed_at = None
        if has_pdf:
            completed_at = datetime.utcfromtimestamp(os.path.getmtime(pdf_path)).isoformat()
        elif has_html:
            completed_at = datetime.utcfromtimestamp(os.path.getmtime(html_path)).isoformat()

        reports.append(
            {
                "id": year * 100 + month,
                "month": month,
                "year": year,
                "status": "completed",
                "html_path": html_path if has_html else None,
                "pdf_path": pdf_path if has_pdf else None,
                "error": None,
                "created_at": completed_at,
                "completed_at": completed_at,
            }
        )

    reports.sort(key=lambda report: (report["year"], report["month"]), reverse=True)
    return reports


class StudentExportApplications(Resource):
    @role_required("student")
    def post(self):
        identity = json.loads(get_jwt_identity())
        student_id = identity["id"]

        try:
            file_path = generate_student_applications_export(student_id)
        except ValueError as exc:
            return {"message": str(exc)}, 404
        except Exception as exc:
            return {"message": "Failed to export applications", "error": str(exc)}, 500

        return send_file(file_path, as_attachment=True)


class CompanyExportApplications(Resource):
    @role_required("company")
    def post(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity["id"]

        try:
            file_path = generate_company_applications_export(company_id)
        except ValueError as exc:
            return {"message": str(exc)}, 404
        except Exception as exc:
            return {"message": "Failed to export applications", "error": str(exc)}, 500

        return send_file(file_path, as_attachment=True)


class CompanyReportsList(Resource):
    @role_required("company")
    def get(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity["id"]

        return {"reports": _list_company_reports_from_files(company_id)}


class CompanyReportDownload(Resource):
    @role_required("company")
    def get(self, report_id):
        identity = json.loads(get_jwt_identity())
        company_id = identity["id"]

        year = report_id // 100
        month = report_id % 100
        if month < 1 or month > 12:
            return {"message": "Report not found"}, 404

        report_dir = os.path.join(_company_report_folder(company_id), f"{year}_{month:02d}")
        pdf_path = os.path.join(report_dir, "report.pdf")
        html_path = os.path.join(report_dir, "report.html")
        file_path = pdf_path if os.path.exists(pdf_path) else html_path

        if not os.path.exists(file_path):
            return {"message": "Report file missing"}, 404

        return send_file(file_path, as_attachment=True)
