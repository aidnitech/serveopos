from flask import jsonify
from flask_login import login_required
from decorators import permission_required
from extensions import db
from models import Order, OrderItem, MenuItem
from . import analytics_bp

@analytics_bp.route("/sales")
@login_required
@permission_required('view_analytics')
def sales_summary():
    try:
        total_orders = Order.query.count()
        total_items = OrderItem.query.count()
        total_revenue = db.session.query(db.func.sum(OrderItem.quantity * MenuItem.price)).join(MenuItem).scalar() or 0
        
        return jsonify({
            "total_orders": total_orders,
            "total_items": total_items,
            "total_revenue": float(total_revenue)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
