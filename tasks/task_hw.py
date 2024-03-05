import time
from tasks import celery

@celery.task
def add(x, y):
    time.sleep(5)
    return x + y