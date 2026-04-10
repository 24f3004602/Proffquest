import os
from datetime import datetime, timedelta

from celery_app import celery
from models import *
from utils.notifications import send_gchat, send_email, GCHAT_URL
from utils.reports import render_report_html, render_report_pdf


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@celery.task(name="tasks.send_email_notification")
def send_email_notification(to_email, subject, body):
    return send_email(to_email, subject, body)


def _queue_email_notification(to_email, subject, body):
    if not to_email:
        return
    try:
        send_email_notification.delay(to_email, subject, body)
    except Exception:
        send_email_notification(to_email, subject, body)


@celery.task(name="tasks.send_interview_reminders")
def send_interview_reminders():
    now = datetime.utcnow()
    window_end = now + timedelta(hours=24)

    applications = Application.query.filter(
        Application.interview_schedule.isnot(None),
        Application.interview_schedule >= now,
        Application.interview_schedule < window_end,
        Application.status.in_(["Shortlisted", "Interview"]),
    ).all()

    for app in applications:
        if app.interview_reminder_sent_at:
            continue
        student = Student.query.get(app.student_id)
        drive = Placement_drive.query.get(app.drive_id)
        if not student or student.is_blacklisted or not drive:
            continue

        send_gchat(GCHAT_URL,
            f"Interview Reminder: {drive.job_title} at {drive.company.company_name} on "
            f"{app.interview_schedule.isoformat()} for {student.full_name}"
        )
        _queue_email_notification(
            student.email,
            f"Interview Reminder: {drive.job_title}",
            f"Dear {student.full_name},\n\nThis is a reminder that your interview for "
            f"\"{drive.job_title}\" at {drive.company.company_name} is scheduled on "
            f"{app.interview_schedule.strftime('%Y-%m-%d %H:%M')}.\n\nGood luck!"
        )

        app.interview_reminder_sent_at = now

    db.session.commit()

@celery.task(name="tasks.generate_monthly_placement_reports")
def generate_monthly_placement_reports():
    today = datetime.utcnow().date()
    first_of_this_month = datetime(today.year, today.month, 1)
    target_date = first_of_this_month - timedelta(days=1)
    start_date = datetime(target_date.year, target_date.month, 1)
    end_date = datetime(target_date.year + 1, 1, 1) if target_date.month == 12 else datetime(target_date.year, target_date.month + 1, 1)

    companies = Company.query.filter_by(status="approved", is_blacklisted=False).all()

    for company in companies:
        try:
            report_dir = os.path.join(
                _BASE_DIR, "reports", f"company_{company.id}", f"{target_date.year}_{target_date.month:02d}"
            )
            os.makedirs(report_dir, exist_ok=True)
            html_path = os.path.join(report_dir, "report.html")
            pdf_path = os.path.join(report_dir, "report.pdf")

            # Report file already exists for this month; skip regenerating.
            if os.path.exists(html_path) or os.path.exists(pdf_path):
                continue

            # Build report data
            drives = Placement_drive.query.filter_by(company_id=company.id).all()
            drive_ids = [d.id for d in drives]
            applications = Application.query.filter(
                Application.drive_id.in_(drive_ids),
                Application.applied_at >= start_date,
                Application.applied_at < end_date,
            ).all() if drive_ids else []

            stats = {
                "total_applications": len(applications),
                "shortlisted": sum(1 for a in applications if a.status == "Shortlisted"),
                "interview": sum(1 for a in applications if a.status == "Interview"),
                "offer": sum(1 for a in applications if a.status in ["Offer", "Selected"]),
                "placed": sum(1 for a in applications if a.status == "Placed"),
                "rejected": sum(1 for a in applications if a.status == "Rejected"),
            }

            by_drive = []
            for drive in drives:
                drive_apps = [a for a in applications if a.drive_id == drive.id]
                by_drive.append({
                    "job_title": drive.job_title,
                    "total": len(drive_apps),
                    "shortlisted": sum(1 for a in drive_apps if a.status == "Shortlisted"),
                    "interview": sum(1 for a in drive_apps if a.status == "Interview"),
                    "offer": sum(1 for a in drive_apps if a.status in ["Offer", "Selected"]),
                    "placed": sum(1 for a in drive_apps if a.status == "Placed"),
                })

            html = render_report_html(company, target_date.month, target_date.year, stats, by_drive)
            with open(html_path, "w", encoding="utf-8") as handle:
                handle.write(html)

            render_report_pdf(pdf_path, company, target_date.month, target_date.year, stats, by_drive)

            send_gchat(GCHAT_URL,
                f"📈 *Monthly Placement Report - {company.company_name}*\n"
                f"📅 Period: {target_date.month:02d}/{target_date.year}\n\n"
                f"📊 *Summary:*\n"
                f"• Total Applications: {stats['total_applications']}\n"
                f"• Shortlisted: {stats['shortlisted']}\n"
                f"• Interviews: {stats['interview']}\n"
                f"• Offers: {stats['offer']}\n"
                f"• Placed: {stats['placed']}\n"
                f"• Rejected: {stats['rejected']}"
            )
            _queue_email_notification(
                company.email,
                f"Monthly Placement Report - {target_date.month:02d}/{target_date.year}",
                f"Dear {company.company_name},\n\nYour monthly placement report for "
                f"{target_date.month:02d}/{target_date.year} is ready.\n\n"
                f"Summary:\n"
                f"  Total Applications: {stats['total_applications']}\n"
                f"  Shortlisted: {stats['shortlisted']}\n"
                f"  Interviews: {stats['interview']}\n"
                f"  Offers: {stats['offer']}\n"
                f"  Placed: {stats['placed']}\n"
                f"  Rejected: {stats['rejected']}\n"
            )
        except Exception as exc:
            send_gchat(
                GCHAT_URL,
                f"Monthly report generation failed for {company.company_name}: {str(exc)}",
            )


