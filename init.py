from flask import Flask
from flask_cors import CORS

from config import load_config


def initialize_flask_app(name: str, config_name: str = 'development'):
    app = Flask(name)
    app = load_config(app, config_name)
    CORS(app)
    return app

