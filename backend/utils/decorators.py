from functools import wraps
from flask_jwt_extended import get_jwt_identity,jwt_required
import json

def role_required(required_role):
    """Decorator to restrict route access based on user role (admin, student, company)."""
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            identity=json.loads(get_jwt_identity())
            if identity['role']!=required_role:
                return {"message": "Unauthorized access"}, 403
            return fn(*args,**kwargs)
        return decorator
    return wrapper