from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            if identity['role'] != required_role:
                return jsonify({"msg": "Access forbidden: incorrect role"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
"""
This decorator is used to access
routes and its functionality based on user 
roles like admin, student, and company.
"""