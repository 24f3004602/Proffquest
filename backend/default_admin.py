from app import app
from models import db, admin
from werkzeug.security import generate_password_hash


with app.app_context():
    admin_username='admin@1234'
    existing_admin=admin.query.filter_by(email=admin_username).first()
    if not existing_admin:
        Admin=admin()
        Admin.email=admin_username
        Admin.password=generate_password_hash('admin1234')
        db.session.add(Admin)
        db.session.commit()
        print('Admin added successfully')
    else:
        print('admin already exist')