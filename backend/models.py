from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db=SQLAlchemy()

class admin(db.Model):
    __tablename__='admin'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(120),nullable=False,unique=True)
    password=db.Column(db.String(120),nullable=False)

class Student(db.Model):
    __tablename__='students'
    id=db.Column(db.Integer,primary_key=True)
    full_name=db.Column(db.String(240),nullable=False)
    roll_number=db.Column(db.String(80),nullable=False,unique=True)
    branch=db.Column(db.String(120),nullable=False)
    cgpa=db.Column(db.Float,nullable=False)
    year=db.Column(db.Integer,nullable=False)
    resume_url=db.Column(db.String(500))
    phone=db.Column(db.String(15),nullable=False)
    is_blacklisted=db.Column(db.Boolean,default=False)
    applications=db.relationship('Application',back_populates='student',lazy=True)#confusion on applications and backref/back_populates

class Company(db.Model):
    __tablename__='companies'
    id=db.Column(db.Integer,nullable=False,primary_key=True)
    company_name=db.Column(db.String(120),unique=True,nullable=False)
    hr_name=db.Column(db.String(120),nullable=False)
    hr_contact=db.Column(db.String(15),nullable=False)
    website=db.Column(db.String(200),nullable=False,unique=True)
    description=db.Column(db.Text)
    address=db.Column(db.Text)
    is_approved=db.Column(db.Boolean,default=False)
    is_blacklisted=db.Column(db.Boolean,default=False)
    placement_drives=db.relationship('Placement_drive',back_populates='company',lazy=True)#

class Application(db.Model):
    __tablename__='applications'
    id=db.Column(db.Integer,nullable=False,primary_key=True)
    student_id=db.Column(db.Integer,db.ForeignKey('students.id'),nullable=False)
    drive_id=db.Column(db.Integer,db.ForeignKey('placement_drives.id'),nullable=False)
    application_date=db.Column(db.Date,nullable=False,default=datetime.utcnow)
    status=db.Column(db.String(50),default='Applied')#selected,shortlisted,rejected,applied
    applied_at=db.Column(db.DateTime, default=datetime.utcnow)
    shortlisted_at=db.Column(db.DateTime)
    selected_at=db.Column(db.DateTime)
    interview_schedule=db.Column(db.DateTime)
    interview_notes=db.Column(db.Text)
    resume_url=db.Column(db.String(500))
    student=db.relationship('Student',back_populates='applications')
    placement_drive=db.relationship('Placement_drive',back_populates='applications')

class Placement_drive(db.Model):
    __tablename__='placement_drives'
    id=db.Column(db.Integer,primary_key=True,nullable=False)
    company_id=db.Column(db.Integer,db.ForeignKey('companies.id'),nullable=False)
    job_title=db.Column(db.String(80),nullable=False)
    job_description=db.Column(db.Text,nullable=False)
    package_offered=db.Column(db.String(100),nullable=False)
    location=db.Column(db.String(240),nullable=False)
    application_deadline=db.Column(db.DateTime,nullable=False)
    drive_date=db.Column(db.DateTime,nullable=False)
    max_applicants=db.Column(db.Integer)
    is_approved=db.Column(db.Boolean,default=False)
    is_active=db.Column(db.Boolean,default=True)
    status=db.Column(db.String(20),default='pending')#pending,approved,rejected,closed
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    company=db.relationship('Company',back_populates='placement_drives')
    eligibilities=db.relationship('Drive_eligibility',back_populates='placement_drive',lazy=True)
    applications=db.relationship('Application',back_populates='placement_drive',lazy=True)

class Drive_eligibility(db.Model):
    __tablename__='drive_eligibility'
    id=db.Column(db.Integer,primary_key=True,nullable=False)
    drive_id=db.Column(db.Integer,db.ForeignKey('placement_drives.id'),nullable=False)
    branch=db.Column(db.String(80),nullable=False)
    min_cgpa=db.Column(db.Float,nullable=False)
    passing_year=db.Column(db.Integer)
    backlog_allowed=db.Column(db.Boolean,default=False)
    additional_criteria=db.Column(db.Text)
    placement_drive=db.relationship('Placement_drive',back_populates='eligibilities',lazy=True)

