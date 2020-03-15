from my_flask import create_apps

my_flask_app, my_celery_app = create_apps()


if __name__ == '__main__':
    my_flask_app.app_context().push()
    my_flask_app.run()
