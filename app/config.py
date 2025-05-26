import os

class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY") or "CHANGE_ME_IN_PRODUCTION"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///secure_portal.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False