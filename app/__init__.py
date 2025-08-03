from flask import Flask, jsonify
from flask_migrate import Migrate
from .config import Config
from .models import db
from .db_manager import DatabaseManager

def create_app(config_obj):
    app = Flask(__name__)
    app.config.from_object(config_obj)

    db.init_app(app)
    
    migrate = Migrate(app, db)

    # Set up custom database manager for read/write session and engine handling
    app.db_manager = DatabaseManager(config_obj)

    @app.route('/')
    def home():
        return jsonify({"message": f"Welcome to the Home Brew Coffee Review API!"})

    from app.routes.auth import auth_bp
    from app.routes.beans import bean_bp
    from app.routes.roaster import roaster_bp
    from app.routes.review import review_bp
    from app.routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(bean_bp)
    app.register_blueprint(roaster_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(user_bp)

    return app
