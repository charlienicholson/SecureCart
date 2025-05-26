# app/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db, bcrypt

auth_bp = Blueprint("auth", __name__, template_folder="templates")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Registers a new user with fields:
    name, age, email, phone, address, payment_details, password.
    """
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        payment_details = request.form.get("payment_details")
        password = request.form.get("password")

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("auth.login"))

        # Hash the user’s password
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        # Create and store the new user
        new_user = User(
            name=name,
            age=int(age),
            email=email,
            phone=phone,
            address=address,
            payment_details=payment_details,
            password=hashed_pw
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You may now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Logs in an existing user. Checks the hashed password.
    If valid, sets up the user session using Flask-Login.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("You have successfully logged in!", "success")
            # Redirect to shop
            return redirect(url_for("main.list_products"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """
    Logs out the current user and ends the session.
    """
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))



