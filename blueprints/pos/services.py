# POS helper functions
def calculate_order_total(order_items):
    return sum(item.menu_item.price * item.quantity for item in order_items)
