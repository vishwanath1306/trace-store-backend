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
    app.config['DEBUG'] = config[config_name]['DEBUG']
    app.secret_key = str(uuid.uuid1())
    return app