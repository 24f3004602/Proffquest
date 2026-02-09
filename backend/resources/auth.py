from flask_restful import Resource
from flask import request
from models import *
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
import json



class Login(Resource):
    def post(self):
        try:
            data=request.get_json()
            if not data or 'email' not in data or 'password' not in data:
                return {'message':'Email and password are required'},400
            
            email=data['email']
            password=data['password']

            admin_user=Admin.query.filter_by(email=email).first()
            if admin_user and check_password_hash(admin_user.password, password):
                access_token=create_access_token(identity=json.dumps({'role':'admin','id':admin_user.id}))
                return {'access_token':access_token},200
            student=Student.query.filter_by(email=email).first()
            if student and check_password_hash(student.password, password):
                if student.is_blacklisted:
                    return {'message':'Your account has been blacklisted'}, 403
                access_token=create_access_token(identity=json.dumps({'role':'student','id':student.id}))
                return {'access_token':access_token},200
            company=Company.query.filter_by(email=email).first()
            if company and check_password_hash(company.password,password):
                if company.is_blacklisted:
                    return {'message':'Your company has been blacklisted'},403
                if company.status=='rejected':
                    return {'message':'Your company registration was rejected by admin'},403
                if company.status=='pending':
                    return {'message':'Your company is pending admin approval'},403
                access_token=create_access_token(identity=json.dumps({'role':'company','id':company.id}))
                return {'access_token':access_token},200
            return {'message':'Invalid email or password'},401
        except Exception as e:
            return {'message': 'Login failed', 'error': str(e)}, 500


class StudentRegister(Resource):
    def post(self):
        data=request.get_json()
        
        # Validation
        required_fields = ['full_name', 'email', 'password', 'college', 'branch', 'year', 'cgpa']
        for field in required_fields:
            if field not in data or not data[field]:
                return {'message': f'{field} is required'}, 400
        
        # Check if email already exists
        if Student.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 400
        
        if Student.query.filter_by(roll_number=data.get('roll_number')).first():
            return {'message': 'Roll number already exists'}, 400
        
        try:
            new_student=Student(
                full_name=data.get('full_name'),
                email=data.get('email'),
                password=generate_password_hash(data.get('password')),
                college=data.get('college'),
                branch=data.get('branch'),
                year=int(data.get('year')),
                cgpa=float(data.get('cgpa')),
                roll_number=data.get('roll_number')
            )
            db.session.add(new_student)
            db.session.commit()
            return {'message':'Student registered successfully'},201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Registration failed', 'error': str(e)}, 500
    
class CompanyRegister(Resource):
    def post(self):
        data=request.get_json()
        
        # Validation
        required_fields = ['company_name', 'email', 'password', 'hr_name', 'website']
        for field in required_fields:
            if field not in data or not data[field]:
                return {'message': f'{field} is required'}, 400
        
        # Check if email already exists
        if Company.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 400
        
        if Company.query.filter_by(company_name=data['company_name']).first():
            return {'message': 'Company name already exists'}, 400
        
        try:
            new_company=Company(
                company_name=data.get('company_name'),
                email=data.get('email'),
                password=generate_password_hash(data.get('password')),
                description=data.get('description'),
                website=data.get('website'),
                status='pending',
                hr_name=data.get('hr_name')
            )
            db.session.add(new_company)
            db.session.commit()
            return {'message':'Company registered,Await admin approval'},201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Registration failed', 'error': str(e)}, 500
