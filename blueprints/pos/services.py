# POS helper functions and business logic
from extensions import db
from models import (
    Order, OrderItem, Discount, BillSplit, PaymentTransaction,
    Receipt, LoyaltyPoints, eWalletTransaction, Product
)
from datetime import datetime
import json


def calculate_order_total(items_list):
    """Calculate total from items list"""
    return sum(
        item.get("price", 0) * item.get("quantity", 0)
        for item in items_list
    )


def calculate_order_total_from_items(order_items):
    """Calculate total from OrderItem objects"""
    return sum(
        item.menu_item.price * item.quantity
        for item in order_items
    )


def apply_discount(order, discount_data):
    """
    Apply discount to order or specific items
    discount_data: {
        "type": "percentage" | "fixed_amount",
        "value": float,
        "applies_to": "product" | "order",
        "product_id": int (optional)
    }
    """
    try:
        discount_type = discount_data.get("type")  # percentage or fixed_amount
        value = discount_data.get("value")
        applies_to = discount_data.get("applies_to", "order")
        product_id = discount_data.get("product_id")
        
        discount_amount = 0
        
        if applies_to == "product" and product_id:
            # Apply to specific product
            for item in order.items:
                if item.menu_item_id == product_id:
                    if discount_type == "percentage":
                        discount_amount += (item.menu_item.price * item.quantity * value / 100)
                    else:
                        discount_amount += value * item.quantity
        else:
            # Apply to entire order
            total = calculate_order_total_from_items(order.items)
            if discount_type == "percentage":
                discount_amount = total * value / 100
            else:
                discount_amount = value
        
        # Store discount info in order metadata if available
        # For now, just return the discount amount
        return {
            "discount_type": discount_type,
            "discount_value": value,
            "discount_amount": discount_amount
        }
    except Exception as e:
        raise Exception(f"Error applying discount: {str(e)}")


def process_payment(order, payment_data, current_user):
    """
    Process payment for an order
    payment_data: {
        "payment_method_id": int,
        "amount": float,
        "is_offline": bool,
        "tip_amount": float (optional),
        "tip_type": "amount" | "percentage" (optional)
    }
    """
    try:
        payment_method_id = payment_data.get("payment_method_id")
        amount = payment_data.get("amount")
        is_offline = payment_data.get("is_offline", False)
        tip_amount = payment_data.get("tip_amount", 0)
        tip_type = payment_data.get("tip_type", "amount")
        
        if not payment_method_id or not amount:
            return {"success": False, "error": "Missing payment method or amount"}
        
        # Create payment transaction
        payment = PaymentTransaction(
            order_id=order.id,
            payment_method_id=payment_method_id,
            amount=amount,
            currency="USD",  # Should come from restaurant settings
            status="completed" if not is_offline else "pending",
            is_offline=is_offline,
            synchronization_status="pending_sync" if is_offline else "synced",
            tip_amount=tip_amount,
            tip_type=tip_type
        )
        db.session.add(payment)
        
        # Generate receipt
        receipt = Receipt(
            order_id=order.id,
            receipt_number=f"REC-{order.id}-{datetime.utcnow().timestamp()}",
            content=generate_receipt_content(order, payment),
            header_text="Thank you for your purchase!",
            footer_text="Visit us again!"
        )
        db.session.add(receipt)
        
        return {
            "success": True,
            "payment_id": payment.id,
            "receipt_id": receipt.id,
            "amount": amount,
            "tip": tip_amount,
            "total": amount + tip_amount,
            "status": "completed" if not is_offline else "pending_sync"
        }
    except Exception as e:
        raise Exception(f"Error processing payment: {str(e)}")


