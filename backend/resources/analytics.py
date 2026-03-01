"""
Public and Analytics API resources.
Provides aggregated statistics, placement trends, and analytics data.
"""
from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from models import db, Student, Company, Placement_drive, Application, Drive_eligibility
from datetime import datetime
from sqlalchemy import func, and_, or_, case
from utils.cache import (
    cache_response, CACHE_PREFIXES
)
from utils.decorators import role_required
import json
import re


class PublicStats(Resource):
    """Public endpoint for landing page statistics - no authentication required."""
    
    @cache_response(CACHE_PREFIXES['public_stats'], ttl_type='long')
    def get(self):
        # Get current date info
        now = datetime.utcnow()
        current_year = now.year
        current_month = now.month
        
        # Calculate stats for the last 12 months
        monthly_stats = []
        for i in range(12):
            # Calculate month/year going back from current
            month = current_month - i
            year = current_year
            if month <= 0:
                month += 12
                year -= 1
            
            # Start and end dates for the month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            # Count placements (status = 'Placed' or 'Selected')
            placements = Application.query.filter(
                and_(
                    Application.status.in_(['Placed', 'Selected']),
                    or_(
                        and_(Application.placed_at >= start_date, Application.placed_at < end_date),
                        and_(Application.selected_at >= start_date, Application.selected_at < end_date)
                    )
                )
            ).count()
            
            # Count new drives created
            drives = Placement_drive.query.filter(
                and_(
                    Placement_drive.created_at >= start_date,
                    Placement_drive.created_at < end_date,
                    Placement_drive.is_approved == True
                )
            ).count()
            
            # Count applications
            applications = Application.query.filter(
                and_(
                    Application.applied_at >= start_date,
                    Application.applied_at < end_date
                )
            ).count()
            
            month_name = start_date.strftime('%b %Y')
            monthly_stats.append({
                'month': month_name,
                'month_num': month,
                'year': year,
                'placements': placements,
                'drives': drives,
                'applications': applications
            })
        
        # Reverse to show oldest first for charts
        monthly_stats.reverse()
        
        # Overall summary stats (aggregated, non-sensitive)
        total_placements = Application.query.filter(
            Application.status.in_(['Placed', 'Selected'])
        ).count()
        
        total_drives = Placement_drive.query.filter(
            Placement_drive.is_approved == True
        ).count()
        
        active_companies = Company.query.filter(
            Company.status == 'approved',
            Company.is_blacklisted == False
        ).count()
        
        registered_students = Student.query.filter(
            Student.is_blacklisted == False
        ).count()
        
        # Top hiring sectors (based on job descriptions - simplified)
        top_sectors = self._get_top_sectors()
        
        return {
            'summary': {
                'total_placements': total_placements,
                'total_drives': total_drives,
                'active_companies': active_companies,
                'registered_students': registered_students,
            },
            'monthly_trends': monthly_stats,
            'top_sectors': top_sectors,
            'last_updated': now.isoformat()
        }, 200
    
    def _get_top_sectors(self):
        """Extract top hiring sectors from job titles and descriptions."""
        # Common tech/job sectors to look for
        sector_keywords = {
            'Software Development': ['software', 'developer', 'engineer', 'programming', 'full stack', 'frontend', 'backend'],
            'Data Science': ['data', 'analytics', 'ml', 'machine learning', 'ai', 'artificial intelligence'],
            'Finance': ['finance', 'banking', 'accounting', 'financial'],
            'Marketing': ['marketing', 'sales', 'business development', 'digital marketing'],
            'Design': ['design', 'ui', 'ux', 'graphic', 'creative'],
            'Operations': ['operations', 'management', 'project manager', 'product'],
            'Consulting': ['consultant', 'consulting', 'advisory'],
            'HR': ['hr', 'human resources', 'recruitment', 'talent'],
        }
        
        drives = Placement_drive.query.filter(
            Placement_drive.is_approved == True
        ).all()
        
        sector_counts = {sector: 0 for sector in sector_keywords}
        
        for drive in drives:
            text = f"{drive.job_title} {drive.job_description or ''}".lower()
            for sector, keywords in sector_keywords.items():
                if any(keyword in text for keyword in keywords):
                    sector_counts[sector] += 1
        
        # Return top 5 non-zero sectors
        sorted_sectors = sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'sector': s[0], 'count': s[1]} for s in sorted_sectors[:5] if s[1] > 0]


