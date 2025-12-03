from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="waiter")  # super_admin/restaurant_admin/manager/waiter/kitchen
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=True)  # Null for super_admin
    currency = db.Column(db.String(3), default="USD")  # e.g., USD, EUR, GBP, INR, etc.
    locale = db.Column(db.String(10), nullable=True)  # e.g., en, es, pt, hi
    is_super_admin = db.Column(db.Boolean, default=False)  # True only for platform super admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 2FA fields
    totp_secret = db.Column(db.String(32), nullable=True)  # Base32-encoded TOTP secret
    totp_enabled = db.Column(db.Boolean, default=False)  # Is 2FA enabled?
    backup_codes = db.Column(db.Text, nullable=True)  # JSON array of backup codes (hashed)
    restaurant = db.relationship('Restaurant', foreign_keys=[restaurant_id], backref='staff')

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default="pending")  # pending, cooking, ready, served
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("OrderItem", backref="order", lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_item.id"))
    quantity = db.Column(db.Integer, default=1)
    menu_item = db.relationship("MenuItem")


class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(32), default="unit")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    old_price = db.Column(db.Float, nullable=False)
    new_price = db.Column(db.Float, nullable=False)
    changed_by = db.Column(db.String(64))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(64))
    action = db.Column(db.String(64))
    object_type = db.Column(db.String(64))
    object_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RolePermission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(64), nullable=False, index=True)
    permission = db.Column(db.String(64), nullable=False, index=True)
    allowed = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('role', 'permission', name='uix_role_permission'),
        {'extend_existing': True}
    )


class Transaction(db.Model):
    """Accounting transactions: income, expense, or refund"""
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # income, expense, refund
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False)  # food, supplies, utilities, etc
    description = db.Column(db.Text)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    recorded_by = db.Column(db.String(64))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Collection(db.Model):
    """Customer payment collection and outstanding balance tracking"""
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(128), nullable=False)
    customer_phone = db.Column(db.String(20))
    total_amount = db.Column(db.Float, nullable=False)  # Total outstanding or order total
    paid_amount = db.Column(db.Float, default=0)  # Amount already paid
    balance = db.Column(db.Float, nullable=False)  # Remaining balance
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, partial, paid, overdue
    notes = db.Column(db.Text)
    last_payment_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Payment(db.Model):
    """Individual payment records for collections"""
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), default='cash')  # cash, card, check, online
    reference_id = db.Column(db.String(128))  # transaction ID, check number, etc
    received_by = db.Column(db.String(64))
    notes = db.Column(db.Text)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    collection = db.relationship('Collection', backref='payments')


class Invoice(db.Model):
    """Simple invoice model linking to orders or collections"""
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(64), unique=True, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=True)
    customer_name = db.Column(db.String(128))
    customer_phone = db.Column(db.String(20))
    items = db.Column(db.Text)  # JSON-serialized items or plain text
    total = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), default='draft')  # draft, issued, paid
    issued_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExchangeRate(db.Model):
    """Store exchange rates per currency with last updated timestamp"""
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(3), nullable=False, index=True)
    rate = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Restaurant(db.Model):
    """Restaurant/merchant account managed by restaurant_admin"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(64))
    country = db.Column(db.String(64))
    postal_code = db.Column(db.String(20))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # restaurant_admin user
    owner = db.relationship('User', foreign_keys=[owner_id], backref='restaurants_owned')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StoreSettings(db.Model):
    """Store-level settings: timezone, locale, currency, tax region, address formats"""
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False, unique=True)
    timezone = db.Column(db.String(64), default='UTC')  # e.g., 'Europe/Dublin', 'America/New_York', 'Asia/Kolkata'
    locale = db.Column(db.String(10), default='en')  # e.g., 'en', 'es', 'pt', 'hi'
    currency = db.Column(db.String(3), default='USD')  # e.g., 'USD', 'EUR', 'INR', 'BRL'
    tax_region = db.Column(db.String(64), default='EU')  # Region code for tax rules (e.g., 'EU', 'US-CA', 'IN')
    address_format = db.Column(db.String(20), default='standard')  # address format: standard, european, asian
    business_registration = db.Column(db.String(128))  # Business/tax registration number
    vat_number = db.Column(db.String(64))  # VAT/GST number
    payment_terms = db.Column(db.Integer, default=0)  # Days for payment terms (0=due on receipt)
    invoice_prefix = db.Column(db.String(10), default='INV')  # Invoice number prefix
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    restaurant = db.relationship('Restaurant', backref='store_settings', uselist=False)

