from functools import wraps
from flask import Blueprint, current_app, g, make_response, request, jsonify
from app.routes.auth import jwt_required
from ..models import db, func, Bean, Roaster, Review, User
from ..config import Config
import bcrypt
import jwt
import datetime

bean_bp = Blueprint('beans', __name__)

@bean_bp.route('/beans/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def get_bean(id):
    if request.method == 'GET':
        with current_app.db_manager.get_read_session() as session:
            # Fetch the bean and its average rating
            bean = session.query(Bean).filter_by(id=id).first()
            if not bean:
                return jsonify({"error": "Bean not found"}), 404
            # Calculate the average rating
            avg_rating = session.query(func.avg(Review.rating)).filter_by(bean_id=id).scalar()
            bean.avg_rating = avg_rating if avg_rating is not None else 0.0
        return jsonify({**bean.to_dict(), **{"average_rating": bean.avg_rating}})
    
    elif request.method == 'PATCH':
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        with current_app.db_manager.get_write_session() as session:
            bean = session.query(Bean).filter_by(id=id).first()
            if not bean:
                return jsonify({"error": "Bean not found"}), 404 

            for key, value in data.items():
                if key in bean.allowed_fields:
                    setattr(bean, key, value)
            return jsonify({'message': 'Bean updated', 'bean': bean.to_dict()}), 200

    elif request.method == 'DELETE':
        with current_app.db_manager.get_write_session() as session:
            bean = session.query(Bean).filter_by(id=id).first()
            if not bean:
                return jsonify({"error": "Bean not found"}), 404
            # Delete the bean
            session.delete(bean)
        return jsonify({"message": "Bean was deleted"})

@bean_bp.route('/beans', methods=['POST'])
def add_bean():
    if request.method == 'POST':
        data = request.get_json()
        with current_app.db_manager.get_read_session() as session:
            if not session.query(Roaster).filter_by(id=data.get("roaster_id")).first():
                return jsonify({"error": "Roaster doesn't exist"}), 404
        try:
            new_bean = Bean(**data)
        except Exception as err:
            return jsonify({"error": err}), 400
        
        with current_app.db_manager.get_write_session() as session:
            session.add(new_bean)
        return jsonify({"message": f"New bean {data.get('name')} was created successfully"}), 201

def paginated_data(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("limit", 10, type=int)
        if per_page < 0 or per_page > 100:
            return jsonify({"error": "Limit must be positive but no more than 100"}), 400
        if page < 1:
            return jsonify({"error": "Page number cannot be less than 1"}), 400
        
        kwargs['page'] = page
        kwargs['per_page'] = per_page

        return f(*args, **kwargs)
    return decorated


@bean_bp.route('/beans/<int:bean_id>/reviews', methods=['GET', 'POST'])
@jwt_required
@paginated_data
def bean_reviews(bean_id, page, per_page):
    if request.method == 'GET':
        with current_app.db_manager.get_read_session() as session:
            bean = session.query(Bean).get(bean_id)
            if not bean:
                return jsonify({"error": "Bean not found"}), 404 
            
            query = session.query(Review).filter_by(bean_id=bean_id)
            total_reviews_count = query.count()
            reviews = query.offset((page - 1) * per_page).limit(per_page).all()

            return jsonify({
                "page": page,
                "limit": per_page,
                "total": total_reviews_count,
                "reviews": [r.to_dict() for r in reviews]
            }), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        content = data.get("content")
        rating = data.get("rating")

        if not content or not isinstance(rating, (int, float)):
            return jsonify({"error": "Invalid review data"}), 400
        
        if not (1 <= rating <= 5):
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        # Check if user is authenticated
        current_user = g.user
        with current_app.db_manager.get_write_session() as session:
            user = session.query(User).filter_by(id=current_user.get("user_id")).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

            bean = session.query(Bean).get(bean_id)
            if not bean:
                return jsonify({"error": "Bean doesn't exist"}), 404
            
            existed_review = session.query(Review).filter_by(user_id=user.id, bean_id=bean.id).first()

            if existed_review:
                return jsonify({"error": "User already reviewed this bean"}), 409

            try:
                new_review = Review(user_id=user.id, bean_id=bean.id, content=content, rating=rating)
                session.add(new_review)
                return jsonify({"message": f'Review was added'}), 201
            except Exception as e:
                return jsonify({"error": f"Internal server error. Error: {e}"}), 500