class AnalyticsPlacementTrends(Resource):
    """Detailed placement trends analytics."""
    
    @role_required('admin')
    @cache_response(CACHE_PREFIXES['analytics'], ttl_type='medium')
    def get(self):
        now = datetime.utcnow()
        months = int(request.args.get('months', 12))
        
        trends = []
        for i in range(months):
            month = now.month - i
            year = now.year
            if month <= 0:
                month += 12
                year -= 1
            
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            # Applications by status for this month
            applied = Application.query.filter(
                Application.applied_at >= start_date,
                Application.applied_at < end_date
            ).count()
            
            shortlisted = Application.query.filter(
                Application.shortlisted_at >= start_date,
                Application.shortlisted_at < end_date
            ).count()
            
            interviewed = Application.query.filter(
                Application.interview_at >= start_date,
                Application.interview_at < end_date
            ).count()
            
            offered = Application.query.filter(
                Application.offer_at >= start_date,
                Application.offer_at < end_date
            ).count()
            
            placed = Application.query.filter(
                or_(
                    and_(Application.placed_at >= start_date, Application.placed_at < end_date),
                    and_(Application.selected_at >= start_date, Application.selected_at < end_date)
                ),
                Application.status.in_(['Placed', 'Selected'])
            ).count()
            
            trends.append({
                'month': start_date.strftime('%b %Y'),
                'month_num': month,
                'year': year,
                'applied': applied,
                'shortlisted': shortlisted,
                'interviewed': interviewed,
                'offered': offered,
                'placed': placed
            })
        
        trends.reverse()
        return {'trends': trends}, 200


class AnalyticsJobDemand(Resource):
    """Job demand analytics by skills and roles."""
    
    @role_required('admin')
    @cache_response(CACHE_PREFIXES['analytics'], ttl_type='medium')
    def get(self):
        # Get all approved drives
        drives = Placement_drive.query.filter(
            Placement_drive.is_approved == True
        ).all()
        
        # Extract skills from job descriptions
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
            'sql', 'mongodb', 'aws', 'azure', 'docker', 'kubernetes',
            'machine learning', 'data science', 'ai', 'tensorflow', 'pytorch',
            'c++', 'c#', '.net', 'php', 'ruby', 'go', 'rust', 'scala',
            'html', 'css', 'typescript', 'flutter', 'swift', 'kotlin',
            'excel', 'tableau', 'power bi', 'git', 'linux', 'devops', 'agile'
        ]
        
        skill_demand = {skill: 0 for skill in skill_keywords}
        role_demand = {}
        location_demand = {}
        package_ranges = {'0-5 LPA': 0, '5-10 LPA': 0, '10-15 LPA': 0, '15-25 LPA': 0, '25+ LPA': 0}
        
        for drive in drives:
            text = f"{drive.job_title} {drive.job_description or ''}".lower()
            
            # Count skill mentions
            for skill in skill_keywords:
                if skill.lower() in text:
                    skill_demand[skill] += 1
            
            # Count role types
            role = self._categorize_role(drive.job_title)
            role_demand[role] = role_demand.get(role, 0) + 1
            
            # Count locations
            location = drive.location or 'Not Specified'
            location_demand[location] = location_demand.get(location, 0) + 1
            
            # Parse and categorize packages
            package_range = self._categorize_package(drive.package_offered)
            package_ranges[package_range] += 1
        
        # Sort and limit results
        top_skills = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:15]
        top_roles = sorted(role_demand.items(), key=lambda x: x[1], reverse=True)[:10]
        top_locations = sorted(location_demand.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'skills': [{'skill': s[0], 'demand': s[1]} for s in top_skills if s[1] > 0],
            'roles': [{'role': r[0], 'count': r[1]} for r in top_roles],
            'locations': [{'location': l[0], 'count': l[1]} for l in top_locations],
            'package_distribution': package_ranges
        }, 200
    
    def _categorize_role(self, job_title):
        """Categorize job title into a role type."""
        title = job_title.lower()
        
        if any(k in title for k in ['intern', 'trainee']):
            return 'Intern/Trainee'
        elif any(k in title for k in ['senior', 'lead', 'principal']):
            return 'Senior Level'
        elif any(k in title for k in ['manager', 'head', 'director']):
            return 'Management'
        elif any(k in title for k in ['analyst']):
            return 'Analyst'
        elif any(k in title for k in ['engineer', 'developer']):
            return 'Engineer/Developer'
        elif any(k in title for k in ['consultant']):
            return 'Consultant'
        elif any(k in title for k in ['designer']):
            return 'Designer'
        else:
            return 'Other'
    
    def _categorize_package(self, package_str):
        """Categorize package string into a range."""
        if not package_str:
            return '0-5 LPA'
        
        # Try to extract numeric value
        package_str = package_str.lower().replace(',', '')
        numbers = re.findall(r'[\d.]+', package_str)
        
        if numbers:
            try:
                value = float(numbers[0])
                # Check if it's in lakhs
                if 'lpa' in package_str or 'lakh' in package_str:
                    pass
                elif 'crore' in package_str:
                    value *= 100
                elif value > 100:  # Likely in thousands
                    value /= 100
                
                if value < 5:
                    return '0-5 LPA'
                elif value < 10:
                    return '5-10 LPA'
                elif value < 15:
                    return '10-15 LPA'
                elif value < 25:
                    return '15-25 LPA'
                else:
                    return '25+ LPA'
            except ValueError:
                return '0-5 LPA'
        
        return '0-5 LPA'


