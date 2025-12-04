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


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Session fixture: create schema at start, drop at end."""
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            pass
    
    yield

    with app.app_context():
        try:
            db.drop_all()
        except Exception:
            pass


@pytest.fixture(scope="function", autouse=True)
def reset_db():
    """Function fixture: clear tables before each test and seed basic data."""
    with app.app_context():
        # Clear all data (but keep schema)
        for table in reversed(db.metadata.sorted_tables):
            try:
                db.session.execute(table.delete())
            except Exception:
                pass
        db.session.commit()

        # Seed basic users and menu items expected by tests
        try:
            from werkzeug.security import generate_password_hash
            from models import User, MenuItem

            admin = User(username="admin", password_hash=generate_password_hash("admin"), role="admin")
            waiter = User(username="waiter", password_hash=generate_password_hash("waiter"), role="waiter")
            kitchen = User(username="kitchen", password_hash=generate_password_hash("kitchen"), role="kitchen")
            manager = User(username="manager", password_hash=generate_password_hash("manager"), role="manager")
            db.session.add_all([admin, waiter, kitchen, manager])
            
            db.session.add(MenuItem(name="Chicken Sizzler", description="Hot sizzling platter", price=45.0))
            db.session.add(MenuItem(name="Paneer Tikka Sizzler", description="Vegetarian delight", price=40.0))
            db.session.add(MenuItem(name="Pasta Alfredo", description="Continental creamy pasta", price=35.0))
            db.session.commit()
        except Exception:
            pass

    yield

    # Clean up after test
    with app.app_context():
        try:
            db.session.rollback()
        except Exception:
            pass
