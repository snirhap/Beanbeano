from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # role = ...


class Roaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    beans = db.relationship('Bean', backref='roaster', lazy=True)

class Bean(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    roast_level = db.Column(db.String(150), nullable=False)
    origin = db.Column(db.String(150), nullable=False)
    price_per_100_grams = db.Column(db.Float(150), nullable=False)
    roaster_id = db.Column(db.Integer, db.ForeignKey('roaster.id'), nullable=False)