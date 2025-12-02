from flask import render_template, jsonify, request
from flask_login import login_required
from decorators import permission_required
from extensions import db
from models import Order, OrderItem, MenuItem
from . import pos_bp

@pos_bp.route("/")
@login_required
def pos_home():
    try:
        return render_template("pos.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pos_bp.route("/orders", methods=["POST"])
@login_required
@permission_required('manage_orders')
def create_order():
    try:
        data = request.get_json()
        if not data or "items" not in data:
            return jsonify({"error": "Missing items"}), 400
        
        order = Order()
        db.session.add(order)
        db.session.flush()
        
        for item in data["items"]:
            menu_item = MenuItem.query.get(item.get("menu_item_id"))
            if not menu_item:
                return jsonify({"error": f"Menu item {item.get('menu_item_id')} not found"}), 404
            
            quantity = item.get("quantity", 1)
            if quantity < 1:
                return jsonify({"error": "Quantity must be at least 1"}), 400
            
            order_item = OrderItem(order_id=order.id, menu_item_id=menu_item.id, quantity=quantity)
            db.session.add(order_item)
        
        db.session.commit()
        return jsonify({"id": order.id, "status": order.status}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@pos_bp.route("/orders/<int:order_id>", methods=["GET"])
@login_required
def get_order(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        items = []
        for item in order.items:
            items.append({
                "menu_item_id": item.menu_item_id,
                "name": item.menu_item.name,
                "quantity": item.quantity,
                "price": item.menu_item.price,
                "subtotal": item.menu_item.price * item.quantity
            })
        
        return jsonify({
            "id": order.id,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "items": items,
            "total": sum(i["subtotal"] for i in items)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pos_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@login_required
@permission_required('manage_orders')
def update_order_status(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        data = request.get_json()
        new_status = data.get("status")
        valid_statuses = ["pending", "cooking", "ready", "served"]
        
        if new_status not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of {valid_statuses}"}), 400
        
        order.status = new_status
        db.session.commit()
        
        return jsonify({"id": order.id, "status": order.status})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
