from flask import Flask                           # type: ignore
from my_celery_client import my_celery_app
from database import db                           # type: ignore
from config import DevConfig, api_allow_origins
from flasgger import Swagger                      # type: ignore
from Blueprints.writ import blueprint_writ
from Blueprints.writ_report import blueprint_writ_report
from Blueprints.task_report import blueprint_task_report
from Blueprints.my_config import blueprint_my_config
from flask_cors import CORS                       # type: ignore
from Blueprints.task import blueprint_task
from Blueprints.user import blueprint_user
import pymysql           # type: ignore
import config
# import shutil
# import os

api_base = config.API_BASE    # alias
swagger_template = {
     "swagger": "2.0",
     "info": {
          "title": "MoocTest Judicial Data Measurement API",
          "description": "API for MoocTest Judicial Data Measurement",
          "version": "0.0.1"
     },
     "basePath": api_base,  # base bash for blueprint registration
     "schemes": [
          "http",
          "https"
     ],
     "operationId": "MoocTestJudicialAPI"
}

def init_database():
    conn = pymysql.connect(host=config.db_hostname,
                           port=config.db_port,
                           user=config.db_username,
                           password=config.db_password)
    cursor = conn.cursor()

    cursor.execute('create database if not exists ' + config.db_name +
                   ' character set utf8mb4 collate utf8mb4_unicode_ci;')
    cursor.close()

# def init_config():
#     target_path = config.transfer_config_path
#     if not os.path.exists(target_path):
#         shutil.copyfile('config/transfer_config.json', target_path)

def create_apps():
    init_database()
    # init_config()
    # __name__是caller的__name__，到时候就是main
    my_flask_app = Flask(__name__)
    Swagger(my_flask_app, template=swagger_template)        # don't know why; it doesn't work
    my_flask_app.config.update(**DevConfig)
    db.init_app(my_flask_app)

    my_flask_app.register_blueprint(blueprint_writ, url_prefix=api_base + '/writ')
    my_flask_app.register_blueprint(blueprint_task, url_prefix=api_base + '/task')
    my_flask_app.register_blueprint(blueprint_writ_report, url_prefix=api_base + '/writ-report')
    my_flask_app.register_blueprint(blueprint_task_report, url_prefix=api_base + '/task-report')
    my_flask_app.register_blueprint(blueprint_my_config, url_prefix=api_base + '/default-config')
    my_flask_app.register_blueprint(blueprint_user, url_prefix=api_base + '/user')

    CORS(my_flask_app, resources={api_base + r"/*": {"origins": api_allow_origins}})
    my_celery_app.conf.update(my_flask_app.config)
    return my_flask_app
