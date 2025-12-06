# 🔐 ServeoPOS Beta - Master Credentials Sheet

**Date:** December 6, 2025  
**Version:** 1.0 Beta  
**Status:** CONFIDENTIAL - FOR INTERNAL USE ONLY  

---

## ⚠️ SECURITY NOTE

This document contains sensitive credentials. Keep it secure and share only with authorized personnel.

---

## 🔑 MASTER LOGIN CREDENTIALS

### Platform Level

#### Super Admin (Platform Owner)
```
Username: superadmin
Password: superadmin@123
Role: Super Admin
Access: Full platform access, all restaurants
Status: ✅ Active
```

---

### Sizzlecraft Restaurant

#### Restaurant Admin
```
Username: sizzlecraft_admin
Password: sizzlecraft@admin123
Role: Restaurant Admin
Restaurant: Sizzlecraft Restaurant
Access: Full restaurant management
Status: ✅ Active
```

#### Manager
```
Username: sizzlecraft_manager
Password: manager@123
Role: Manager
Restaurant: Sizzlecraft Restaurant
Access: Dashboard, POS, Analytics, Menu, Reports
Status: ✅ Active
```

#### Kitchen Staff (2)
```
Username: sizzlecraft_chef_1
Password: chef@123
Role: Kitchen
Restaurant: Sizzlecraft Restaurant
Access: Kitchen Display System, Order Management
Status: ✅ Active

Username: sizzlecraft_chef_2
Password: chef@123
Role: Kitchen
Restaurant: Sizzlecraft Restaurant
Access: Kitchen Display System, Order Management
Status: ✅ Active
```

#### Waiters (5)
```
Username: sizzlecraft_waiter_1
Password: waiter@123
Role: Waiter
Restaurant: Sizzlecraft Restaurant
Access: POS System, Menu, Order Placement
Status: ✅ Active

Username: sizzlecraft_waiter_2
Password: waiter@123
Role: Waiter
Restaurant: Sizzlecraft Restaurant
Access: POS System, Menu, Order Placement
Status: ✅ Active

Username: sizzlecraft_waiter_3
Password: waiter@123
Role: Waiter
Restaurant: Sizzlecraft Restaurant
Access: POS System, Menu, Order Placement
Status: ✅ Active

Username: sizzlecraft_waiter_4
Password: waiter@123
Role: Waiter
Restaurant: Sizzlecraft Restaurant
Access: POS System, Menu, Order Placement
Status: ✅ Active

Username: sizzlecraft_waiter_5
Password: waiter@123
Role: Waiter
Restaurant: Sizzlecraft Restaurant
Access: POS System, Menu, Order Placement
Status: ✅ Active
```

---

## 📊 Access Matrix by Role

| Feature | Super Admin | Restaurant Admin | Manager | Chef | Waiter |
|---------|:-----------:|:----------------:|:-------:|:----:|:------:|
| Platform Settings | ✅ | ❌ | ❌ | ❌ | ❌ |
| Restaurant Management | ✅ | ✅ | ❌ | ❌ | ❌ |
| Admin Dashboard | ✅ | ✅ | ✅ | ❌ | ❌ |
| Menu Management | ✅ | ✅ | ✅ | ❌ | ✅ (view) |
| Inventory Management | ✅ | ✅ | ✅ | ❌ | ❌ |
| Staff Management | ✅ | ✅ | ❌ | ❌ | ❌ |
| POS System | ✅ | ✅ | ✅ | ❌ | ✅ |
| Kitchen Display | ✅ | ✅ | ❌ | ✅ | ❌ |
| Order Management | ✅ | ✅ | ✅ | ✅ | ✅ |
| Analytics & Reports | ✅ | ✅ | ✅ | ❌ | ❌ |
| Payment Processing | ✅ | ✅ | ✅ | ❌ | ✅ |
| Collections & Invoicing | ✅ | ✅ | ✅ | ❌ | ❌ |
| Audit Logs | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## 🚀 Quick Access Links

### Login Page
```
http://localhost:5000/auth/login
```

### After Login (by Role)

**Super Admin:**
```
http://localhost:5000/admin/
```

**Restaurant Admin:**
```
http://localhost:5000/admin/
http://localhost:5000/pos/
```

**Manager:**
```
http://localhost:5000/admin/
http://localhost:5000/pos/
http://localhost:5000/analytics/sales
http://localhost:5000/menu/
```

**Kitchen Staff:**
```
http://localhost:5000/kds/
http://localhost:5000/kds/orders
```

**Waiter:**
```
http://localhost:5000/pos/
http://localhost:5000/menu/
```

---

