#!/usr/bin/env python
"""
Beta Launch User Setup Script
Creates super admin, restaurant admin for Sizzlecraft, and test users
"""

from app import create_app
from extensions import db
from models import User, Restaurant, StoreSettings
from werkzeug.security import generate_password_hash

app = create_app()

def create_users():
    with app.app_context():
        db.create_all()
        
        print("\n" + "="*70)
        print("🚀 SERVEOPOS BETA LAUNCH - USER SETUP")
        print("="*70 + "\n")
        
        # =========================================================================
        # 1. CREATE SUPER ADMIN (Platform Owner)
        # =========================================================================
        print("📌 Step 1: Creating Platform Super Admin...")
        if not User.query.filter_by(username='superadmin').first():
            superadmin = User(
                username="superadmin",
                password_hash=generate_password_hash("superadmin@123"),
                role="super_admin",
                is_super_admin=True,
                restaurant_id=None,
                locale="en",
                currency="USD"
            )
            db.session.add(superadmin)
            db.session.commit()
            print("✅ Super admin created: superadmin / superadmin@123\n")
        else:
            print("⚠️  Super admin already exists\n")
        
        # =========================================================================
        # 2. CREATE SIZZLECRAFT RESTAURANT ADMIN
        # =========================================================================
        print("📌 Step 2: Creating Sizzlecraft Restaurant Admin...")
        
        # Check if Sizzlecraft exists
        sizzlecraft_admin = User.query.filter_by(username='sizzlecraft_admin').first()
        if not sizzlecraft_admin:
            sizzlecraft_admin = User(
                username="sizzlecraft_admin",
                password_hash=generate_password_hash("sizzlecraft@admin123"),
                role="restaurant_admin",
                is_super_admin=False,
                locale="en",
                currency="INR"
            )
            db.session.add(sizzlecraft_admin)
            db.session.flush()
            print(f"✅ Restaurant admin created: sizzlecraft_admin / sizzlecraft@admin123")
        else:
            print(f"⚠️  Restaurant admin already exists")
        
        # Create Sizzlecraft restaurant if it doesn't exist
        sizzlecraft = Restaurant.query.filter_by(email='sizzlecraft@example.com').first()
        if not sizzlecraft:
            sizzlecraft = Restaurant(
                name="Sizzlecraft Restaurant",
                email="sizzlecraft@example.com",
                phone="+91-11-XXXX-XXXX",
                address="123 Restaurant Lane, Delhi NCR",
                city="Delhi",
                country="India",
                postal_code="110001",
                owner_id=sizzlecraft_admin.id,
                active=True
            )
            db.session.add(sizzlecraft)
            db.session.flush()
            
            # Create store settings for Sizzlecraft
            store_settings = StoreSettings(
                restaurant_id=sizzlecraft.id,
                timezone="Asia/Kolkata",
                locale="en",
                currency="INR",
                tax_region="IN",
                address_format="standard",
                business_registration="GSTIN1234567890",
                vat_number="VAT123456",
                payment_terms=0,
                invoice_prefix="SIZ"
            )
            db.session.add(store_settings)
            db.session.commit()
            print(f"✅ Sizzlecraft restaurant created: {sizzlecraft.name}")
            
            # Update admin's restaurant_id
            sizzlecraft_admin.restaurant_id = sizzlecraft.id
            db.session.commit()
        else:
            sizzlecraft = sizzlecraft
            if not sizzlecraft_admin.restaurant_id:
                sizzlecraft_admin.restaurant_id = sizzlecraft.id
                db.session.commit()
            print(f"⚠️  Sizzlecraft restaurant already exists")
        
        print()
        
        # =========================================================================
        # 3. CREATE SIZZLECRAFT MANAGER
        # =========================================================================
        print("📌 Step 3: Creating Sizzlecraft Manager...")
        if not User.query.filter_by(username='sizzlecraft_manager').first():
            manager = User(
                username="sizzlecraft_manager",
                password_hash=generate_password_hash("manager@123"),
                role="manager",
                is_super_admin=False,
                restaurant_id=sizzlecraft.id,
                locale="en",
                currency="INR"
            )
            db.session.add(manager)
            db.session.commit()
            print(f"✅ Manager created: sizzlecraft_manager / manager@123\n")
        else:
            print(f"⚠️  Manager already exists\n")
        
        # =========================================================================
        # 4. CREATE SIZZLECRAFT CHEFS (2)
        # =========================================================================
        print("📌 Step 4: Creating Sizzlecraft Chefs (2)...")
        chef_data = [
            ('sizzlecraft_chef_1', 'Chef One'),
            ('sizzlecraft_chef_2', 'Chef Two'),
        ]
        
        for username, display_name in chef_data:
            if not User.query.filter_by(username=username).first():
                chef = User(
                    username=username,
                    password_hash=generate_password_hash("chef@123"),
                    role="kitchen",
                    is_super_admin=False,
                    restaurant_id=sizzlecraft.id,
                    locale="en",
                    currency="INR"
                )
                db.session.add(chef)
                db.session.commit()
                print(f"✅ {display_name} created: {username} / chef@123")
        print()
        
        # =========================================================================
        # 5. CREATE SIZZLECRAFT WAITERS (5)
        # =========================================================================
        print("📌 Step 5: Creating Sizzlecraft Waiters (5)...")
        waiter_data = [
            ('sizzlecraft_waiter_1', 'Waiter One'),
            ('sizzlecraft_waiter_2', 'Waiter Two'),
            ('sizzlecraft_waiter_3', 'Waiter Three'),
            ('sizzlecraft_waiter_4', 'Waiter Four'),
            ('sizzlecraft_waiter_5', 'Waiter Five'),
        ]
        
        for username, display_name in waiter_data:
            if not User.query.filter_by(username=username).first():
                waiter = User(
                    username=username,
                    password_hash=generate_password_hash("waiter@123"),
                    role="waiter",
                    is_super_admin=False,
                    restaurant_id=sizzlecraft.id,
                    locale="en",
                    currency="INR"
                )
                db.session.add(waiter)
                db.session.commit()
                print(f"✅ {display_name} created: {username} / waiter@123")
        print()
        
        # =========================================================================
        # SUMMARY
        # =========================================================================
        print("="*70)
        print("📊 SETUP COMPLETE - USER CREDENTIALS SUMMARY")
        print("="*70 + "\n")
        
        print("🔐 PLATFORM SUPER ADMIN:")
        print("  Username: superadmin")
        print("  Password: superadmin@123")
        print("  Role: Super Admin (manages entire platform)\n")
        
        print("🏢 SIZZLECRAFT RESTAURANT:")
        print("  Restaurant Admin:")
        print("    Username: sizzlecraft_admin")
        print("    Password: sizzlecraft@admin123")
        print("    Role: Restaurant Admin\n")
        
        print("  Manager:")
        print("    Username: sizzlecraft_manager")
        print("    Password: manager@123")
        print("    Role: Manager\n")
        
        print("  Chefs (2):")
        print("    Username: sizzlecraft_chef_1 / sizzlecraft_chef_2")
        print("    Password: chef@123")
        print("    Role: Kitchen Staff\n")
        
        print("  Waiters (5):")
        print("    Username: sizzlecraft_waiter_1 to sizzlecraft_waiter_5")
        print("    Password: waiter@123")
        print("    Role: Waiter\n")
        
        print("="*70)
        print("✨ All users created successfully!")
        print("="*70 + "\n")

if __name__ == '__main__':
    create_users()