def generate_receipt_content(order, payment):
    """Generate receipt content"""
    try:
        lines = []
        lines.append("=" * 40)
        lines.append("RECEIPT")
        lines.append("=" * 40)
        lines.append(f"Order #: {order.id}")
        lines.append(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("-" * 40)
        
        total = 0
        from models import Product
        for item in order.items:
            menu = item.menu_item
            if not menu:
                menu = Product.query.get(item.menu_item_id)
            name = getattr(menu, 'name', 'Item')
            unit_price = getattr(menu, 'price', getattr(menu, 'base_price', 0))
            subtotal = unit_price * item.quantity
            total += subtotal
            lines.append(f"{name}")
            lines.append(f"  {item.quantity} x ${unit_price:.2f} = ${subtotal:.2f}")
        
        lines.append("-" * 40)
        lines.append(f"Subtotal: ${total:.2f}")
        lines.append(f"Payment Method: {payment.payment_method.name if hasattr(payment, 'payment_method') else 'N/A'}")
        if payment.tip_amount > 0:
            lines.append(f"Tip: ${payment.tip_amount:.2f}")
            lines.append(f"Total: ${total + payment.tip_amount:.2f}")
        else:
            lines.append(f"Total: ${total:.2f}")
        lines.append("=" * 40)
        
        return "\n".join(lines)
    except Exception as e:
        return f"Error generating receipt: {str(e)}"


def handle_bill_split(order, split_data):
    """
    Handle bill splitting for multiple parties
    split_data: {
        "splits": [
            {"payment_method_id": int, "amount": float},
            {"payment_method_id": int, "amount": float}
        ]
    }
    """
    try:
        splits = split_data.get("splits", [])
        
        bill_splits = []
        for idx, split in enumerate(splits, 1):
            bill_split = BillSplit(
                order_id=order.id,
                split_index=idx,
                amount=split.get("amount"),
                payment_method_id=split.get("payment_method_id"),
                status="pending"
            )
            db.session.add(bill_split)
            bill_splits.append({
                "split_number": idx,
                "amount": split.get("amount"),
                "status": "pending"
            })
        
        return bill_splits
    except Exception as e:
        raise Exception(f"Error handling bill split: {str(e)}")


def add_loyalty_points(customer, order, points_earned):
    """
    Add loyalty points to customer
    """
    try:
        if not customer.loyalty_card:
            return {"success": False, "error": "Customer does not have a loyalty card"}
        
        loyalty_card = customer.loyalty_card
        loyalty_card.points_balance += points_earned
        loyalty_card.points_earned_total += points_earned
        
        points_record = LoyaltyPoints(
            loyalty_card_id=loyalty_card.id,
            order_id=order.id,
            points=points_earned,
            earn_method="purchase",
            description=f"Points earned from order #{order.id}"
        )
        db.session.add(points_record)
        
        return {
            "success": True,
            "points_earned": points_earned,
            "points_balance": loyalty_card.points_balance
        }
    except Exception as e:
        raise Exception(f"Error adding loyalty points: {str(e)}")


def topup_ewallet(ewallet, amount, payment_method_id):
    """
    Top-up customer e-wallet
    """
    try:
        ewallet.balance += amount
        
        transaction = eWalletTransaction(
            ewallet_id=ewallet.id,
            amount=amount,
            transaction_type="topup",
            reference_id=f"TOPUP-{datetime.utcnow().timestamp()}"
        )
        db.session.add(transaction)
        
        return {
            "success": True,
            "amount_added": amount,
            "new_balance": ewallet.balance
        }
    except Exception as e:
        raise Exception(f"Error topping up e-wallet: {str(e)}")


def calculate_price_with_pricelist(product, pricelist):
    """
    Get product price from specific pricelist
    """
    try:
        from models import PriceListItem
        price_list_item = PriceListItem.query.filter_by(
            pricelist_id=pricelist.id,
            product_id=product.id
        ).first()
        
        if price_list_item:
            return price_list_item.price
        else:
            return product.base_price
    except Exception as e:
        raise Exception(f"Error calculating price from pricelist: {str(e)}")


def validate_credit_limit(customer, order_total):
    """
    Check if customer has exceeded credit limit
    """
    try:
        if customer.credit_limit <= 0:
            return {"allowed": True, "reason": "No credit limit"}
        
        new_balance = customer.outstanding_balance + order_total
        
        if new_balance > customer.credit_limit:
            return {
                "allowed": False,
                "reason": "Credit limit exceeded",
                "credit_limit": customer.credit_limit,
                "current_balance": customer.outstanding_balance,
                "would_be_balance": new_balance
            }
        
        return {"allowed": True, "reason": "Credit limit OK"}
    except Exception as e:
        raise Exception(f"Error validating credit limit: {str(e)}")
