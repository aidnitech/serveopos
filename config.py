import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.abspath('instance/app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ["en", "ro"]
    # Currency support: base currency and exchange rates
    BASE_CURRENCY = "USD"
    EXCHANGE_RATES = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "INR": 83.12,
        "RON": 4.97,
        "CAD": 1.32,
        "AUD": 1.52,
        "JPY": 149.50,
        "CNY": 7.24,
        "AED": 3.67,
    }
    ENABLE_EXCHANGE_UPDATER = True
    EXCHANGE_UPDATE_INTERVAL = 60*60*6  # 6 hours
