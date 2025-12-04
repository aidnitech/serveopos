import pytest

from app import create_app
from extensions import db

# Create an application for the test session and ensure the DB schema exists
app = create_app()
app.config.setdefault("WTF_CSRF_ENABLED", False)

# Ensure schema exists as soon as conftest is imported (before test collection)
with app.app_context():
    try:
        db.create_all()
    except Exception:
        pass
    # Seed minimal data expected by tests if not present
    try:
        from werkzeug.security import generate_password_hash
        from models import User, MenuItem

        if User.query.count() == 0:
            admin = User(username="admin", password_hash=generate_password_hash("admin"), role="admin")
            waiter = User(username="waiter", password_hash=generate_password_hash("waiter"), role="waiter")
            kitchen = User(username="kitchen", password_hash=generate_password_hash("kitchen"), role="kitchen")
            manager = User(username="manager", password_hash=generate_password_hash("manager"), role="manager")
            db.session.add_all([admin, waiter, kitchen, manager])
            db.session.commit()

        if MenuItem.query.count() == 0:
            db.session.add(MenuItem(name="Chicken Sizzler", description="Hot sizzling platter", price=45.0))
            db.session.add(MenuItem(name="Paneer Tikka Sizzler", description="Vegetarian delight", price=40.0))
            db.session.add(MenuItem(name="Pasta Alfredo", description="Continental creamy pasta", price=35.0))
            db.session.commit()
    except Exception:
        # If models are not available or seeding fails, continue; tests will fail later with clear errors.
        pass


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Session fixture to optionally teardown DB after the test session."""
    # Tables are created at import time to avoid race conditions with test collection.
    yield

    with app.app_context():
        try:
            db.drop_all()
        except Exception:
            pass
