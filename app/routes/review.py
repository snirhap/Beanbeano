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

@review_bp.route('/update_review', methods=['GET', 'POST'])
def update_review():
    if request.method == 'POST':
        pass

@review_bp.route('/get_all_reviews', methods=['GET'])
def get_all_reviews():
    reviews = Review.query.all()
    if reviews:
        return jsonify([r.to_dict() for r in reviews]), 200
    return 'No reviews'

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
