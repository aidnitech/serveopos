from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
csrf = CSRFProtect()


# Currency conversion utility
def convert_currency(amount, from_currency, to_currency, rates):
    """Convert amount from one currency to another using provided rates."""
    if from_currency == to_currency:
        return amount
    # Normalize to USD first, then convert to target currency
    usd_amount = amount / rates.get(from_currency, 1.0)
    converted = usd_amount * rates.get(to_currency, 1.0)
    return round(converted, 2)
