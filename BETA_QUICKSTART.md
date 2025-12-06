# 🚀 ServeoPOS Beta - Quick Start Guide

Welcome to the **ServeoPOS Beta Launch!** This guide will help you get started with the application quickly.

---

## 🎯 Quick Login Credentials

### For Full System Access
```
Username: superadmin
Password: superadmin@123
Role: Platform Super Admin
```

### For Restaurant Management (Sizzlecraft)
```
Username: sizzlecraft_admin
Password: sizzlecraft@admin123
Role: Restaurant Admin
```

### For Daily Operations
```
Manager:      sizzlecraft_manager / manager@123
Chef 1:       sizzlecraft_chef_1 / chef@123
Chef 2:       sizzlecraft_chef_2 / chef@123
Waiter 1:     sizzlecraft_waiter_1 / waiter@123
Waiter 2-5:   sizzlecraft_waiter_2 to 5 / waiter@123
```

---

## 🚀 Getting Started in 3 Steps

### Step 1: Start the Application
```bash
cd /workspaces/serveopos
python app.py
```

### Step 2: Open in Browser
Navigate to: **http://localhost:5000**

### Step 3: Login with Your Credentials
- Enter username and password from above
- You'll be redirected based on your role

---

## 📱 What You Can Do

### 👨‍💼 As Super Admin (superadmin)
- Access platform-wide settings
- Manage restaurants
- View all system activities
- Monitor audit logs

### 🏢 As Restaurant Admin (sizzlecraft_admin)
- Manage restaurant configuration
- Set up menu and inventory
- Manage staff and permissions
- View comprehensive reports
- Handle financial records

### 📊 As Manager (sizzlecraft_manager)
- View sales dashboard
- Manage menu items
- Process POS transactions
- View analytics and reports
- Manage staff shifts

### 🍳 As Kitchen Staff (sizzlecraft_chef_*)
- View pending orders
- Track order status
- Update order progress
- Communicate with waiters (via order notes)

### 🍽️ As Waiter (sizzlecraft_waiter_*)
- Take customer orders
- Select items from menu
- Apply discounts
- Process payments
- Split bills
- Print receipts
- Track order status in kitchen

---

## 🎨 User Interface Overview

### Header
- **Left:** ServeoPOS logo and "by Aidni Global LLP" branding
- **Right:** Current user info and role badge

### Navigation Menu (Top)
- Different options based on your role
- Dropdown menus for easy access
- Responsive design for mobile devices

### Main Content Area
- Role-specific dashboards and features
- Flash messages for important notifications
- Professional green and gold color scheme

### Footer
- Company information (Aidni Global LLP & Gaatha Ventures SRL)
- Contact email: office@aidniglobal.in
- Copyright and beta notice

---

## ✨ Key Features Ready for Testing

### ✅ Authentication
- Secure login system
- Password hashing
- Session management
- 2FA enabled (for testing)

### ✅ POS System
- Order creation
- Item selection from menu
- Quantity adjustment
- Special requests/notes

### ✅ Kitchen Display System
- View pending orders
- Track order status
- Mark orders as complete

### ✅ Menu Management
- Add/edit menu items
- Set prices
- Mark items as available/unavailable

### ✅ Financial Management
- Payment processing
- Invoice generation
- Collection tracking

### ✅ Multi-Currency Support
- Supports 10+ currencies
- Live exchange rates
- Automatic rate updates

---

## 📝 Testing Scenarios

### Scenario 1: Complete Order-to-Payment Flow
1. Login as **sizzlecraft_waiter_1**
2. Click **POS System**
3. Create a new order
4. Add items from menu
5. Apply discount (if any)
6. Process payment
7. Print receipt
8. Login as **sizzlecraft_chef_1** to view kitchen orders

### Scenario 2: Menu Management
1. Login as **sizzlecraft_admin** or **sizzlecraft_manager**
2. Go to **Management → Menu Management**
3. Add a new menu item
4. Set price and description
5. Mark as available/unavailable
6. Verify in POS as waiter

### Scenario 3: Multi-User Workflow
1. Open multiple browser tabs/windows
2. Login as different users simultaneously
3. Waiter: Create an order
4. Chef: View and mark order ready
5. Waiter: Process payment
6. Manager: View analytics

---

## 🐛 Reporting Issues

Found a bug or issue? Please provide:

1. **Your Role:** What was your user role?
2. **Steps to Reproduce:** How did you trigger the issue?
3. **Expected Behavior:** What should have happened?
4. **Actual Behavior:** What actually happened?
5. **Screenshot:** Include if possible
6. **Browser & Device:** Chrome, Firefox, Safari? Desktop or Mobile?

Send to: **office@aidniglobal.in**

---

## 💡 Tips & Tricks

- **Dark Theme Friendly:** Light header with dark navigation
- **Mobile Friendly:** Resize your browser to test mobile experience
- **Keyboard Shortcuts:** Tab through fields for quick data entry
- **Multiple Tabs:** You can open POS in one tab and Analytics in another
- **Role Switching:** Logout and login as different users to test role-based features

---

## ⚠️ Beta Limitations

- This is a **Beta version** - some features are under development
- Data may be reset during testing phases
- Features and UI may change based on feedback
- Not recommended for production use yet
- Performance optimizations are ongoing

---

## 📞 Support

**Email:** office@aidniglobal.in  
**Status:** Available during business hours (IST)  
**Version:** Beta 1.0  
**Last Updated:** December 6, 2025

---

## 🎉 Ready to Test?

```
1. Start the app:     python app.py
2. Open browser:      http://localhost:5000
3. Login:             Use credentials above
4. Have fun testing:  Explore all features!
5. Report feedback:   office@aidniglobal.in
```

**Happy Testing! 🚀**

---

## 📚 Additional Resources

- **Full Documentation:** See `/workspaces/serveopos/README.md`
- **API Reference:** See `/workspaces/serveopos/API_REFERENCE.md`
- **Technical Details:** See `/workspaces/serveopos/IMPLEMENTATION_SUMMARY.md`
- **Test Results:** See `/workspaces/serveopos/BETA_LAUNCH_COMPLETE.md`
