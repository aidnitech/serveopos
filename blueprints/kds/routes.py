from flask import jsonify
from flask_login import login_required
from models import Order, OrderItem
from decorators import permission_required
from . import kds_bp

@kds_bp.route("/orders")
@login_required
@permission_required('manage_orders')
def pending_orders():
    try:
        orders = Order.query.filter_by(status="pending").all()
        order_data = []
        for o in orders:
            items = []
            for item in o.items:
                items.append({
                    "name": item.menu_item.name,
                    "quantity": item.quantity,
                    "price": item.menu_item.price
                })
            order_data.append({
                "id": o.id,
                "status": o.status,
                "created_at": o.created_at.isoformat(),
                "items": items
            })
        return jsonify(order_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
