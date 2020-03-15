from flask import Flask
from my_celery import my_celery_app
from database import db
from config import DevConfig
from flasgger import Swagger
from Blueprints.writ import blueprint_writ
from Blueprints.writ_report import blueprint_writ_report
from Blueprints.task_report import blueprint_task_report
from Blueprints.my_config import blueprint_my_config


def create_apps():
    # __name__是caller的__name__，到时候就是main
    my_flask_app = Flask(__name__)
    my_flask_app.config.from_object(DevConfig)
    db.init_app(my_flask_app)

    my_flask_app.register_blueprint(blueprint_writ, url_prefix='/writ')
    my_flask_app.register_blueprint(blueprint_writ_report, url_prefix='/writ_report')
    my_flask_app.register_blueprint(blueprint_task_report, url_prefix='/task_report')
    my_flask_app.register_blueprint(blueprint_my_config, url_prefix='/my_config')

    Swagger(my_flask_app)
    my_celery_app.conf.update(my_flask_app.config)
    return my_flask_app, my_celery_app
