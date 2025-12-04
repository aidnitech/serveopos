from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from decorators import permission_required
from extensions import db
from datetime import datetime
from models import (
    Order, OrderItem, MenuItem, Product, ProductCategory, BarcodeMapping,
    PaymentMethod, PaymentTransaction, Discount, BillSplit, Receipt,
    Table, TableSection, RestaurantFloorPlan, OrderNote, DelayedOrder, Kiosk,
    Customer, LoyaltyCard, LoyaltyPoints, eWallet, eWalletTransaction, PriceList, PriceListItem,
    CashierAccount, CashRegister, CashFlow, HardwareDevice, Restaurant
)
from . import pos_bp
from .services import (
    calculate_order_total, apply_discount, process_payment,
    handle_bill_split, add_loyalty_points, topup_ewallet
)

# ============================================================================
# MAIN POS INTERFACE
# ============================================================================
@pos_bp.route("/")
@login_required
def pos_home():
    try:
        return render_template("pos.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# PRODUCTS & CATEGORIES
# ============================================================================
@pos_bp.route("/products", methods=["GET"])
@login_required
def list_products():
    """List all products with optional category filter"""
    try:
        restaurant_id = current_user.restaurant_id
        category_id = request.args.get("category_id", type=int)
        search = request.args.get("search", "")
        
        query = Product.query.filter_by(restaurant_id=restaurant_id, active=True, available=True)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if search:
            query = query.filter(
                (Product.name.ilike(f"%{search}%")) |
                (Product.description.ilike(f"%{search}%")) |
                (Product.sku.ilike(f"%{search}%"))
            )
        
        products = query.all()
        return jsonify([{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.base_price,
            "cost": p.cost,
            "category_id": p.category_id,
            "sku": p.sku,
            "requires_weight": p.requires_weight,
            "unit_of_measure": p.unit_of_measure,
            "is_gift_card": p.is_gift_card
        } for p in products])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/products/by-barcode/<barcode>", methods=["GET"])
@login_required
def get_product_by_barcode(barcode):
    """Lookup product by barcode"""
    try:
        barcode_mapping = BarcodeMapping.query.filter_by(barcode=barcode).first()
        if not barcode_mapping:
            return jsonify({"error": "Barcode not found"}), 404
        
        product = barcode_mapping.product
        price = barcode_mapping.embedded_price or product.base_price
        
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": price,
            "barcode": barcode,
            "variant_id": barcode_mapping.variant_id,
            "embedded_weight": barcode_mapping.embedded_weight,
            "loyalty_points": barcode_mapping.loyalty_points
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/categories", methods=["GET"])
@login_required
def list_categories():
    """List product categories"""
    try:
        restaurant_id = current_user.restaurant_id
        categories = ProductCategory.query.filter_by(restaurant_id=restaurant_id, active=True).all()
        return jsonify([{
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "parent_id": c.parent_id,
            "display_order": c.display_order
        } for c in categories])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ORDERS & CHECKOUT
# ============================================================================
@pos_bp.route("/orders", methods=["POST"])
@login_required
@permission_required('manage_orders')
def create_order():
    """Create a new order"""
    try:
        data = request.get_json()
        if not data or "items" not in data:
            return jsonify({"error": "Missing items"}), 400
        
        order = Order()
        db.session.add(order)
        db.session.flush()
        
        for item in data["items"]:
            # Accept either menu_item_id (MenuItem) or product_id (Product)
            menu_item = None
            if item.get("menu_item_id"):
                menu_item = MenuItem.query.get(item.get("menu_item_id"))
            elif item.get("product_id"):
                # product may be a Product record; try to map to MenuItem first
                product = Product.query.get(item.get("product_id"))
                if product:
                    # if there's a MenuItem with same id (legacy), use it; otherwise create a lightweight mapping
                    menu_item = MenuItem.query.get(product.id)
                    if not menu_item:
                        # create temporary placeholder-like object using product fields
                        class _Tmp:
                            pass
                        menu_item = _Tmp()
                        menu_item.id = product.id
                        menu_item.name = product.name
                        menu_item.price = getattr(product, 'base_price', getattr(product, 'price', 0))

            if not menu_item:
                return jsonify({"error": f"Menu/Product not found for item {item}"}), 404

            quantity = int(item.get("quantity", 1))
            if quantity < 1:
                return jsonify({"error": "Quantity must be at least 1"}), 400

            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=quantity
            )
            db.session.add(order_item)
            
            # Add order notes if provided
            if "notes" in item:
                for note in item["notes"]:
                    order_note = OrderNote(
                        order_item_id=order_item.id,
                        note_type=note.get("type", "special_request"),
                        content=note.get("content")
                    )
                    db.session.add(order_note)
        
        db.session.commit()
        return jsonify({"id": order.id, "status": order.status}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/orders/<int:order_id>", methods=["GET"])
@login_required
def get_order(order_id):
    """Get order details"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        items = []
        from models import Product
        for item in order.items:
            # menu_item may be None if OrderItem references a Product id instead
            menu = item.menu_item
            if not menu:
                menu = Product.query.get(item.menu_item_id)
            name = getattr(menu, 'name', None)
            price = getattr(menu, 'price', getattr(menu, 'base_price', 0))
            items.append({
                "id": item.id,
                "product_id": item.menu_item_id,
                "name": name,
                "quantity": item.quantity,
                "price": price,
                "subtotal": price * item.quantity,
                "notes": [{"type": n.note_type, "content": n.content} for n in item.notes]
            })
        
        total = calculate_order_total([{"price": i["price"], "quantity": i["quantity"]} for i in items])
        
        return jsonify({
            "id": order.id,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "items": items,
            "total": total,
            "payments": [{"id": p.id, "amount": p.amount, "method": p.payment_method.name} for p in order.payments]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@login_required
@permission_required('manage_orders')
def update_order_status(order_id):
    """Update order status"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        data = request.get_json()
        new_status = data.get("status")
        valid_statuses = ["pending", "cooking", "ready", "served", "completed", "cancelled"]
        
        if new_status not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of {valid_statuses}"}), 400
        
        order.status = new_status
        db.session.commit()
        
        return jsonify({"id": order.id, "status": order.status})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/orders/<int:order_id>/parallel", methods=["PUT"])
@login_required
@permission_required('manage_orders')
def put_order_aside(order_id):
    """Put order aside and process another order (parallel orders)"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        order.status = "hold"
        db.session.commit()
        
        return jsonify({"message": "Order put aside", "id": order.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/orders/<int:order_id>/discount", methods=["POST"])
@login_required
@permission_required('manage_orders')
def apply_order_discount(order_id):
    """Apply discount to order"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        data = request.get_json()
        discount = apply_discount(order, data)
        
        db.session.commit()
        return jsonify({"message": "Discount applied", "discount": discount})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ============================================================================
# PAYMENTS & CHECKOUT
# ============================================================================
@pos_bp.route("/orders/<int:order_id>/checkout", methods=["POST"])
@login_required
@permission_required('manage_payments')
def checkout_order(order_id):
    """Process payment for order"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        data = request.get_json()
        payment_result = process_payment(order, data, current_user)
        
        if payment_result.get("success"):
            order.status = "completed"
            db.session.commit()
            return jsonify(payment_result), 200
        else:
            return jsonify(payment_result), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/orders/<int:order_id>/split-bill", methods=["POST"])
@login_required
@permission_required('manage_payments')
def split_bill(order_id):
    """Split bill between multiple payment methods"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        data = request.get_json()
        splits = handle_bill_split(order, data)
        
        db.session.commit()
        return jsonify({"splits": splits, "total": len(splits)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/payment-methods", methods=["GET"])
@login_required
def list_payment_methods():
    """List available payment methods"""
    try:
        restaurant_id = current_user.restaurant_id
        methods = PaymentMethod.query.filter_by(restaurant_id=restaurant_id, active=True).all()
        return jsonify([{
            "id": m.id,
            "name": m.name,
            "payment_type": m.payment_type,
            "requires_terminal": m.requires_external_terminal,
            "currency_rounding": m.currency_rounding
        } for m in methods])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# RESTAURANT MANAGEMENT
# ============================================================================
@pos_bp.route("/tables", methods=["GET"])
@login_required
def list_tables():
    """List all tables with status"""
    try:
        restaurant_id = current_user.restaurant_id
        floor_plan = RestaurantFloorPlan.query.filter_by(restaurant_id=restaurant_id).first()
        if not floor_plan:
            return jsonify({"tables": []}), 200
        
        tables = Table.query.join(TableSection).filter(TableSection.floor_plan_id == floor_plan.id).all()
        return jsonify({"tables": [{
            "id": t.id,
            "number": t.table_number,
            "seats": t.seats,
            "section": t.section.name,
            "status": t.status,
            "reserved_until": t.reserved_until.isoformat() if t.reserved_until else None
        } for t in tables]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/tables/<int:table_id>/assign", methods=["POST"])
@login_required
@permission_required('manage_tables')
def assign_table(table_id):
    """Assign order to table"""
    try:
        table = Table.query.get(table_id)
        if not table:
            return jsonify({"error": "Table not found"}), 404
        
        data = request.get_json()
        order_id = data.get("order_id")
        customer_name = data.get("customer_name")
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        table.current_order_id = order_id
        table.status = "occupied"
        db.session.commit()
        
        return jsonify({"message": "Table assigned", "table_id": table_id, "order_id": order_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/tables/<int:table_id>/transfer", methods=["POST"])
@login_required
@permission_required('manage_tables')
def transfer_table(table_id):
    """Transfer customers from one table to another"""
    try:
        source_table = Table.query.get(table_id)
        if not source_table:
            return jsonify({"error": "Source table not found"}), 404
        
        data = request.get_json()
        dest_table_id = data.get("destination_table_id")
        dest_table = Table.query.get(dest_table_id)
        if not dest_table:
            return jsonify({"error": "Destination table not found"}), 404
        
        order_id = source_table.current_order_id
        
        dest_table.current_order_id = order_id
        dest_table.status = "occupied"
        source_table.current_order_id = None
        source_table.status = "available"
        
        db.session.commit()
        return jsonify({"message": "Table transfer completed"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/delayed-orders", methods=["POST"])
@login_required
@permission_required('manage_orders')
def create_delayed_order():
    """Create delayed order for multiple courses"""
    try:
        data = request.get_json()
        order_id = data.get("order_id")
        course_number = data.get("course_number", 1)
        delay_minutes = data.get("delay_minutes", 0)
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        delayed_order = DelayedOrder(
            order_id=order_id,
            course_number=course_number,
            delay_minutes=delay_minutes
        )
        db.session.add(delayed_order)
        db.session.commit()
        
        return jsonify({"id": delayed_order.id, "course": course_number}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/kiosk/<kiosk_code>/menu", methods=["GET"])
@login_required
def kiosk_menu(kiosk_code):
    """Get menu for self-service kiosk"""
    try:
        kiosk = Kiosk.query.filter_by(kiosk_code=kiosk_code, active=True).first()
        if not kiosk:
            return jsonify({"error": "Kiosk not found"}), 404
        
        restaurant = kiosk.restaurant
        categories = ProductCategory.query.filter_by(restaurant_id=restaurant.id, active=True).all()
        products = Product.query.filter_by(restaurant_id=restaurant.id, active=True, available=True).all()
        
        return jsonify({
            "kiosk_name": kiosk.name,
            "categories": [{"id": c.id, "name": c.name} for c in categories],
            "products": [{
                "id": p.id,
                "name": p.name,
                "price": p.base_price,
                "category_id": p.category_id,
                "image_url": p.image_url
            } for p in products]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CUSTOMER LOYALTY
# ============================================================================
@pos_bp.route("/customers/search", methods=["GET"])
@login_required
def search_customers():
    """Search customers by name, email, phone, or barcode"""
    try:
        restaurant_id = current_user.restaurant_id
        query_term = request.args.get("q", "")
        
        customers = Customer.query.filter_by(restaurant_id=restaurant_id).filter(
            (Customer.name.ilike(f"%{query_term}%")) |
            (Customer.email.ilike(f"%{query_term}%")) |
            (Customer.phone.ilike(f"%{query_term}%")) |
            (Customer.barcode.ilike(f"%{query_term}%"))
        ).all()
        
        # Be defensive: fetch loyalty card / wallet via queries to avoid
        # surprises if relationships are configured differently.
        out = []
        from models import LoyaltyCard, eWallet as EWalletModel
        for c in customers:
            loyalty = LoyaltyCard.query.filter_by(customer_id=c.id).first()
            wallet = EWalletModel.query.filter_by(customer_id=c.id).first()
            out.append({
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "loyalty_points": loyalty.points_balance if loyalty else 0,
                "ewallet_balance": wallet.balance if wallet else 0
            })
        return jsonify(out)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/customers/<int:customer_id>/loyalty", methods=["GET"])
@login_required
def get_customer_loyalty(customer_id):
    """Get customer loyalty information"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        # Defensive fetch in case relationships are lists or misconfigured
        from models import LoyaltyCard, eWallet as EWalletModel
        loyalty_card = LoyaltyCard.query.filter_by(customer_id=customer.id).first()
        wallet = EWalletModel.query.filter_by(customer_id=customer.id).first()

        return jsonify({
            "customer_id": customer.id,
            "name": customer.name,
            "loyalty_points": loyalty_card.points_balance if loyalty_card else 0,
            "loyalty_tier": loyalty_card.tier if loyalty_card else None,
            "ewallet_balance": wallet.balance if wallet else 0,
            "ewallet_currency": wallet.currency if wallet else None,
            "credit_limit": customer.credit_limit,
            "outstanding_balance": customer.outstanding_balance
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/customers/<int:customer_id>/loyalty/redeem", methods=["POST"])
@login_required
@permission_required('manage_loyalty')
def redeem_loyalty_points(customer_id):
    """Redeem loyalty points"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Defensive lookup for loyalty card
        from models import LoyaltyCard
        loyalty_card = LoyaltyCard.query.filter_by(customer_id=customer.id).first()
        if not loyalty_card:
            return jsonify({"error": "Loyalty card not found"}), 404

        data = request.get_json() or {}
        reward_id = data.get("reward_id")
        points_to_redeem = int(data.get("points", 0))

        if loyalty_card.points_balance < points_to_redeem:
            return jsonify({"error": "Insufficient loyalty points"}), 400

        loyalty_card.points_balance -= points_to_redeem
        loyalty_card.points_redeemed_total += points_to_redeem

        points_record = LoyaltyPoints(
            loyalty_card_id=loyalty_card.id,
            points=-points_to_redeem,
            earn_method="redemption",
            description=f"Redeemed {points_to_redeem} points"
        )
        db.session.add(points_record)
        db.session.commit()

        return jsonify({"message": "Points redeemed", "remaining_points": loyalty_card.points_balance})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/customers/<int:customer_id>/ewallet/topup", methods=["POST"])
@login_required
@permission_required('manage_payments')
def topup_ewallet_endpoint(customer_id):
    """Top-up customer e-wallet"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Defensive lookup for wallet
        from models import eWallet as EWalletModel
        wallet = EWalletModel.query.filter_by(customer_id=customer.id).first()
        if not wallet:
            return jsonify({"error": "E-wallet not found"}), 404

        data = request.get_json() or {}
        amount = float(data.get("amount", 0))
        payment_method_id = data.get("payment_method_id")

        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400

        topup_ewallet(wallet, amount, payment_method_id)
        db.session.commit()

        return jsonify({"message": "E-wallet topped up", "new_balance": wallet.balance})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ============================================================================
# RECEIPTS
# ============================================================================
@pos_bp.route("/orders/<int:order_id>/receipt", methods=["GET"])
@login_required
def get_receipt(order_id):
    """Generate and return receipt"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        receipt = Receipt.query.filter_by(order_id=order_id).first()
        if not receipt:
            return jsonify({"error": "Receipt not found"}), 404
        
        return jsonify({
            "id": receipt.id,
            "receipt_number": receipt.receipt_number,
            "content": receipt.content,
            "header": receipt.header_text,
            "footer": receipt.footer_text,
            "created_at": receipt.created_at.isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/orders/<int:order_id>/receipt/print", methods=["POST"])
@login_required
@permission_required('manage_receipts')
def print_receipt(order_id):
    """Mark receipt as printed"""
    try:
        receipt = Receipt.query.filter_by(order_id=order_id).first()
        if not receipt:
            return jsonify({"error": "Receipt not found"}), 404
        
        receipt.printed = True
        receipt.printed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"message": "Receipt printed"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CASH MANAGEMENT
# ============================================================================
@pos_bp.route("/cash-registers/open", methods=["POST"])
@login_required
@permission_required('manage_cash')
def open_cash_register():
    """Open cash register for cashier"""
    try:
        data = request.get_json()
        register_id = data.get("register_id")
        opening_balance = data.get("opening_balance", 0)
        
        register = CashRegister.query.get(register_id)
        if not register:
            return jsonify({"error": "Cash register not found"}), 404
        
        if register.status == "opened":
            return jsonify({"error": "Register already open"}), 400
        
        register.opening_balance = opening_balance
        register.current_balance = opening_balance
        register.opened_at = datetime.utcnow()
        register.status = "opened"
        register.current_cashier_id = current_user.cashier_account.id if current_user.cashier_account else None
        
        db.session.commit()
        return jsonify({"message": "Cash register opened", "id": register.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@pos_bp.route("/cash-registers/<int:register_id>/close", methods=["POST"])
@login_required
@permission_required('manage_cash')
def close_cash_register(register_id):
    """Close cash register and reconcile"""
    try:
        data = request.get_json()
        actual_balance = data.get("actual_balance")
        
        register = CashRegister.query.get(register_id)
        if not register:
            return jsonify({"error": "Cash register not found"}), 404
        
        if register.status == "closed":
            return jsonify({"error": "Register already closed"}), 400
        
        register.closed_at = datetime.utcnow()
        register.status = "closed"
        
        # Create cash flow record for reconciliation
        cash_flow = CashFlow(
            cash_register_id=register_id,
            adjustment_type="closing_balance",
            amount=actual_balance,
            expected_balance=register.current_balance,
            actual_balance=actual_balance,
            variance=actual_balance - register.current_balance,
            recorded_by=current_user.username
        )
        db.session.add(cash_flow)
        db.session.commit()
        
        return jsonify({
            "message": "Cash register closed",
            "variance": cash_flow.variance,
            "expected": register.current_balance,
            "actual": actual_balance
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ============================================================================
# OFFLINE SUPPORT
# ============================================================================
@pos_bp.route("/orders/sync", methods=["POST"])
@login_required
def sync_offline_orders():
    """Synchronize offline orders when connection is restored"""
    try:
        data = request.get_json()
        orders = data.get("orders", [])
        
        synced_count = 0
        for order_data in orders:
            # Process each offline order
            payment = PaymentTransaction.query.filter_by(reference_id=order_data.get("reference_id")).first()
            if payment:
                payment.synchronization_status = "synced"
                payment.is_offline = False
                synced_count += 1
        
        db.session.commit()
        return jsonify({"message": f"{synced_count} orders synced"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
