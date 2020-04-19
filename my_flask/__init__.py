from flask import Flask
from my_celery_client import my_celery_app
from database import db
from config import DevConfig, api_allow_origins
from flasgger import Swagger
from Blueprints.writ import blueprint_writ
from Blueprints.writ_report import blueprint_writ_report
from Blueprints.task_report import blueprint_task_report
from Blueprints.my_config import blueprint_my_config
from flask_cors import CORS
from task import blueprint_task
from user import blueprint_user


def create_apps():
    # __name__是caller的__name__，到时候就是main
    my_flask_app = Flask(__name__)

    my_flask_app.config.update(**DevConfig)
    db.init_app(my_flask_app)

    my_flask_app.register_blueprint(blueprint_writ, url_prefix='/api/v2/writ')
    my_flask_app.register_blueprint(blueprint_task, url_prefix='/api/v2/task')
    my_flask_app.register_blueprint(blueprint_writ_report, url_prefix='/api/v2/writ-report')
    my_flask_app.register_blueprint(blueprint_task_report, url_prefix='/api/v2/task-report')
    my_flask_app.register_blueprint(blueprint_my_config, url_prefix='/api/v2/default-config')
    my_flask_app.register_blueprint(blueprint_user, url_prefix='/api/v2/user')


    CORS(my_flask_app,
         resources={r"/api/v2/*": {"origins": api_allow_origins}})
    Swagger(my_flask_app)
    my_celery_app.conf.update(my_flask_app.config)
    return my_flask_app
