from flask import Blueprint, make_response, request, jsonify
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
        print(f'{username} {password}')

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
        print(data)
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.checkpw(password=password.encode(), hashed_password=user.password_hash.encode()):
            return jsonify({"error": "Invalid Credentials"}), 401
        
        jwt_token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': 'viewer',  # custom claim
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, Config.SECRET_KEY, algorithm='HS256')

        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie('access_token', jwt_token, httponly=True)
        return response

@auth_bp.route('/admin', methods=['GET'])
def admin():
    token = request.cookies.get('access_token')
    
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms='HS256')
        print(payload)
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

    if payload.get("role") == 'admin':
        return jsonify({"message": payload}), 200
    
    return jsonify({"message": "You are not an admin"}), 401
