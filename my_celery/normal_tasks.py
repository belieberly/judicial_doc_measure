from my_celery import my_celery_app


@my_celery_app.task
def add(x, y):
    """
    :param x:
    :param y:
    :return:
    """
    return str(x + y)