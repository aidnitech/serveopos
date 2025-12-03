from flask import Flask, render_template
from extensions import db, migrate, login_manager, csrf
from config import Config
from blueprints import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    register_blueprints(app)

    # Start exchange rate updater if enabled
    try:
        if app.config.get('ENABLE_EXCHANGE_UPDATER', True):
            from extensions import schedule_exchange_rate_updater, update_exchange_rates
            # perform a first-time immediate update
            with app.app_context():
                update_exchange_rates(app)
            # schedule background updates
            schedule_exchange_rate_updater(app, interval_seconds=app.config.get('EXCHANGE_UPDATE_INTERVAL', 60*60*6))
    except Exception:
        pass

    # Root route
    @app.route("/")
    def index():
        return render_template("base.html")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
