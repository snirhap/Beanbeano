from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from .config import Config
from app.models import db

def create_app(config_obj: Config):
    app = Flask(__name__)
    app.config.from_object(config_obj)

    db.init_app(app)
    
    jwt = JWTManager(app)
    
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to the Home Brew Coffee Review API!"})

    from app.routes.auth import auth_bp
    from app.routes.beans import bean_bp
    from app.routes.roaster import roaster_bp
    from app.routes.review import review_bp
    # Set auth paths
    app.register_blueprint(auth_bp)
    app.register_blueprint(bean_bp)
    app.register_blueprint(roaster_bp)
    app.register_blueprint(review_bp)

    return app
