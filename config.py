import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.abspath('instance/app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ["en", "ro"]
