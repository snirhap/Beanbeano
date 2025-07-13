from functools import wraps
from flask import Blueprint, current_app, g, make_response, request, jsonify
from ..models import db, Bean, User, Review
from .auth import jwt_required, role_required

review_bp = Blueprint('review', __name__)
        
@review_bp.route('/reviews/<int:review_id>', methods=['PATCH', 'DELETE'])
@jwt_required
def modify_or_delete_review(review_id):
    if request.method == 'DELETE':
        with current_app.db_manager.get_write_session() as session:
            review = session.query(Review).get(review_id)
            if not review:
                return jsonify({'error': 'Review does not exist'}), 404
            session.delete(review)
            session.commit()
            return jsonify({"message": "Review was deleted"})
    
    elif request.method == 'PATCH':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        with current_app.db_manager.get_write_session() as session:
            review = session.query(Review).get(review_id)
            if not review:
                return jsonify({'message': 'Review does not exist'}), 404
            
            # Check that user owns review
            current_user = g.user
            if current_user['user_id'] != review.user_id:
                return jsonify({'message': 'You are not authorized to modify this review'}), 403

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

            session.commit()
            return jsonify({'message': 'Review was updated', 'review': review.to_dict()}), 200

@review_bp.route('/reviews/<int:review_id>', methods=['GET'])
def view_review(review_id):
    if request.method == 'GET':
        with current_app.db_manager.get_read_session() as session:
            review = session.query(Review).get(review_id)
            if not review:
                return jsonify({'message': 'Review does not exist'}), 404
            return jsonify({"message": f'Review details: {review.to_dict()}'})
