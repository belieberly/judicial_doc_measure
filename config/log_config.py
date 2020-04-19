from logging import config as my_log_config
from celery.utils.log import get_task_logger

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            # 'datefmt': '%m-%d-%Y %H:%M:%S'
            'format': '%(asctime)s \"%(pathname)s：%(module)s:%(funcName)s:%(lineno)d\" [%(levelname)s]- %(message)s'
        }
    },
    'handlers': {
        'celery': {
            # 'level': 'INFO',
            # 'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'your_name.log',
            'when': 'midnight',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'my_celery': {
            'handlers': ['celery'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

my_log_config.dictConfig(LOG_CONFIG)

logger = get_task_logger('my_celery')
