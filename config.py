import os

class Config(object):
    # Can (should?) use an environment variable to set this
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
    UPLOAD_PATH = 'uploads'

    error_duplicate = False
    error_tag_not_added = False
    error_tag_found = False
    form_error = False

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'correcthorsebatterystaple'  # https://xkcd.com/936/

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///photo_database.db'

    # Track Modifications is deprecated and older versions of
    # SQLAlchemy might warn you about it - this stops the warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLALCHEMY_ECHO shows the SQL commands it used to execute
    # a query in the console - can be useful, can also be
    # confuzzling
    SQLALCHEMY_ECHO = False