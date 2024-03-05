from flask import Flask
from flask_cors import CORS

from config import load_config
from models import database
from tasks import celery, initialize_celery

def initialize_flask_app(name: str, config_name: str = 'development'):
    app = Flask(name)
    app = load_config(app, config_name)
    CORS(app)
    database.init_app(app)
    with app.app_context():
        from modules.session.session_routes import session_bp
        
        app.register_blueprint(session_bp)

        initialize_celery(app, celery)
        
    return app

