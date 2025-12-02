from flask import render_template, jsonify
from flask_login import login_required
from models import MenuItem
from . import menu_bp

@menu_bp.route("/")
@login_required
def show_menu():
    try:
        items = MenuItem.query.all()
        return render_template("menu.html", items=items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
