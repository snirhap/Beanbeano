from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(128), nullable=False, default='viewer')
    reviews = db.relationship('Review', back_populates='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.id}: Username: {self.username} | role: {self.role}>"

class Roaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    beans = db.relationship('Bean', back_populates='roaster', lazy=True, cascade='all, delete-orphan')

    @property
    def avg_rating(self):
            ratings = [bean.avg_rating for bean in self.beans if bean.avg_rating is not None]
            return round(sum(ratings) / len(ratings), 2) if ratings else None

    def __repr__(self):
        return f"<Roaster {self.id}: {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avg_rating': self.avg_rating,
            'beans': [bean.to_dict() for bean in self.beans]
        }

class Bean(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    roast_level = db.Column(db.String(150), nullable=False)
    origin = db.Column(db.String(150), nullable=False)
    price_per_100_grams = db.Column(db.Float, nullable=False)
    roaster_id = db.Column(db.Integer, db.ForeignKey('roaster.id'), nullable=False)
    roaster = db.relationship('Roaster', back_populates='beans')
    reviews = db.relationship('Review', back_populates='bean', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Bean {self.id}: {self.name}; Roaster: {self.roaster_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'roast_level': self.roast_level,
            'origin': self.origin,
            'price_per_100_grams': self.price_per_100_grams,
            'roaster_id': self.roaster_id,
            'roaster_name': self.roaster.name if self.roaster else None,
            'reviews': [review.to_dict() for review in self.reviews] if self.reviews else None
        }
    
    @property
    def avg_rating(self):
        return db.session.query(func.avg(Review.rating)).filter(Review.bean_id == self.id).scalar()
    
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='reviews')
    bean_id = db.Column(db.Integer, db.ForeignKey('bean.id'), nullable=False)
    bean = db.relationship('Bean', back_populates='reviews')
    content = db.Column(db.String(150), nullable=False)
    rating = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Review {self.id}: User: {self.user_id}; Bean: {self.bean_id}; Rating: {self.rating}; Content: {self.content}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user_id,
            'username': self.user.username if self.user else None,
            'bean_id': self.bean_id,
            'content': self.content,
            'rating': self.rating
        }