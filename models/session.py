import datetime
import enum
from typing import Dict, Union

from flask import current_app as app
from models import database
from utils.exceptions import SessionNotFoundException

class ExampleTable(database.Model):
    __tablename__ = 'example_table'
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), nullable=False)
    created_at = database.Column(database.DateTime, default=datetime.datetime.utcnow)
    updated_at = database.Column(database.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, id, name: str):
        self.id = id
        self.name = name

    def __repr__(self):
        return f'<ExampleTable {self.name}>'

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
