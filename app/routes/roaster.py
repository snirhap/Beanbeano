from flask import Blueprint, g, make_response, request, jsonify
from ..models import db, Roaster, Review
from ..config import Config
import bcrypt
import jwt
import datetime
from .auth import jwt_required, role_required

roaster_bp = Blueprint('roaster', __name__)

@roaster_bp.route('/add_roaster', methods=['GET', 'POST'])
@jwt_required
@role_required('admin')
def add_roaster():
    if request.method == 'POST':
        user = g.user
        print(user)
        if user.get('role') != 'admin':
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()

        if not Roaster.query.filter_by(name=data.get("name")):
             return jsonify({"error:": "Roaster doesn't exist"}), 500
        try:
            new_roaster = Roaster(**data)
        except Exception as err:
            return jsonify({"error:": err}), 500
        
        db.session.add(new_roaster)
        db.session.commit()
        return jsonify({"message": f"New roaster {data.get('name')} was created successfully"}), 201

@roaster_bp.route('/edit_roaster/<int:roaster_id>', methods=['GET', 'PATCH'])
@jwt_required
def edit_roaster(roaster_id):
    if request.method == 'PATCH':
        data = request.get_json()
        roaster = Roaster.query.get_or_404(roaster_id)

        for key, value in data.items():
            if key in roaster.allowed_fields:
                setattr(roaster, key, value)

        db.session.commit()
        return jsonify({'message': 'Roaster updated', 'roaster': roaster.to_dict()}), 200


@roaster_bp.route('/get_all_roasters', methods=['GET'])
def get_all_roasters():
    roasters = Roaster.query.all()
    if roasters:
        return jsonify([r.to_dict() for r in roasters]), 200
    return 'No roasters'

@roaster_bp.route('/view_roaster/<int:id>', methods=['GET', 'POST'])
def view_roaster(id):
    if request.method == 'GET':
        roaster = Roaster.query.filter_by(id=id).first()
        return jsonify(roaster.to_dict())

@roaster_bp.route('/delete_roaster/<int:id>', methods=['GET', 'POST'])
def delete_roaster(id):
    if request.method == 'POST':
        roaster = roaster.query.get_or_404(id)
        db.session.delete(roaster)
        db.session.commit()
        return jsonify({"message": f"roaster {roaster.name} was deleted"})
