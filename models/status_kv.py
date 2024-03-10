from typing import Tuple
import redis
from services.redis_service import cache
from utils.exceptions import RedisSetupException, RedisRuntimeError


class StatusKV(object):

    __slots__ = ['session_id', 'lines_completed']

    def __init__(self):
        self.session_id = None
        self.lines_completed = 0

    def create_new_session(self, session_id):
        try:
            cache.jobs_storage.set(session_id, self.lines_completed)
            self.session_id = session_id
        except Exception as e:
            raise RedisRuntimeError(f"Unable to run create_new_session due to: {e}")

    @staticmethod
    def get_lines_completed(key: str) -> int:
        try:
            value = cache.jobs_storage.get(key)
        except Exception as e:
            raise RedisRuntimeError(f"Unable to run get_status due to: {e}")
        return int(value)
    
    @staticmethod
    def delete_lines_completed(key: str) -> int:
        try:
            retval = cache.jobs_storage.delete(key)
        except Exception as e:
            raise RedisRuntimeError(f"Unable to run delete_status due to: {e}")
        return retval
    
    @staticmethod
    def increment_session_id_lines_completed(session_id):
        try:
            cache.jobs_storage.incr(session_id)
        except Exception as e:
            raise RedisRuntimeError(f"Unable to run increment_session_id_lines_completed due to: {e}")
    

    def get_status_with_expiry(self, key: str, expiry: int) -> Tuple[str, int]:
        value = self.get_status(key)
        cache.jobs_storage.expire(key, expiry)
        return value, expiry