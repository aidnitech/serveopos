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

    # Root route
    @app.route("/")
    def index():
        return render_template("base.html")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
