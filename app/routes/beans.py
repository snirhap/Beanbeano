from functools import wraps
from flask import Blueprint, g, make_response, request, jsonify
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
        bean = Bean.query.get_or_404(id)
        return jsonify({**bean.to_dict(), **{"average_rating": bean.avg_rating}})
    
    elif request.method == 'PATCH':
        data = request.get_json()
        bean = Bean.query.get_or_404(id)

        for key, value in data.items():
            if key in bean.allowed_fields:
                setattr(bean, key, value)

        db.session.commit()
        return jsonify({'message': 'Bean updated', 'Bean': bean.to_dict()}), 200

    elif request.method == 'DELETE':
        bean = Bean.query.get_or_404(id)
        db.session.delete(bean)
        db.session.commit()
        return jsonify({"message": "Bean was deleted"})

@bean_bp.route('/beans', methods=['POST'])
def add_bean():
    if request.method == 'POST':
        data = request.get_json()

        if not Roaster.query.filter_by(id=data.get("roaster_id")).first():
             return jsonify({"error:": "Roaster doesn't exist"}), 404
        try:
            new_bean = Bean(**data)
        except Exception as err:
            return jsonify({"error:": err}), 400
        
        db.session.add(new_bean)
        db.session.commit()
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
        bean = Bean.query.get_or_404(bean_id)
        pagination = Review.query.filter_by(bean_id=bean_id).paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "page": pagination.page,
            "limit": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "reviews": [r.to_dict() for r in pagination.items]
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
        user = User.query.filter_by(id=current_user.get("user_id")).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        bean = Bean.query.get_or_404(bean_id)

        existed_review = Review.query.filter_by(user_id=user.id, bean_id=bean.id).first()
        if existed_review:
            return jsonify({"error": "User already reviewed this bean"}), 409
        
        try:
            new_review = Review(user_id=user.id, bean_id=bean.id, content=content, rating=rating)
            db.session.add(new_review)
            db.session.commit()
            return jsonify({"message": f'Review was added'}), 201
        except Exception as e:
            return jsonify({"Error": f"Internal server error. Error: {e}"}), 500