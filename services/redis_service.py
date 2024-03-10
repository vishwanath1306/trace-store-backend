import redis
from flask import Flask

from utils.exceptions import RedisSetupException

class SemSearchRedis(object):
     
    __slots__ = ['jobs_storage']

    def __init__(self):
          self.jobs_storage = None

    def _check_connection(self, connection):
        connection.ping()
    
    def _create_connection(self, host, port, db):
        try:
            connection = redis.Redis(host=host, port=port, db=db) 
        except redis.ConnectionError as e:
            raise RedisSetupException(f"Redis connection failed due to: {e}")
        return connection
        
    
        
    def init_app(self, app: Flask):
        print(app.config['JOBS_STORAGE']['HOST'], app.config['JOBS_STORAGE']['PORT'], app.config['JOBS_STORAGE']['DB'])
        try:
            self.jobs_storage = self._create_connection(
                app.config['JOBS_STORAGE']['HOST'],
                app.config['JOBS_STORAGE']['PORT'],
                app.config['JOBS_STORAGE']['DB'])
            
        except Exception as e:
            raise RedisSetupException(f"Redis setup failed due to: {e}")
        

cache = SemSearchRedis()

    
