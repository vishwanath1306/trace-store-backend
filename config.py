import os
import uuid
from datetime import timedelta
from typing import Dict, Union

from flask import Flask
import yaml 


def load_config(app: Flask, config_name: str = 'development'):
    file_name = os.path.join(os.path.dirname(__file__), 'config.yml')
    config_file = open(file_name, 'r')
    all_config_dict: Dict = yaml.load(config_file, Loader=yaml.FullLoader)
    config_file.close()

    config = {
        "development": all_config_dict['DevelopmentConfig'],
    }

    app.config['TEMP_FILE_UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'temp_file_storage')
    app.config['EMBEDDING_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'embeddings')

    app.config['DEBUG'] = config[config_name]['DEBUG']
    app.config['SQLALCHEMY_DATABASE_URI'] = config[config_name]['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config[config_name]['SQLALCHEMY_TRACK_MODIFICATIONS']

    app.config['CELERY_BROKER_URL'] = config[config_name]['CELERY_BROKER_URL']
    app.config['CELERY_RESULT_BACKEND'] = config[config_name]['CELERY_RESULT_BACKEND']

    app.config['OPENAI_API_KEY'] = config[config_name]['OPENAI_KEY']
    
    app.config['GOOGLE_API_KEY']   = config[config_name]['GCP_API_key']
    app.config['GOOGLE_MODEL_NAME'] = config[config_name]['GCP_MODEL_NAME']


    app.config['JOBS_STORAGE'] = {}
    app.config['JOBS_STORAGE']['HOST'] = config[config_name]['JOBS_STORAGE']['HOST']
    app.config['JOBS_STORAGE']['PORT'] = config[config_name]['JOBS_STORAGE']['PORT']
    app.config['JOBS_STORAGE']['DB'] = config[config_name]['JOBS_STORAGE']['DB']

    app.config['MILVUS_HOST'] = config[config_name]['MILVUS_HOST']
    app.config['MILVUS_PORT'] = config[config_name]['MILVUS_PORT']
    
    app.secret_key = str(uuid.uuid1())
    return app