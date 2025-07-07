from flask import Blueprint, make_response, request, jsonify
from ..models import db, Review
from ..config import Config
import bcrypt
import jwt
import datetime
from .auth import jwt_required, role_required

review_bp = Blueprint('review', __name__)

@review_bp.route('/add_review', methods=['GET', 'POST'])
@jwt_required
def add_review():
    if request.method == 'POST':
        data = request.get_json()

        if not Review.query.filter_by(name=data.get("name")):
             return jsonify({"error:": "review doesn't exist"}), 500
        elif "rating" in data and 1 <= data.get("rating") <= 5:
            return jsonify({"error:": "Invalid review rating (must be between 1 and 5)"}), 400
        try:

            new_review = Review(**data)
        except Exception as err:
            return jsonify({"error:": err}), 500
        
        db.session.add(new_review)
        db.session.commit()
        return jsonify({"message": f"New review {data.get('name')} was created successfully"}), 201

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


@review_bp.route('/reviews/<int:bean_id>', methods=['GET'])
def get_reviews_for_bean(bean_id):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("limit", 10, type=int)
    pagination = Review.query.filter_by(bean_id=bean_id).paginate(page=page, per_page=per_page, error_out=False)

    if pagination.items:
        return jsonify({
            "page": pagination.page,
            "limit": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "reviews": [r.to_dict() for r in pagination.items]
        }), 200
    return 'No reviews found for this bean', 404

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
