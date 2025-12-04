#!/usr/bin/env python
"""
Comprehensive endpoint testing for ServeoPOS System
Tests all major functions for beta launch
"""

from app import create_app
from extensions import db
from models import User, MenuItem, Order, OrderItem
from werkzeug.security import generate_password_hash
import json

app = create_app()
app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing
client = app.test_client()

def setup_test_data():
    """Initialize test database"""
    with app.app_context():
        # Instead of dropping the schema, clear rows and reseed
        try:
            for table in reversed(db.metadata.sorted_tables):
                try:
                    db.session.execute(table.delete())
                except Exception:
                    pass
            db.session.commit()
        except Exception:
            db.session.rollback()
        
        # Create test users
        admin = User(username="admin", password_hash=generate_password_hash("admin"), role="admin")
        waiter = User(username="waiter", password_hash=generate_password_hash("waiter"), role="waiter")
        kitchen = User(username="kitchen", password_hash=generate_password_hash("kitchen"), role="kitchen")
        manager = User(username="manager", password_hash=generate_password_hash("manager"), role="manager")
        db.session.add_all([admin, waiter, kitchen, manager])
        
        # Create menu items
        db.session.add(MenuItem(name="Chicken Sizzler", description="Hot sizzling platter", price=45.0))
        db.session.add(MenuItem(name="Paneer Tikka Sizzler", description="Vegetarian delight", price=40.0))
        db.session.add(MenuItem(name="Pasta Alfredo", description="Continental creamy pasta", price=35.0))
        db.session.commit()

def test_home():
    """Test root route"""
    print("\n🔍 Testing home route...")
    response = client.get("/")
    assert response.status_code == 200
    assert b"navbar" in response.data or b"Navbar" in response.data or b"navbar-brand" in response.data
    print("  ✓ Home route works with navbar")

