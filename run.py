from database import db
from my_flask import create_apps

my_flask_app = create_apps()


if __name__ == '__main__':
    my_flask_app.run()
    with my_flask_app.app_context():
        db.drop_all()
        db.create_all()
