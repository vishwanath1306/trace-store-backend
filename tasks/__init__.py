from celery import Celery
from flask import Flask

"""
Global Task Manager that is a Celery instance to be used for asynchronously triggering jobs
"""
celery = Celery('tasks', config_source='tasks.celery_config')


def initialize_celery(app: Flask, celery: Celery) -> None:

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
