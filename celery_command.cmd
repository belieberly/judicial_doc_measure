conda activate judicial
celery -A my_celery_server.tasks worker -l info