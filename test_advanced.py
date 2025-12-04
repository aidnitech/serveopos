#!/usr/bin/env python
"""
Advanced unit tests for ServeoPOS:
- Role Permission behavior and enforcement
- CSV import/export functionality
- Permission denial logging
"""

from app import create_app
from extensions import db
from models import User, MenuItem, InventoryItem, RolePermission, AuditLog
from werkzeug.security import generate_password_hash
import json
import io
import csv

app = create_app()
app.config["WTF_CSRF_ENABLED"] = False
client = app.test_client()

def setup_test_data():
    """Initialize test database with users, items, and permissions"""
    with app.app_context():
        # Instead of dropping the schema, clear data and reseed expected rows
        try:
            for table in reversed(db.metadata.sorted_tables):
                try:
                    db.session.execute(table.delete())
                except Exception:
                    pass
            db.session.commit()
        except Exception:
            db.session.rollback()

        # Create users with different roles
        admin = User(username="admin", password_hash=generate_password_hash("admin"), role="admin")
        manager = User(username="manager", password_hash=generate_password_hash("manager"), role="manager")
        waiter = User(username="waiter", password_hash=generate_password_hash("waiter"), role="waiter")
        kitchen = User(username="kitchen", password_hash=generate_password_hash("kitchen"), role="kitchen")
        db.session.add_all([admin, manager, waiter, kitchen])

        # Create menu items
        db.session.add(MenuItem(name="Sizzler", description="Hot platter", price=45.0))
        db.session.add(MenuItem(name="Pasta", description="Creamy pasta", price=35.0))

        # Create inventory items
        db.session.add(InventoryItem(name="Chicken", quantity=50, unit="kg"))
        db.session.add(InventoryItem(name="Oil", quantity=20, unit="liters"))

        db.session.commit()

def login_as(username, password):
    """Helper to login as a user"""
    return client.post("/auth/login", data={"username": username, "password": password}, follow_redirects=False)

def logout():
    """Helper to logout"""
    return client.get("/auth/logout", follow_redirects=False)

# ============================================================
# ROLE PERMISSION TESTS
# ============================================================

def test_role_permission_defaults():
    """Test that RolePermission falls back to sensible defaults when rows are missing"""
    print("\n🔍 Testing Role Permission Defaults...")
    
    login_as("waiter", "waiter")
    
    # Waiter should be able to create orders (manage_orders permission)
    order_data = {"items": [{"menu_item_id": 1, "quantity": 1}]}
    response = client.post("/pos/orders", 
        data=json.dumps(order_data),
        content_type="application/json")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    print("  ✓ Waiter can create orders (fallback default)")
    
    # Waiter should NOT be able to manage menu
    response = client.get("/admin/api/menu")
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    print("  ✓ Waiter cannot manage menu (fallback default blocks)")
    
    logout()

def test_role_permission_explicit():
    """Test that explicit RolePermission rows override defaults"""
    print("\n🔍 Testing Explicit Role Permissions...")
    
    with app.app_context():
        # Create explicit RolePermission for waiter to manage_menu
        db.session.add(RolePermission(role="waiter", permission="manage_menu", allowed=True))
        db.session.commit()
    
    login_as("waiter", "waiter")
    
    # Now waiter CAN manage menu
    response = client.get("/admin/api/menu")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    items = response.get_json()
    assert isinstance(items, list), "Menu should return a list"
    print("  ✓ Waiter can manage menu after explicit permission grant")
    
    logout()

def test_role_permission_denial_logging():
    """Test that denied access is logged in AuditLog"""
    print("\n🔍 Testing Permission Denial Logging...")
    
    login_as("waiter", "waiter")
    
    # Try to access admin panel (forbidden)
    response = client.get("/admin/")
    assert response.status_code == 403
    
    logout()
    
    # Check that a forbidden action was logged
    with app.app_context():
        logs = AuditLog.query.filter_by(action='forbidden').all()
        assert len(logs) > 0, "Forbidden action should be logged"
        assert any('waiter' in str(l.details) for l in logs), "Log should contain role info"
        print("  ✓ Permission denials are logged in AuditLog")

