from tasks import celery, initialize_celery
from init import initialize_flask_app

app = initialize_flask_app(__name__)
initialize_celery(app, celery)
