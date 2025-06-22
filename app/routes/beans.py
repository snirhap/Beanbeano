from flask import Blueprint, make_response, request, jsonify
from ..models import db, Bean, Roaster
from ..config import Config
import bcrypt
import jwt
import datetime

bean_bp = Blueprint('beans', __name__)

@bean_bp.route('/add_bean', methods=['GET', 'POST'])
def add_bean():
    if request.method == 'POST':
        data = request.get_json()

        if not Roaster.query.filter_by(id=data.get("roaster_id")).first():
             return jsonify({"error:": "Roaster doesn't exist"}), 500
        try:
            new_bean = Bean(**data)
        except Exception as err:
            return jsonify({"error:": err}), 500
        
        db.session.add(new_bean)
        db.session.commit()
        return jsonify({"message": f"New Bean {data.get('name')} was created successfully"}), 201

@bean_bp.route('/update_bean', methods=['GET', 'POST'])
def update_bean():
    if request.method == 'POST':
        pass
        # data = request.get_json()
        # username = data.get('username')
        # password = data.get('password')
        # print(f'{username} {password}')

        # if User.query.filter_by(username=username).first():
        #     return jsonify({"error": f"User {username} already exist in DB"}), 400
        
        # hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        # new_user = User(username=username, password_hash=hashed_password)
        # db.session.add(new_user)
        # db.session.commit()
        
        # return jsonify({"message": f"User {username} was created successfully"}), 201

@bean_bp.route('/view_bean/<int:id>', methods=['GET', 'POST'])
def view_bean(id):
    if request.method == 'GET':
        bean = Bean.query.get_or_404(id)
        return jsonify({"message": f'Bean details: {bean.to_dict()}'})

@bean_bp.route('/delete_bean/<int:id>', methods=['GET', 'POST'])
def delete_bean(id):
    if request.method == 'POST':
        bean = Bean.query.get_or_404(id)
        db.session.delete(bean)
        db.session.commit()
        return jsonify({"message": "Bean was deleted"})