def test_admin_default_permissions():
    """Test that admin role has all permissions by default"""
    print("\n🔍 Testing Admin Default Permissions...")
    
    login_as("admin", "admin")
    
    # Admin should access menu
    resp = client.get("/admin/api/menu")
    assert resp.status_code == 200
    print("  ✓ Admin can manage menu")
    
    # Admin should access users
    resp = client.get("/admin/api/users")
    assert resp.status_code == 200
    print("  ✓ Admin can manage users")
    
    # Admin should access inventory
    resp = client.get("/admin/api/inventory")
    assert resp.status_code == 200
    print("  ✓ Admin can manage inventory")
    
    # Admin should access analytics
    resp = client.get("/analytics/sales")
    assert resp.status_code == 200
    print("  ✓ Admin can view analytics")
    
    logout()

# ============================================================
# CSV IMPORT/EXPORT TESTS
# ============================================================

def test_menu_csv_export():
    """Test menu CSV export"""
    print("\n🔍 Testing Menu CSV Export...")
    
    login_as("admin", "admin")
    
    response = client.get("/admin/api/menu/export")
    assert response.status_code == 200
    assert b"name" in response.data
    assert b"Sizzler" in response.data
    print("  ✓ Menu CSV export contains items")
    
    logout()

def test_menu_csv_import():
    """Test menu CSV import with row-level results"""
    print("\n🔍 Testing Menu CSV Import with Results...")
    
    login_as("admin", "admin")
    
    # Create CSV file in memory (using StringIO then encode)
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(['name', 'price', 'description'])
    writer.writerow(['New Dish', '50.00', 'Test dish'])
    writer.writerow(['Invalid', 'bad_price', 'Should fail'])  # Invalid price
    writer.writerow(['Another', '30', 'Good'])
    csv_content = csv_buffer.getvalue().encode('utf-8')
    csv_data = io.BytesIO(csv_content)
    
    data = {'file': (csv_data, 'test.csv')}
    response = client.post("/admin/api/menu/import",
        data=data,
        content_type='multipart/form-data')
    
    assert response.status_code == 201
    json_resp = response.get_json()
    assert 'results' in json_resp
    results = json_resp['results']
    
    # Verify row-level results
    created_count = len([r for r in results if r['status'] == 'created'])
    error_count = len([r for r in results if r['status'] == 'error'])
    assert created_count > 0, "Should have created at least 1 item"
    assert error_count > 0, "Should have 1 error for bad price"
    assert created_count == 2, f"Expected 2 created, got {created_count}"
    print(f"  ✓ Menu CSV import: {created_count} created, {error_count} errors")
    
    logout()

def test_inventory_csv_export():
    """Test inventory CSV export"""
    print("\n🔍 Testing Inventory CSV Export...")
    
    login_as("admin", "admin")
    
    response = client.get("/admin/api/inventory/export")
    assert response.status_code == 200
    assert b"name" in response.data
    assert b"Chicken" in response.data
    print("  ✓ Inventory CSV export contains items")
    
    logout()

def test_inventory_csv_import():
    """Test inventory CSV import"""
    print("\n🔍 Testing Inventory CSV Import...")
    
    login_as("admin", "admin")
    
    # Create CSV file using StringIO then encode
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(['name', 'quantity', 'unit'])
    writer.writerow(['Flour', '100', 'kg'])
    writer.writerow(['Sugar', '50', 'kg'])
    csv_content = csv_buffer.getvalue().encode('utf-8')
    csv_data = io.BytesIO(csv_content)
    
    data = {'file': (csv_data, 'inventory.csv')}
    response = client.post("/admin/api/inventory/import",
        data=data,
        content_type='multipart/form-data')
    
    assert response.status_code == 201
    json_resp = response.get_json()
    assert len(json_resp['created']) == 2, "Should create 2 inventory items"
    print(f"  ✓ Inventory CSV import created {len(json_resp['created'])} items")
    
    logout()

def test_menu_csv_template_download():
    """Test menu CSV template download"""
    print("\n🔍 Testing Menu CSV Template...")
    
    login_as("admin", "admin")
    
    response = client.get("/admin/api/menu/template")
    assert response.status_code == 200
    assert b"name" in response.data
    assert b"price" in response.data
    assert b"description" in response.data
    print("  ✓ Menu CSV template headers present")
    
    logout()

def test_inventory_csv_template_download():
    """Test inventory CSV template download"""
    print("\n🔍 Testing Inventory CSV Template...")
    
    login_as("admin", "admin")
    
    response = client.get("/admin/api/inventory/template")
    assert response.status_code == 200
    assert b"name" in response.data
    assert b"quantity" in response.data
    assert b"unit" in response.data
    print("  ✓ Inventory CSV template headers present")
    
    logout()

# ============================================================
# PERMISSION ENFORCEMENT ACROSS ENDPOINTS
# ============================================================

