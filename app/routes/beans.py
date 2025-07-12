from flask import Blueprint, make_response, request, jsonify
from app.routes.auth import jwt_required
from ..models import db, func, Bean, Roaster, Review, User
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
        return jsonify({"message": f"New bean {data.get('name')} was created successfully"}), 201

@bean_bp.route('/edit_bean/<int:bean_id>', methods=['GET', 'PATCH'])
@jwt_required
def edit_bean(bean_id):
    if request.method == 'PATCH':
        data = request.get_json()
        bean = Bean.query.get_or_404(bean_id)

        for key, value in data.items():
            if key in bean.allowed_fields:
                setattr(bean, key, value)

        db.session.commit()
        return jsonify({'message': 'Bean updated', 'Bean': bean.to_dict()}), 200

@bean_bp.route('/view_bean/<int:id>', methods=['GET', 'POST'])
def view_bean(id):
    if request.method == 'GET':
        bean = Bean.query.get_or_404(id)
        return jsonify({**bean.to_dict(), **{"average_rating": bean.avg_rating}})
    
@bean_bp.route('/delete_bean/<int:id>', methods=['GET', 'POST'])
def delete_bean(id):
    if request.method == 'POST':
        bean = Bean.query.get_or_404(id)
        db.session.delete(bean)
        db.session.commit()
        return jsonify({"message": "Bean was deleted"})
