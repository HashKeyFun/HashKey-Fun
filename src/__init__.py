import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'hashkeyfun.sqlite'),
        S3_REGION=os.environ.get('AWS_S3_BUCKET_REGION'),
        S3_ACCESS_KEY=os.environ.get('AWS_S3_ACCESS_KEY'),
        S3_SECRET_KEY=os.environ.get('AWS_S3_SECRET_KEY'),
        S3_BUCKET_NAME=os.environ.get('AWS_S3_BUCKET_NAME'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db, file
    db.init_app(app)

    app.register_blueprint(file.bp)

    return app
