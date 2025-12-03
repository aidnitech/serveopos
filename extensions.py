from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import threading
import time
from flask import current_app
from services.exchange import fetch_exchange_rates, normalize_rates_dict
from flask_babel import Babel

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
csrf = CSRFProtect()
babel = Babel()


# Currency conversion utility
def convert_currency(amount, from_currency, to_currency, rates):
    """Convert amount from one currency to another using provided rates."""
    if from_currency == to_currency:
        return amount
    # Normalize to USD first, then convert to target currency
    usd_amount = amount / rates.get(from_currency, 1.0)
    converted = usd_amount * rates.get(to_currency, 1.0)
    return round(converted, 2)


def update_exchange_rates(app=None, supported=None):
    """Fetch latest rates and update app config and DB (if available)."""
    app = app or current_app._get_current_object()
    supported = supported or list(app.config.get('EXCHANGE_RATES', {}).keys())
    try:
        res = fetch_exchange_rates(base=app.config.get('BASE_CURRENCY', 'USD'), symbols=supported)
        rates = normalize_rates_dict(res['rates'], supported)
        # Update in-memory config
        app.config['EXCHANGE_RATES'] = rates
        app.config['EXCHANGE_RATES_LAST_UPDATED'] = res.get('timestamp')
        # Persist to DB if available
        try:
            from models import ExchangeRate
            from extensions import db
            with app.app_context():
                for cur, val in rates.items():
                    er = ExchangeRate.query.filter_by(currency=cur).first()
                    if not er:
                        er = ExchangeRate(currency=cur, rate=val)
                        db.session.add(er)
                    else:
                        er.rate = val
                    er.updated_at = res.get('timestamp')
                db.session.commit()
        except Exception:
            # DB might not be available in some contexts; ignore persistence errors
            pass
        return rates
    except Exception as e:
        # On error, just return existing config rates
        return app.config.get('EXCHANGE_RATES', {})


def schedule_exchange_rate_updater(app, interval_seconds=60*60*6):
    """Start a background thread to periodically update exchange rates.

    interval_seconds: default 6 hours
    """
    def _loop():
        while True:
            try:
                update_exchange_rates(app)
            except Exception:
                pass
            time.sleep(interval_seconds)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()


@babel.localeselector
def get_locale():
    """Locale selector used by Flask-Babel. Prefer current_user.locale if available, else accept-language header."""
    try:
        from flask import request
        from flask_login import current_user
        if getattr(current_user, 'is_authenticated', False):
            # fall back to user's currency or role, but ideally add locale field to User
            if hasattr(current_user, 'locale') and current_user.locale:
                return current_user.locale
        # default to request accept languages
        return request.accept_languages.best_match(current_app.config.get('LANGUAGES', ['en']))
    except Exception:
        return 'en'