def test_kitchen_cannot_manage_menu():
    """Test that kitchen role cannot manage menu items"""
    print("\n🔍 Testing Kitchen Cannot Manage Menu...")
    
    login_as("kitchen", "kitchen")
    
    # Kitchen should not be able to GET menu for management
    response = client.get("/admin/api/menu")
    assert response.status_code == 403
    print("  ✓ Kitchen role denied menu management access")
    
    logout()

def test_kitchen_can_view_pending_orders():
    """Test that kitchen role can view pending orders"""
    print("\n🔍 Testing Kitchen Can View Pending Orders...")
    
    login_as("kitchen", "kitchen")
    
    response = client.get("/kds/orders")
    assert response.status_code == 200
    orders = response.get_json()
    assert isinstance(orders, list)
    print("  ✓ Kitchen can view pending orders")
    
    logout()

def test_manager_can_manage_menu():
    """Test that manager role can manage menu"""
    print("\n🔍 Testing Manager Can Manage Menu...")
    
    login_as("manager", "manager")
    
    response = client.get("/admin/api/menu")
    assert response.status_code == 200
    items = response.get_json()
    assert isinstance(items, list)
    print("  ✓ Manager can manage menu")
    
    logout()

def test_waiter_can_create_orders():
    """Test that waiter can create orders"""
    print("\n🔍 Testing Waiter Can Create Orders...")
    
    login_as("waiter", "waiter")
    
    order_data = {"items": [{"menu_item_id": 1, "quantity": 2}]}
    response = client.post("/pos/orders",
        data=json.dumps(order_data),
        content_type="application/json")
    assert response.status_code == 201
    order = response.get_json()
    assert "id" in order
    print(f"  ✓ Waiter created order #{order['id']}")
    
    logout()

def test_waiter_cannot_manage_users():
    """Test that waiter cannot manage users"""
    print("\n🔍 Testing Waiter Cannot Manage Users...")
    
    login_as("waiter", "waiter")
    
    response = client.get("/admin/api/users")
    assert response.status_code == 403
    print("  ✓ Waiter denied user management access")
    
    logout()

# ============================================================
# ANALYTICS PERMISSION TEST
# ============================================================

def test_analytics_permission():
    """Test that view_analytics permission is enforced"""
    print("\n🔍 Testing Analytics Permission...")
    
    login_as("admin", "admin")
    
    response = client.get("/analytics/sales")
    assert response.status_code == 200
    data = response.get_json()
    assert "total_orders" in data
    print("  ✓ Admin can view analytics")
    
    logout()
    
    login_as("kitchen", "kitchen")
    
    # With fallback defaults, kitchen cannot access analytics
    response = client.get("/analytics/sales")
    assert response.status_code == 403
    print("  ✓ Kitchen denied analytics access (by default)")
    
    logout()

# ============================================================
# RUN ALL TESTS
# ============================================================

def run_all_tests():
    """Run all advanced test suites"""
    print("=" * 60)
    print("🧪 SERVEOPOS - ADVANCED TEST SUITE")
    print("=" * 60)
    
    setup_test_data()
    
    try:
        # Role Permission Tests
        test_role_permission_defaults()
        test_role_permission_explicit()
        test_role_permission_denial_logging()
        test_admin_default_permissions()
        
        # CSV Import/Export Tests
        test_menu_csv_export()
        test_menu_csv_import()
        test_inventory_csv_export()
        test_inventory_csv_import()
        test_menu_csv_template_download()
        test_inventory_csv_template_download()
        
        # Permission Enforcement Tests
        test_kitchen_cannot_manage_menu()
        test_kitchen_can_view_pending_orders()
        test_manager_can_manage_menu()
        test_waiter_can_create_orders()
        test_waiter_cannot_manage_users()
        
        # Analytics Permission Tests
        test_analytics_permission()
        
        print("\n" + "=" * 60)
        print("✅ ALL ADVANCED TESTS PASSED!")
        print("=" * 60)
        print("\n📋 Test Summary:")
        print("  • Role Permission Defaults: ✓")
        print("  • Explicit Role Permissions: ✓")
        print("  • Permission Denial Logging: ✓")
        print("  • Admin Default Permissions: ✓")
        print("  • Menu CSV Export/Import: ✓")
        print("  • Inventory CSV Export/Import: ✓")
        print("  • CSV Templates: ✓")
        print("  • Permission Enforcement: ✓")
        print("  • Analytics Permission: ✓")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
