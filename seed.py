from app import create_app
from extensions import db
from models import User, MenuItem
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.first():
        admin = User(username="admin", password_hash=generate_password_hash("admin"), role="admin")
        waiter = User(username="waiter", password_hash=generate_password_hash("waiter"), role="waiter")
        kitchen = User(username="kitchen", password_hash=generate_password_hash("kitchen"), role="kitchen")
        manager = User(username="manager", password_hash=generate_password_hash("manager"), role="manager")
        db.session.add_all([admin, waiter, kitchen, manager])
        db.session.commit()
        print("Users created: admin/admin, waiter/waiter, kitchen/kitchen, manager/manager")

    if not MenuItem.query.first():
        db.session.add(MenuItem(name="Chicken Sizzler", description="Hot sizzling platter", price=45.0))
        db.session.add(MenuItem(name="Paneer Tikka Sizzler", description="Vegetarian delight", price=40.0))
        db.session.add(MenuItem(name="Pasta Alfredo", description="Continental creamy pasta", price=35.0))
        db.session.commit()
        print("Sample menu items added.")
