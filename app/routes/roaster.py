from flask import Blueprint, current_app, g, make_response, request, jsonify
from ..models import db, Roaster, Review
from ..config import Config
from .auth import jwt_required, role_required

roaster_bp = Blueprint('roaster', __name__)

@roaster_bp.route('/roasters', methods=['POST'])
@jwt_required
@role_required('admin')
def add_roaster():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Missing roaster name"}), 400

    with current_app.db_manager.get_write_session() as session:
        if session.query(Roaster).filter_by(name=data.get("name")).first():
            return jsonify({"error:": "Roaster already exist"}), 400
        try:
            new_roaster = Roaster(**data)
            session.add(new_roaster)
            session.commit()
        except Exception as err:
            session.rollback()
            return jsonify({"error": f"Invalid input or DB error: {err}"}), 400
        
        return jsonify({"message": f"New roaster {data.get('name')} was created successfully"}), 201

def get_roaster_from_db(db_session, roaster_id):
    roaster = db_session.query(Roaster).filter_by(id=roaster_id).first()
    if not roaster:
        return None
    return roaster
    
@roaster_bp.route('/roasters/<int:roaster_id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required
def get_roaster(roaster_id):
    if request.method == 'GET':
        with current_app.db_manager.get_read_session() as session:
            roaster = get_roaster_from_db(session, roaster_id)
            if not roaster:
                return jsonify({"error": "Roaster doesn't exist"}), 404
            return jsonify(roaster.to_dict()), 200
    elif request.method == 'PATCH':
        data = request.get_json()
        with current_app.db_manager.get_write_session() as session:
            roaster = get_roaster_from_db(session, roaster_id)
            if not roaster:
                return jsonify({"error": "Roaster doesn't exist"}), 404
            for key, value in data.items():
                if key in roaster.allowed_fields:
                    setattr(roaster, key, value)
            session.commit()
            return jsonify({'message': 'Roaster updated', 'roaster': roaster.to_dict()}), 200
    elif request.method == 'DELETE':
        with current_app.db_manager.get_write_session() as session:
            roaster = get_roaster_from_db(session, roaster_id)
            if not roaster:
                return jsonify({"error": "Roaster doesn't exist"}), 404
            session.delete(roaster)
            session.commit()
            return jsonify({"message": f"Roaster {roaster.name} was deleted"}), 200

@roaster_bp.route('/get_all_roasters', methods=['GET'])
def get_all_roasters():
    with current_app.db_manager.get_read_session() as session:
        roasters = session.query(Roaster).all() 

        if roasters:
            return jsonify([r.to_dict() for r in roasters]), 200
        return jsonify({"message": f"There are no roasters in DB"}), 404
