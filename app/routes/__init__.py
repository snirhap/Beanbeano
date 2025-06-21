from flask import Flask, request, jsonify
from ..config import Config
from ..models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    

    @app.route('/')
    def home():
        return "Welcome to the Home Brew Coffee Review API!"

    # Set auth paths
    from ..routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    return app
