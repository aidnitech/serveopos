# Example inventory logic
def calculate_stock_value(items):
    return sum(item["qty"] * item["price"] for item in items)
