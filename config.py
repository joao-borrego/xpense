import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Prevent CSRF attacks
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # SQLAlchemy config

    # Path to database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    # Disable signaling the application on every DB change
    SQLALCHEMY_TRACK_MODIFICATIONS = False
