try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


def render_report_html(company, month, year, stats, by_drive):
    rows = "".join(
        f"<tr><td>{row['job_title']}</td><td>{row['total']}</td>"
        f"<td>{row['shortlisted']}</td><td>{row['interview']}</td>"
        f"<td>{row['offer']}</td><td>{row['placed']}</td></tr>"
        for row in by_drive
    )

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Placement Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 24px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f4f4f4; }}
  </style>
</head>
<body>
  <h1>Placement Report - {company.company_name}</h1>
  <p>Reporting Period: {month:02d}/{year}</p>
  <h2>Summary</h2>
  <ul>
    <li>Total Applications: {stats['total_applications']}</li>
    <li>Shortlisted: {stats['shortlisted']}</li>
    <li>Interviews: {stats['interview']}</li>
    <li>Offers: {stats['offer']}</li>
    <li>Placed: {stats['placed']}</li>
    <li>Rejected: {stats['rejected']}</li>
  </ul>
  <h2>By Drive</h2>
  <table>
    <thead>
      <tr>
        <th>Drive</th>
        <th>Total</th>
        <th>Shortlisted</th>
        <th>Interview</th>
        <th>Offer</th>
        <th>Placed</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
"""


def render_report_pdf(file_path, company, month, year, stats, by_drive):
    if not REPORTLAB_AVAILABLE:
        return None

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []
    elements.append(Paragraph(f"Placement Report - {company.company_name}", styles["Title"]))
    elements.append(Paragraph(f"Reporting Period: {month:02d}/{year}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    summary_data = [
        ["Total Applications", stats["total_applications"]],
        ["Shortlisted", stats["shortlisted"]],
        ["Interviews", stats["interview"]],
        ["Offers", stats["offer"]],
        ["Placed", stats["placed"]],
        ["Rejected", stats["rejected"]],
    ]
    summary_table = Table([["Metric", "Count"]] + summary_data)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    drive_table_data = [["Drive", "Total", "Shortlisted", "Interview", "Offer", "Placed"]]
    for row in by_drive:
        drive_table_data.append([
            row["job_title"],
            row["total"],
            row["shortlisted"],
            row["interview"],
            row["offer"],
            row["placed"],
        ])

    drive_table = Table(drive_table_data)
    drive_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))

    elements.append(drive_table)
    doc.build(elements)
    return file_path