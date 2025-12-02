from flask import jsonify
from models import MenuItem
from . import api_bp

@api_bp.route("/menu")
def menu_json():
    try:
        items = MenuItem.query.all()
        return jsonify([
            {"id": m.id, "name": m.name, "price": m.price, "available": m.available}
            for m in items
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