class AnalyticsApplicationFunnel(Resource):
    """Application funnel analytics."""
    
    @role_required('admin')
    @cache_response(CACHE_PREFIXES['analytics'], ttl_type='medium')
    def get(self):
        # Overall funnel
        total_applications = Application.query.count()
        status_counts = db.session.query(
            Application.status,
            func.count(Application.id)
        ).group_by(Application.status).all()
        
        status_dict = dict(status_counts)
        
        funnel = {
            'applied': total_applications,
            'shortlisted': status_dict.get('Shortlisted', 0) + status_dict.get('Interview', 0) + 
                          status_dict.get('Offer', 0) + status_dict.get('Selected', 0) + 
                          status_dict.get('Placed', 0),
            'interview': status_dict.get('Interview', 0) + status_dict.get('Offer', 0) + 
                        status_dict.get('Selected', 0) + status_dict.get('Placed', 0),
            'offered': status_dict.get('Offer', 0) + status_dict.get('Selected', 0) + 
                      status_dict.get('Placed', 0),
            'placed': status_dict.get('Selected', 0) + status_dict.get('Placed', 0)
        }
        
        # Calculate conversion rates
        conversion_rates = {}
        if funnel['applied'] > 0:
            conversion_rates['applied_to_shortlisted'] = round(funnel['shortlisted'] / funnel['applied'] * 100, 1)
        if funnel['shortlisted'] > 0:
            conversion_rates['shortlisted_to_interview'] = round(funnel['interview'] / funnel['shortlisted'] * 100, 1)
        if funnel['interview'] > 0:
            conversion_rates['interview_to_offered'] = round(funnel['offered'] / funnel['interview'] * 100, 1)
        if funnel['offered'] > 0:
            conversion_rates['offered_to_placed'] = round(funnel['placed'] / funnel['offered'] * 100, 1)
        if funnel['applied'] > 0:
            conversion_rates['overall'] = round(funnel['placed'] / funnel['applied'] * 100, 1)
        
        # Top performing branches
        branch_stats = db.session.query(
            Student.branch,
            func.count(Application.id).label('total'),
            func.sum(case((Application.status.in_(['Placed', 'Selected']), 1), else_=0)).label('placed')
        ).join(Application, Student.id == Application.student_id)\
         .group_by(Student.branch).all()
        
        branch_performance = []
        for branch, total, placed in branch_stats:
            if total > 0:
                branch_performance.append({
                    'branch': branch,
                    'total_applications': total,
                    'placements': placed or 0,
                    'success_rate': round((placed or 0) / total * 100, 1)
                })
        
        branch_performance.sort(key=lambda x: x['success_rate'], reverse=True)
        
        return {
            'funnel': funnel,
            'conversion_rates': conversion_rates,
            'branch_performance': branch_performance[:10],
            'status_breakdown': status_dict
        }, 200


