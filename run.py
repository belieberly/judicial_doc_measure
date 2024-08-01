from database import db
from my_flask import create_apps
from config import USE_WSGI

my_flask_app = create_apps()

if __name__ == '__main__':
    with my_flask_app.app_context():
        # db.drop_all()
        db.create_all()
    # run之后的都不执行
    if not USE_WSGI:
        my_flask_app.run(threaded=True)
    else:
        from waitress import serve                          # type: ignore
        serve(my_flask_app, host="0.0.0.0", port=5000)
