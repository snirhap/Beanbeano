from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
# Initialize SQLAlchemy ORM for model definitions and metadata management
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'app_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(128), nullable=False, default='viewer')
    reviews = db.relationship('Review', back_populates='user', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', back_populates='user', lazy=True, cascade='all, delete-orphan')
    favorite_beans = db.relationship('FavoriteBean', back_populates='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }

class Roaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    address = db.Column(db.String(150), unique=True, nullable=False)
    website = db.Column(db.String(150), unique=True, nullable=False)
    beans = db.relationship('Bean', back_populates='roaster', lazy=True, cascade='all, delete-orphan')

    @property
    def allowed_fields(self):
        return {'name', 'address', 'website'}

    def avg_rating(self, session):
        ratings = []
        for bean in self.beans:
            rating = bean.avg_rating(session)
            if rating is not None:
                ratings.append(rating)
        return round(sum(ratings) / len(ratings), 2) if ratings else None

    def __repr__(self):
        return f"<Roaster {self.id}: {self.name}>"

    def to_dict(self, session=None):
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'website': self.website,

        }
        if session:
            data['average_rating'] = self.avg_rating(session)
            if self.beans:
                data['beans'] = [bean.to_dict(session) for bean in self.beans]
            else:
                data['beans'] = []
        return data

class Bean(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    roast_level = db.Column(db.String(150), nullable=False)
    origin = db.Column(db.String(150), nullable=False)
    price_per_100_grams = db.Column(db.Float, nullable=False)
    roaster_id = db.Column(db.Integer, db.ForeignKey('roaster.id'), nullable=False)
    roaster = db.relationship('Roaster', back_populates='beans')
    reviews = db.relationship('Review', back_populates='bean', cascade='all, delete-orphan')
    favorited_by = db.relationship('FavoriteBean', back_populates='bean', cascade='all, delete-orphan')

    @property
    def allowed_fields(self):
        return {'name', 'roast_level', 'origin', 'price_per_100_grams'}
    
    def to_dict(self, session=None):
        data = {
            'id': self.id,
            'name': self.name,
            'roast_level': self.roast_level,
            'origin': self.origin,
            'price_per_100_grams': self.price_per_100_grams,
            'roaster_id': self.roaster_id,
            'roaster_name': self.roaster.name if self.roaster else None,
        }
        
        if session:
            data['average_rating'] = self.avg_rating(session)
        return data
    
    def avg_rating(self, session):
        return session.query(func.avg(Review.rating)).filter(Review.bean_id == self.id).scalar()

class FavoriteBean(db.Model):
    __tablename__ = 'favorite_bean'
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), primary_key=True)
    user = db.relationship('User', back_populates='favorite_beans')
    bean_id = db.Column(db.Integer, db.ForeignKey('bean.id'), primary_key=True)
    bean = db.relationship('Bean', back_populates='favorited_by')

class Like(db.Model):
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), primary_key=True)
    review = db.relationship('Review', back_populates='likes')
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), primary_key=True)
    user = db.relationship('User', back_populates='likes')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    user = db.relationship('User', back_populates='reviews')
    bean_id = db.Column(db.Integer, db.ForeignKey('bean.id'), nullable=False)
    bean = db.relationship('Bean', back_populates='reviews')
    content = db.Column(db.String(150), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    brew_method = db.Column(db.String(150), nullable=False)
    likes = db.relationship('Like', back_populates='review', cascade='all, delete-orphan')

    @property
    def allowed_fields(self):
        return {'content', 'rating', 'brew_method'}
    
    @property
    def num_likes(self):
        return len(self.likes)
    
    def __repr__(self):
        return f"Review {self.id}: \
            User: {self.user_id}; \
            Bean: {self.bean_id}; \
            Rating: {self.rating}; \
            Content: {self.content}; \
            Brew Method: {self.brew_method}; \
            Likes: {self.num_likes}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user_id,
            'username': self.user.username if self.user else None,
            'bean_id': self.bean_id,
            'content': self.content,
            'rating': self.rating,
            'brew_method': self.brew_method,
            'likes': self.num_likes
        }