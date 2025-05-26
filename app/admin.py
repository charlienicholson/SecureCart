from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import current_user, login_required
from . import db
from .models import User, Order, OrderItem, Product

admin_bp = Blueprint("admin", __name__, template_folder="templates")

def admin_required(f): #decorator is current user admin, like the default login required type
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/portal")
@login_required
@admin_required
def admin_portal():
    return render_template("admin_portal.html")



@admin_bp.route("/dashboard")
@login_required
@admin_required
def admin_dashboard():
    """
    Admin dashboard used for displaying and editing the databases in the website.
    """
    users = User.query.all()
    products = Product.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    print("User count:", len(users))
    print("Product count:", len(products))
    print("Order count:", len(orders))
    
    return render_template("admin_dashboard.html", users=users, products=products, orders=orders)


@admin_bp.route("/products/add", methods=["GET", "POST"])
@login_required
@admin_required
def admin_add_product():
    """
    Provides a form for an admin to add a new product to the products table.
    """
    if request.method == "POST":
        # Retrieve form data
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")
        stock = request.form.get("stock")
        
        # Validate required fields
        if not name or not price or not stock:
            flash("Name, price, and stock are required fields.", "danger")
            return redirect(url_for("admin.admin_add_product"))
        
        # Validate numeric fields
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            flash("Invalid input for price or stock.", "danger")
            return redirect(url_for("admin.admin_add_product"))
        
        # Create a new Product instance
        new_product = Product(
            name=name,
            description=description,
            price=price,
            category=category,
            stock=stock
        )
        
        # Insert into the database
        db.session.add(new_product)
        db.session.commit()
        
        flash("Product added successfully.", "success")
        return redirect(url_for("admin.admin_dashboard"))
    
    # For GET requests, render the add product form
    return render_template("admin_add_product.html")

#vvvvv UPDATES WITHIN TABLES WITHIN THE DASHBOARD.


# UPDATE USER
# -----------------------------
@admin_bp.route("/users/update/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    new_name = request.form.get("name")
    new_email = request.form.get("email")
    new_is_admin = request.form.get("is_admin")

    if new_name:
        user.name = new_name
    if new_email:
        user.email = new_email
    if new_is_admin is not None:
        user.is_admin = (new_is_admin == "1")

    db.session.commit()
    return jsonify({"success": True, "message": "User updated successfully."})

# UPDATE PRODUCT
# -----------------------------
@admin_bp.route("/products/update/<int:product_id>", methods=["POST"])
@login_required
@admin_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    new_name = request.form.get("name")
    new_price = request.form.get("price")
    new_stock = request.form.get("stock")

    try:
        new_price = float(new_price) if new_price else product.price
        new_stock = int(new_stock) if new_stock else product.stock
    except ValueError:
        return jsonify({"success": False, "message": "Invalid input for price or stock."}), 400

    if new_name:
        product.name = new_name
    product.price = new_price
    product.stock = new_stock

    db.session.commit()
    return jsonify({"success": True, "message": "Product updated successfully."})

# UPDATE ORDER
# -----------------------------
@admin_bp.route("/orders/update/<int:order_id>", methods=["POST"])
@login_required
@admin_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    if new_status:
        order.status = new_status

    db.session.commit()
    return jsonify({"success": True, "message": "Order updated successfully."})
    

@admin_bp.route("/users")
@login_required
@admin_required
def admin_users():
    
    #Shows all registered users.
    
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@admin_bp.route("/orders")
@login_required
@admin_required
def admin_orders():
    
    #Shows all orders for all users.
   
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin_orders.html", orders=orders)

@admin_bp.route("/orders/<int:order_id>/update-status", methods=["POST"])
@login_required
@admin_required
def update_order_status(order_id):
    
    #Updates the status of a given order (received, shipped, delivered, etc.)
    
    new_status = request.form.get("status")
    order = Order.query.get_or_404(order_id)
    order.status = new_status
    db.session.commit()
    flash(f"Order #{order.id} status updated to {order.status}.", "success")
    return redirect(url_for("admin.admin_orders"))
