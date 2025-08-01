from flask import current_app, Blueprint, jsonify
from app.models import Review, User

user_bp = Blueprint('user', __name__)

def fetch_user_with_reviews(user_id):
    with current_app.db_manager.get_read_session() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return None, None
        reviews = session.query(Review).filter_by(user_id=user_id).all()
        return user, reviews
    
@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user, _ = fetch_user_with_reviews(user_id)
    if not user:
        return jsonify({"message": "User does not exist"}), 404
    return jsonify({"message": user.to_dict()}), 200
    
@user_bp.route('/users/<int:user_id>/reviews', methods=['GET'])
def get_user_reviews(user_id):    
    with current_app.db_manager.get_read_session() as session:
        user, reviews = fetch_user_with_reviews(user_id)
        if not user:
            return jsonify({"message": "User does not exist"}), 404
        return jsonify({"message": [r.to_dict() for r in reviews]}), 200

@user_bp.route('/users/<int:user_id>/brew_methods', methods=['GET'])
def favorite_brew_methods(user_id):    
    user, reviews = fetch_user_with_reviews(user_id)
    brew_methods = dict()
    if not user:
        return jsonify({"message": "User does not exist"}), 404
    
    for r in reviews:
        brew_methods[r.brew_method] = brew_methods.get(r.brew_method, 0) + 1

    return jsonify({"brew_methods": dict(sorted(brew_methods.items(), key=lambda x: x[1], reverse=True))}), 200

@user_bp.route('/users/<int:user_id>/favorite_beans', methods=['GET'])
def favorite_beans(user_id):
    user, _ = fetch_user_with_reviews(user_id)
    fav_beans = [fb.bean.to_dict() for fb in user.favorite_beans]
    return jsonify({"favorite_beans": fav_beans}), 200