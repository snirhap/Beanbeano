from functools import wraps
from flask import Blueprint, current_app, make_response, request, jsonify
from ..models import db, User
from ..config import Config
import bcrypt
import jwt
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if User.query.filter_by(username=username).first():
            return jsonify({"error": f"User {username} already exist in DB"}), 400
        
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": f"User {username} was created successfully"}), 201

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.checkpw(password=password.encode(), hashed_password=user.password_hash.encode()):
            return jsonify({"error": "Invalid Credentials"}), 401
        
        jwt_token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, Config.JWT_SECRET_KEY, algorithm='HS256')

        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie('access_token', jwt_token, httponly=True)
        return response

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            request.user = payload  # attach user data to request
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated

def role_required(required_role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(request, 'user', None)
            if not user or user.get('role') != required_role:
                return jsonify({'error': f'{required_role.capitalize()} role required'}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper

@auth_bp.route('/promote/<int:user_id>', methods=['POST'])
@jwt_required
@role_required('admin')
def promote_user(user_id):
    current_user = request.user
    if current_user['role'] != 'admin':
        return jsonify({"error": "Only admins can promote users"}), 403

    user = User.query.get_or_404(user_id)
    user.role = 'admin'
    db.session.commit()

    return jsonify({"message": f"{user.username} promoted to admin"})


