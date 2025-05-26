# app/main.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Product
from .models import Product, CartItem, Order, OrderItem
from flask_login import login_required, current_user
from .models import User, Product, CartItem, Order, OrderItem
from . import db, bcrypt 

main_bp = Blueprint("main", __name__, template_folder="templates")

@main_bp.route("/")
def index():
    
    #Renders the home page. Users can see this even if not logged in.
    
    return render_template("index.html")
    
'''
@main_bp.route("/seed-admin")
def seed_admin():
    """
    Creates a default admin user (admin@example.com / admin).
    WARNING: For demo only, do not use in production.
    """
    existing_admin = User.query.filter_by(email="admin@example.com").first()
    if existing_admin:
        flash("Admin user already exists.", "info")
        return redirect(url_for("main.index"))

    hashed_pw = bcrypt.generate_password_hash("admin").decode("utf-8")
    admin_user = User(
        name="Administrator",
        age=30,
        email="admin@example.com",
        phone="123456789",
        address="Admin HQ",
        payment_details="N/A",
        password=hashed_pw,
        is_admin=True
    )
    db.session.add(admin_user)
    db.session.commit()

    flash("Default admin user created (email: admin@example.com, password: admin).", "success")
    return redirect(url_for("main.index"))
'''
@main_bp.route("/products")
def list_products():
    """
    Lists products. Optional filters:
      ?category=someCategory
      ?min_price=10
      ?max_price=100
    """
    category = request.args.get("category")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    # start with the base query
    query = Product.query

    # Filter by category if provided
    if category:
        query = query.filter(Product.category == category)

    # Filter by min_price
    if min_price:
        try:
            min_val = float(min_price)
            query = query.filter(Product.price >= min_val)
        except ValueError:
            pass  # ignore if invalid input

    # Filter by max_price
    if max_price:
        try:
            max_val = float(max_price)
            query = query.filter(Product.price <= max_val)
        except ValueError:
            pass

    products = query.all()
    return render_template("products.html", products=products)

@main_bp.route("/user-portal")
def user_portal():
    # Return a template or simple string for demonstration
    return render_template("user_portal.html", user=current_user)

@login_required
@main_bp.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    """
    Adds a product to the current user's cart. If product is already in the cart,
    just increase the quantity. Requires the user to be logged in.
    """
    product = Product.query.get_or_404(product_id)

    # Check if there's already a CartItem for this user & product
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        # Increase quantity
        cart_item.quantity += 1
    else:
        # Create a new cart item
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash(f"Added {product.name} to cart.", "success")
    return redirect(url_for("main.list_products"))

@main_bp.route("/cart")
@login_required
def view_cart():

    #Shows all items in the current user's cart.
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    # Calculate a total if you want
    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity

    return render_template("cart.html", cart_items=cart_items, total=total)



@main_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():

    #Finalizes the user's cart into an Order and clears the cart.

    # Get all cart items
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Your cart is empty!", "warning")
        return redirect(url_for("main.view_cart"))

    # Create a new order
    new_order = Order(user_id=current_user.id, status="received")
    db.session.add(new_order)
    db.session.commit() 

    # For each cart item, create an OrderItem
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.product.price
        )
        db.session.add(order_item)

    db.session.commit()

    # Clear the cart
    for item in cart_items:
        db.session.delete(item)
    db.session.commit()

    flash(f"Order #{new_order.id} has been created! Status: {new_order.status}", "success")
    return redirect(url_for("main.index"))


@main_bp.route("/my-orders")
@login_required
def my_orders():

    #Shows all orders of the current user.

    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("my_orders.html", orders=orders)
    
@main_bp.route("/order/<int:order_id>")
@login_required
def order_detail(order_id):

    #Displays detailed information about a single order.

    order = Order.query.get_or_404(order_id)
    return render_template("order_detail.html", order=order)

@main_bp.route("/user-portal/update", methods=["POST"])
@login_required
def update_user_portal():

    user = current_user  # This is the user who is logged in
    
    new_name = request.form.get("name")
    new_email = request.form.get("email")
    new_phone = request.form.get("phone")
    new_address = request.form.get("address")
    new_payment = request.form.get("payment_details")
    
    # Update fields if they're provided
    if new_name:
        user.name = new_name
    if new_email:
        user.email = new_email
    if new_phone:
        user.phone = new_phone
    if new_address:
        user.address = new_address
    if new_payment:
        user.payment_details = new_payment
    
    db.session.commit()
    
    return jsonify({"success": True, "message": "User profile updated successfully!"})