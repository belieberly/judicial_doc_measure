from database import db
from config import DevConfig
from flasgger import Swagger
from Blueprints.writ import blueprint_writ
from Blueprints.writ_report import blueprint_writ_report
from Blueprints.task_report import blueprint_task_report
from Blueprints.my_config import blueprint_my_config
from flask import Flask
from celery import Celery

# celery配置
# app = Flask(__name__)
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'


app = Flask(__name__)
app.config.from_object(DevConfig)
db.init_app(app)

app.register_blueprint(blueprint_writ, url_prefix='/writ')
app.register_blueprint(blueprint_writ_report, url_prefix='/writ_report')
app.register_blueprint(blueprint_task_report, url_prefix='/task_report')
app.register_blueprint(blueprint_my_config, url_prefix='/my_config')

Swagger(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

if __name__ == '__main__':
    app.run(debug=True)
    # 需要在App启动后再调用db
    db.drop_all()
    db.create_all()