## 📝 Password Policy (Beta)

- **Format:** Lower/uppercase + numbers + special characters
- **Length:** Minimum 8 characters
- **Expiry:** None (beta version)
- **Change:** Available in user settings
- **Reset:** Contact: office@aidniglobal.in

---

## 🔒 Security Recommendations

### DO:
✅ Keep credentials secure  
✅ Use unique passwords for production  
✅ Change default passwords after first login  
✅ Enable 2FA for admin accounts  
✅ Log out after each session  
✅ Report suspicious activity immediately  

### DON'T:
❌ Share credentials via email  
❌ Write down passwords on paper  
❌ Use passwords in public places  
❌ Keep credentials in browser  
❌ Share access with unauthorized people  
❌ Leave account logged in unattended  

---

## 📞 Account Management

### Password Reset
1. Go to login page
2. Click "Forgot Password" (to be implemented)
3. Or contact: office@aidniglobal.in

### Account Lockout
- After 5 failed attempts, account locked for 15 minutes
- Contact support to unlock

### Role Change
- Only Super Admin can change user roles
- Changes logged in audit trail

---

## 🧪 Test Scenarios

### Scenario 1: POS Workflow
1. Login as **sizzlecraft_waiter_1**
2. Access POS system
3. Create order, add items
4. Process payment
5. Print receipt

### Scenario 2: Kitchen Operations
1. Login as **sizzlecraft_chef_1**
2. View Kitchen Display System
3. Check pending orders
4. Update order status
5. Mark complete

### Scenario 3: Management Dashboard
1. Login as **sizzlecraft_manager**
2. View sales analytics
3. Check inventory
4. Review reports
5. Manage menu

### Scenario 4: Admin Functions
1. Login as **sizzlecraft_admin**
2. Access admin dashboard
3. Manage staff
4. Configure settings
5. View audit logs

---

## 🎯 First Login Checklist

After first login, do the following:

### For All Users
- [ ] Verify correct username display
- [ ] Check user role badge
- [ ] Explore navigation menu
- [ ] Test role-specific features
- [ ] Change password (optional)

### For Admin/Manager
- [ ] Access dashboard
- [ ] Check menu items
- [ ] View analytics
- [ ] Test reporting

### For POS Users
- [ ] Test order creation
- [ ] Check menu loading
- [ ] Verify payment options
- [ ] Print test receipt

### For Kitchen Staff
- [ ] Access KDS
- [ ] View pending orders
- [ ] Test order updates

---

## 📱 Multi-Device Login

Users can be logged in on multiple devices:
- Desktop
- Laptop
- Tablet
- Mobile

Each device has independent session.

---

## 🔄 Session Management

- **Session Duration:** 8 hours
- **Idle Timeout:** 30 minutes
- **Concurrent Sessions:** Unlimited per user
- **Auto-Logout:** Yes (after idle timeout)

---

## 📊 User Statistics

| Metric | Value |
|--------|-------|
| Total Users | 10 |
| Super Admins | 1 |
| Restaurant Admins | 1 |
| Managers | 1 |
| Kitchen Staff | 2 |
| Waiters | 5 |
| Active Users | 10/10 |

---

## ✅ Beta Testing Status

- ✅ All accounts created
- ✅ All passwords verified
- ✅ All roles tested
- ✅ All routes accessible
- ✅ Permissions verified
- ✅ Ready for user testing

---

## 🚀 For Live Production

### Before Production Deployment:

1. **Change All Passwords**
   - Use strong, unique passwords
   - Store securely in password manager
   - Implement password policy

2. **Enable 2FA**
   - For all admin accounts
   - For sensitive operations
   - Optional for staff

3. **Database Backup**
   - Daily backups
   - Off-site storage
   - Test restore process

4. **SSL/TLS**
   - Install SSL certificate
   - Force HTTPS
   - Security headers

5. **Monitoring**
   - Set up logging
   - Configure alerts
   - Monitor user actions

6. **Compliance**
   - GDPR compliance
   - Data protection
   - Audit requirements

---

## 📞 Support Contacts

**Email:** office@aidniglobal.in  
**Company:** Aidni Global LLP & Gaatha Ventures SRL  
**Hours:** Business hours (IST)  
**Version:** Beta 1.0  

---

## ⚠️ CONFIDENTIAL NOTICE

This document contains sensitive information. Keep it:
- Locked in secure storage
- Access limited to authorized personnel
- Updated when credentials change
- Destroyed when deployment goes live

---

**Created:** December 6, 2025  
**Version:** 1.0 Beta  
**Status:** FOR BETA TESTING ONLY  
**Next Review:** Before production deployment
