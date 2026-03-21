"""
Public and Analytics API resources.
Provides public aggregated statistics.
"""
from flask_restful import Resource
from models import Student, Company, Placement_drive, Application
from datetime import datetime
from sqlalchemy import and_, or_
from utils.cache import cache


class PublicStats(Resource):
    """Public endpoint for landing page statistics - no authentication required."""
    
    @cache.cached(timeout=300)
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
