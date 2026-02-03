from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity,jwt_required
from flask import jsonify
import json

def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            identity=json.loads(get_jwt_identity())
            if identity['role']!=required_role:
                return jsonify({"message": "Unauthorized access"}), 403
            return fn(*args,**kwargs)
        return decorator
    return wrapper

"""
This decorator is used to access
routes and its functionality based on user 
roles like admin, student, and company.
"""