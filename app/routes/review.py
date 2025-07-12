from functools import wraps
from flask import Blueprint, make_response, request, jsonify
from ..models import db, Bean, User, Review
from .auth import jwt_required, role_required

review_bp = Blueprint('review', __name__)

@review_bp.route('/add_review/<int:bean_id>', methods=['POST'])
@jwt_required
def add_review(bean_id):
    if request.method == 'POST':
        data = request.get_json()
        content = data.get("content")
        rating = data.get("rating")

        # Validate input
        if not content or not isinstance(rating, (int, float)):
            return jsonify({"error": "Invalid review data"}), 400
        
        current_user = request.user
        user = User.query.filter_by(id=current_user.get("user_id")).first()
        bean = Bean.query.filter_by(id=bean_id).first()

        existed_review = Review.query.filter_by(user_id=user.id, bean_id=bean.id).first()
        if existed_review:
            return jsonify({"error": "User already reviewed this bean"}), 409
        
        try:
            new_review = Review(user_id=user.id, bean_id=bean.id, content=content, rating=rating)
            db.session.add(new_review)
            db.session.commit()
            return jsonify({"message": f'Review was added'}), 201
        except Exception as e:
            return jsonify({"Error": f"User or Bean not found. Error: {e}"}), 500
        
@review_bp.route('/edit_review/<int:review_id>', methods=['GET', 'PATCH'])
@jwt_required
def edit_review(review_id):
    if request.method == 'PATCH':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        review = Review.query.get_or_404(review_id)

        # Check that user owns review
        current_user = request.user
        if current_user['user_id'] != review.user_id:
            return jsonify({'message': 'Review belongs to other user'}), 401

        if 'rating' in data:
            try:
                rating = float(data['rating'])
                if not (1 <= rating <= 5):
                    return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            except ValueError:
                return jsonify({'error': 'Rating must be a number'}), 400
            
        for key, value in data.items():
            if key in review.allowed_fields:
                setattr(review, key, value)

        db.session.commit()
        return jsonify({'message': 'Review was updated', 'Review': review.to_dict()}), 200

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

@review_bp.route('/reviews/<int:bean_id>', methods=['GET'])
@paginated_data
def get_reviews_for_bean(bean_id, page, per_page):
    bean = Bean.query.get_or_404(bean_id) # ensure the bean exists before querying reviews
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

@review_bp.route('/view_review/<int:id>', methods=['GET', 'POST'])
def view_review(id):
    if request.method == 'GET':
        review = Review.query.filter_by(id=id).first()
        return jsonify({"message": f'review details: {review}'})

@review_bp.route('/delete_review/<int:id>', methods=['GET', 'POST'])
def delete_review(id):
    if request.method == 'POST':
        review = Review.query.get_or_404(id)
        db.session.delete(review)
        db.session.commit()
        return jsonify({"message": "review was deleted"})
