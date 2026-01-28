from flask_restful import Resource
from models import Company,db
from utils.decorators import role_required

class ApproveCompany(Resource):
    @role_required('admin')
    def put(self,company_id):
        company=Company.query.get_or_404(company_id)
        company.is_approved=True
        db.session.commit()
        return {'message':'Company approved successfully'},200