class AnalyticsCompanyPerformance(Resource):
    """Company-specific analytics (for companies to see their own performance)."""
    
    @role_required('company')
    @cache_response(CACHE_PREFIXES['analytics'], ttl_type='medium')
    def get(self):
        identity = json.loads(get_jwt_identity())
        company_id = identity['id']
        
        # Get company's drives
        drives = Placement_drive.query.filter_by(company_id=company_id).all()
        drive_ids = [d.id for d in drives]
        
        if not drive_ids:
            return {
                'overview': {'total_drives': 0, 'total_applications': 0, 'total_placed': 0},
                'funnel': {},
                'drive_performance': []
            }, 200
        
        # Get all applications for company's drives
        applications = Application.query.filter(Application.drive_id.in_(drive_ids)).all()
        
        # Status counts
        status_counts = {}
        for app in applications:
            status_counts[app.status] = status_counts.get(app.status, 0) + 1
        
        # Calculate funnel
        total = len(applications)
        placed = status_counts.get('Placed', 0) + status_counts.get('Selected', 0)
        
        # Drive-wise performance
        drive_performance = []
        for drive in drives:
            drive_apps = [a for a in applications if a.drive_id == drive.id]
            drive_placed = sum(1 for a in drive_apps if a.status in ['Placed', 'Selected'])
            
            drive_performance.append({
                'drive_id': drive.id,
                'job_title': drive.job_title,
                'total_applications': len(drive_apps),
                'placed': drive_placed,
                'status': drive.status,
                'created_at': drive.created_at.isoformat()
            })
        
        return {
            'overview': {
                'total_drives': len(drives),
                'total_applications': total,
                'total_placed': placed,
                'conversion_rate': round(placed / total * 100, 1) if total > 0 else 0
            },
            'funnel': status_counts,
            'drive_performance': drive_performance
        }, 200


class AnalyticsStudentPerformance(Resource):
    """Student-specific analytics (for students to see their own performance)."""
    
    @role_required('student')
    @cache_response(CACHE_PREFIXES['analytics'], ttl_type='short')
    def get(self):
        identity = json.loads(get_jwt_identity())
        student_id = identity['id']
        
        # Get student's applications
        applications = Application.query.filter_by(student_id=student_id).all()
        
        if not applications:
            return {
                'overview': {'total_applications': 0},
                'status_breakdown': {},
                'timeline': []
            }, 200
        
        # Status breakdown
        status_counts = {}
        for app in applications:
            status_counts[app.status] = status_counts.get(app.status, 0) + 1
        
        # Application timeline (last 6 months)
        now = datetime.utcnow()
        timeline = []
        for i in range(6):
            month = now.month - i
            year = now.year
            if month <= 0:
                month += 12
                year -= 1
            
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            month_apps = [a for a in applications 
                         if a.applied_at and start_date <= a.applied_at < end_date]
            
            timeline.append({
                'month': start_date.strftime('%b %Y'),
                'applications': len(month_apps)
            })
        
        timeline.reverse()
        
        # Calculate success metrics
        total = len(applications)
        placed = status_counts.get('Placed', 0) + status_counts.get('Selected', 0)
        
        return {
            'overview': {
                'total_applications': total,
                'placed': placed,
                'shortlisted': status_counts.get('Shortlisted', 0),
                'interviews': status_counts.get('Interview', 0),
                'offers': status_counts.get('Offer', 0),
                'rejected': status_counts.get('Rejected', 0)
            },
            'status_breakdown': status_counts,
            'timeline': timeline
        }, 200
