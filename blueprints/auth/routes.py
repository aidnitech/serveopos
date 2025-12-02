from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from extensions import db, login_manager
from models import User
from . import auth_bp

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Logged in successfully", "success")
            if user.role in ["admin", "manager"]:
                return redirect(url_for("admin.dashboard"))
            elif user.role == "waiter":
                return redirect(url_for("pos.pos_home"))
            elif user.role == "kitchen":
                return redirect(url_for("kds.pending_orders"))
            else:
                return redirect(url_for("menu.show_menu"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))