def test_login():
    """Test login functionality"""
    print("\n🔍 Testing authentication...")
    
    # Test GET login page
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Login" in response.data
    print("  ✓ Login page loads")
    
    # Test invalid credentials
    response = client.post("/auth/login", data={
        "username": "invalid",
        "password": "wrong"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data
    print("  ✓ Invalid credentials rejected")
    
    # Test valid login as waiter
    response = client.post("/auth/login", data={
        "username": "waiter",
        "password": "waiter"
    }, follow_redirects=True)
    assert response.status_code == 200
    print("  ✓ Waiter login successful")
    
    # Test logout
    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    print("  ✓ Logout successful")

def test_protected_routes():
    """Test protected route access"""
    print("\n🔍 Testing protected routes...")
    
    # Test menu without auth (should redirect)
    response = client.get("/menu/", follow_redirects=True)
    assert b"Login" in response.data
    print("  ✓ Menu redirects to login when not authenticated")
    
    # Test with admin login
    client.post("/auth/login", data={"username": "admin", "password": "admin"})
    
    response = client.get("/admin/")
    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data
    print("  ✓ Admin dashboard accessible to admin")
    
    client.get("/auth/logout")

def test_menu_route():
    """Test menu display"""
    print("\n🔍 Testing menu route...")
    
    client.post("/auth/login", data={"username": "waiter", "password": "waiter"})
    response = client.get("/menu/")
    assert response.status_code == 200
    assert b"Chicken Sizzler" in response.data
    assert b"45" in response.data
    print("  ✓ Menu displays items correctly")
    client.get("/auth/logout")

def test_pos_routes():
    """Test POS endpoints"""
    print("\n🔍 Testing POS routes...")
    
    client.post("/auth/login", data={"username": "waiter", "password": "waiter"})
    
    # Test POS page
    response = client.get("/pos/")
    assert response.status_code == 200
    assert b"Point of Sale" in response.data
    print("  ✓ POS page loads")
    
    # Test create order
    order_data = {
        "items": [
            {"menu_item_id": 1, "quantity": 2},
            {"menu_item_id": 2, "quantity": 1}
        ]
    }
    response = client.post("/pos/orders", 
        data=json.dumps(order_data),
        content_type="application/json")
    assert response.status_code == 201
    order = json.loads(response.data)
    order_id = order["id"]
    print(f"  ✓ Order created: #{order_id}")
    
    # Test get order
    response = client.get(f"/pos/orders/{order_id}")
    assert response.status_code == 200
    order = json.loads(response.data)
    assert order["id"] == order_id
    assert len(order["items"]) == 2
    assert order["total"] == 130.0  # (45*2) + 40*1
    print(f"  ✓ Order retrieved: total = {order['total']} RON")
    
    # Test update order status
    response = client.put(f"/pos/orders/{order_id}/status",
        data=json.dumps({"status": "cooking"}),
        content_type="application/json")
    assert response.status_code == 200
    print("  ✓ Order status updated to cooking")
    
    client.get("/auth/logout")

def test_kds_routes():
    """Test Kitchen Display System"""
    print("\n🔍 Testing KDS routes...")
    
    # Create an order first
    with app.app_context():
        order = Order()
        db.session.add(order)
        db.session.flush()
        item = MenuItem.query.first()
        order_item = OrderItem(order_id=order.id, menu_item_id=item.id, quantity=1)
        db.session.add(order_item)
        db.session.commit()
    
    client.post("/auth/login", data={"username": "kitchen", "password": "kitchen"})
    
    response = client.get("/kds/orders")
    assert response.status_code == 200
    orders = json.loads(response.data)
    assert len(orders) > 0
    assert "items" in orders[0]
    assert "name" in orders[0]["items"][0]
    print(f"  ✓ KDS displays {len(orders)} pending order(s) with item details")
    
    client.get("/auth/logout")

def test_analytics():
    """Test analytics endpoints"""
    print("\n🔍 Testing analytics...")
    
    client.post("/auth/login", data={"username": "admin", "password": "admin"})
    
    response = client.get("/analytics/sales")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "total_orders" in data
    assert "total_items" in data
    assert "total_revenue" in data
    print(f"  ✓ Analytics: {data['total_orders']} orders, {data['total_items']} items, {data['total_revenue']} RON revenue")
    
    client.get("/auth/logout")

def test_api():
    """Test API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    response = client.get("/api/menu")
    assert response.status_code == 200
    items = json.loads(response.data)
    assert len(items) == 3
    assert items[0]["name"] == "Chicken Sizzler"
    print(f"  ✓ API returns {len(items)} menu items")

def test_role_based_access():
    """Test role-based access control"""
    print("\n🔍 Testing role-based access control...")
    
    # Test waiter cannot access admin
    client.post("/auth/login", data={"username": "waiter", "password": "waiter"})
    response = client.get("/admin/")
    assert response.status_code == 403
    print("  ✓ Waiter cannot access admin dashboard")
    client.get("/auth/logout")
    
    # Test manager can access admin
    client.post("/auth/login", data={"username": "manager", "password": "manager"})
    response = client.get("/admin/")
    assert response.status_code == 200
    print("  ✓ Manager can access admin dashboard")
    client.get("/auth/logout")

def run_all_tests():
    """Run all test suites"""
    print("=" * 60)
    print("🚀 SERVEOPOS SYSTEM - BETA LAUNCH TEST SUITE")
    print("=" * 60)
    
    setup_test_data()
    
    try:
        test_home()
        test_login()
        test_protected_routes()
        test_menu_route()
        test_pos_routes()
        test_kds_routes()
        test_analytics()
        test_api()
        test_role_based_access()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED! SYSTEM READY FOR BETA LAUNCH")
        print("=" * 60)
        print("\n📋 Test Results Summary:")
        print("  • Authentication: ✓")
        print("  • Menu Management: ✓")
        print("  • Order Creation: ✓")
        print("  • Order Management: ✓")
        print("  • KDS Display: ✓")
        print("  • Analytics: ✓")
        print("  • API: ✓")
        print("  • Role-Based Access Control: ✓")
        print("  • Error Handling: ✓")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
