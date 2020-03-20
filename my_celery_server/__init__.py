from celery import Celery
from flask import Flask

from config import DevConfig
from database import db

celery_server = Celery(include='my_celery_server.tasks')

celery_server.conf.update(DevConfig)

celery_flask_app = None


def get_celery_flask_app():
    global celery_flask_app
    if celery_flask_app is None:
        celery_flask_app = Flask(__name__)
        celery_flask_app.config.update(**DevConfig)
        db.init_app(celery_flask_app)
    return celery_flask_app


def with_context(fun):
    def wrapper(*args, **kwargs):
        with get_celery_flask_app().app_context():
            return fun(*args, **kwargs)

    return wrapper


# 这里必须抽离出来，否则会无穷递归
tempDec = celery_server.task


def my_task(*args, **kwargs):
    def deco(fn):
        return tempDec(*args, **kwargs)(with_context(fn))

    return deco


celery_server.task = my_task