@celery.task(name="tasks.send_deadline_reminders")
def send_deadline_reminders():
    now = datetime.utcnow()
    deadline_window = now + timedelta(days=3)

    # Get active/approved drives with deadlines in the next 3 days
    drives = Placement_drive.query.filter(
        Placement_drive.application_deadline >= now,
        Placement_drive.application_deadline < deadline_window,
        Placement_drive.is_active == True,
        Placement_drive.status == "approved",
    ).all()

    for drive in drives:
        # Get students who haven't applied yet and aren't blacklisted
        applied_student_ids = [app.student_id for app in drive.applications]
        students_to_remind = Student.query.filter(
            ~Student.id.in_(applied_student_ids),
            Student.is_blacklisted == False,
        ).all()

        for student in students_to_remind:
            send_gchat(GCHAT_URL,
                f"Reminder: Application deadline for '{drive.job_title}' at {drive.company.company_name} "
                f"is approaching: {drive.application_deadline.strftime('%Y-%m-%d %H:%M')}. Apply soon!"
            )
            _queue_email_notification(
                student.email,
                f"Deadline Reminder: {drive.job_title}",
                f"Dear {student.full_name},\n\nThe application deadline for "
                f"\"{drive.job_title}\" at {drive.company.company_name} is "
                f"{drive.application_deadline.strftime('%Y-%m-%d %H:%M')}.\n\n"
                f"Don't miss your chance — apply soon!"
            )


@celery.task(name="tasks.generate_admin_monthly_report")
def generate_admin_monthly_report():
    today = datetime.utcnow().date()
    first_of_this_month = datetime(today.year, today.month, 1)
    target_date = first_of_this_month - timedelta(days=1)
    start_date = datetime(target_date.year, target_date.month, 1)
    end_date = datetime(target_date.year + 1, 1, 1) if target_date.month == 12 else datetime(target_date.year, target_date.month + 1, 1)

    # Build admin stats
    stats = {
        "drives_conducted": Placement_drive.query.filter(
            Placement_drive.created_at >= start_date,
            Placement_drive.created_at < end_date,
            Placement_drive.status == "approved",
        ).count(),
        "students_applied": Application.query.filter(
            Application.applied_at >= start_date,
            Application.applied_at < end_date,
        ).count(),
        "students_selected": Application.query.filter(
            Application.status.in_(["Placed", "Selected"]),
            Application.placed_at >= start_date,
            Application.placed_at < end_date,
        ).count(),
    }

    # Render and save HTML report
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Monthly Activity Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 24px; }}
    ul {{ list-style-type: none; }}
  </style>
</head>
<body>
  <h1>Monthly Activity Report - Institute</h1>
  <p>Reporting Period: {target_date.month:02d}/{target_date.year}</p>
  <h2>Summary</h2>
  <ul>
    <li>Drives Conducted: {stats['drives_conducted']}</li>
    <li>Students Applied: {stats['students_applied']}</li>
    <li>Students Selected: {stats['students_selected']}</li>
  </ul>
</body>
</html>"""

    report_dir = os.path.join(_BASE_DIR, "reports", "admin", f"{target_date.year}_{target_date.month:02d}")
    os.makedirs(report_dir, exist_ok=True)
    html_path = os.path.join(report_dir, "report.html")
    with open(html_path, "w", encoding="utf-8") as handle:
        handle.write(html)

    # Send GChat notification
    send_gchat(GCHAT_URL,
        f"📈 *Monthly Activity Report - Institute*\n"
        f"📅 Period: {target_date.month:02d}/{target_date.year}\n\n"
        f"📊 *Summary:*\n"
        f"• Drives Conducted: {stats['drives_conducted']}\n"
        f"• Students Applied: {stats['students_applied']}\n"
        f"• Students Selected: {stats['students_selected']}"
    )

    # Email all admins
    admins = Admin.query.all()
    for admin in admins:
        _queue_email_notification(
            admin.email,
            f"Monthly Activity Report - {target_date.month:02d}/{target_date.year}",
            f"The monthly activity report for {target_date.month:02d}/{target_date.year} is ready.\n\n"
            f"Summary:\n"
            f"  Drives Conducted: {stats['drives_conducted']}\n"
            f"  Students Applied: {stats['students_applied']}\n"
            f"  Students Selected: {stats['students_selected']}\n\n"
            f"Report saved at: {html_path}\n"
        )
