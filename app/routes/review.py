from functools import wraps
from flask import Blueprint, make_response, request, jsonify
from ..models import db, Bean, User, Review
from .auth import jwt_required, role_required

review_bp = Blueprint('review', __name__)
        
@review_bp.route('/reviews/<int:review_id>', methods=['PATCH', 'DELETE'])
@jwt_required
def modify_or_delete_review(review_id):
    if request.method == 'DELETE':
        review = Review.query.get_or_404(review_id)
        db.session.delete(review)
        db.session.commit()
        return jsonify({"message": "Review was deleted"})
    
    elif request.method == 'PATCH':
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

@review_bp.route('/reviews/<int:review_id>', methods=['GET'])
def view_review(review_id):
    if request.method == 'GET':
        review = Review.query.filter_by(id=review_id).first()
        return jsonify({"message": f'Review details: {review}'})
