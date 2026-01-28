from flask_restful import Resource
from flask import request
from models import db,admin,Student,Company
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash



class Login(Resource):
    def post(self):
        data=request.get_json()
        email=data['email']
        password=data['password']

        admin_user=admin.query.filter_by(email=email).first()
        if admin_user and check_password_hash(admin_user.password, password):
            access_token=create_access_token(identity={'role':'admin','id':admin_user.id})
            return {'access_token':access_token},200
        student=Student.query.filter_by(email=email).first()
        if student and check_password_hash(student.password, password):
            access_token=create_access_token(identity={'role':'Student','id':student.id})
            return {'access_token':access_token},200
        company=Company.query.filter_by(email=email).first()
        if company and check_password_hash(company.password, password):
            access_token=create_access_token(identity={'role':'company','id':company.id})
            return {'access_token':access_token},200
        return {'message':'Invalid credentials'},401


class StudentRegister(Resource):
    def post(self):
        data=request.get_json()
        new_student=Student(
            full_name=data.get('full_name'),
            email=data.get('email'),
            password=generate_password_hash(data.get('password')),
            college=data.get('college'),
            branch=data.get('branch'),
            year=data.get('year'),
            cgpa=data.get('cgpa')
        )
        db.session.add(new_student)
        db.session.commit()
        return {'message':'Student registered successfully'},201
    
class CompanyRegister(Resource):
    def post(self):
        data=request.get_json()
        new_company=Company(
            company_name=data.get('company_name'),
            email=data.get('email'),
            password=generate_password_hash(data.get('password')),
            description=data.get('description'),
            website=data.get('website'),
            is_approved=False,
            hr_name=data.get('hr_name')
        )
        db.session.add(new_company)
        db.session.commit()
        return {'message':'Company registered,Await admin approval'},201
