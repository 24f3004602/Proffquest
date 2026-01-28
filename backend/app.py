from flask import Flask, jsonify
from models import db
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.auth import Login, StudentRegister, CompanyRegister
from flask_migrate import Migrate
from flask_cors import CORS
app = Flask(__name__)
jwt=JWTManager(app)
api=Api(app)
CORS(app)

# SQLite configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JWT_SECRET_KEY'] = 'secret-key'

db.init_app(app)
migrate = Migrate(app, db)

api.add_resource(Login,'/api/login')
api.add_resource(StudentRegister,'/api/register/student')
api.add_resource(CompanyRegister,'/api/register/company')
# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)