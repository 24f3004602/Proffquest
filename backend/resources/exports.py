import json
import os
from datetime import datetime

from flask import send_file
from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource

from tasks import generate_company_applications_export, generate_student_applications_export
from utils.decorators import role_required


_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
