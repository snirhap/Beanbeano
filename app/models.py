from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(128), nullable=False, default='viewer')

    def __repr__(self):
        return f"<User {self.id}: Username: {self.username} | role: {self.role}>"

class Roaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    beans = db.relationship('Bean', back_populates='roaster', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Roaster {self.id}: {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
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

    def __repr__(self):
        return f"Bean {self.id}: {self.name}; Roaster: {self.roaster_id}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'roast_level': self.roast_level,
            'origin': self.origin,
            'price_per_100_grams': self.price_per_100_grams,
            'roaster_id': self.roaster_id,
            'roaster_name': self.roaster.name if self.roaster else None
        }