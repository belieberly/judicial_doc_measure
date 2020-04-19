from database import db
from my_flask import create_apps

my_flask_app = create_apps()


if __name__ == '__main__':
    with my_flask_app.app_context():
        # db.drop_all()
        db.create_all()
    # run之后的都不执行
    my_flask_app.run(threaded=True)
