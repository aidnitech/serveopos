# 🚀 SERVEOPOS - QUICK START GUIDE

## Installation & Setup

### 1. Install Dependencies
```bash
cd /workspaces/serveopos
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python seed.py
```

This creates:
- 4 test users (admin, waiter, kitchen, manager)
- 3 sample menu items

### 3. Run Application
```bash
python app.py
```

Server starts at: **http://localhost:5000**

---

## 🔑 Login Credentials

| Username | Password | Role | Access |
|----------|----------|------|--------|
| admin | admin | Admin | All features |
| manager | manager | Manager | All features |
| waiter | waiter | Waiter | POS, Menu |
| kitchen | kitchen | Kitchen | KDS |

---

## 🧪 Run Tests

```bash
python test_endpoints.py
```

This runs 24 comprehensive tests covering:
- Authentication
- Menu display
- Order creation & management
- KDS display
- Analytics
- API endpoints
- Role-based access control
- Error handling

---

## 📱 Feature Walkthrough

### For Waiters (POS Staff)
1. Login with waiter/waiter
2. Go to **Menu** to see all items
3. Go to **POS** to create orders:
   - Select items and quantities
   - Submit to create order
   - Track order status

### For Kitchen Staff (KDS)
1. Login with kitchen/kitchen
2. Go to **KDS** to see pending orders
3. Each order shows:
   - Order ID
   - Items with quantities
   - Total price
   - Order timestamp

### For Managers/Admins
1. Login with admin/admin or manager/manager
2. Access **Admin Dashboard**
3. Check **Analytics** for:
   - Total orders
   - Total items sold
   - Revenue
4. View **Menu** (read-only)

---

## 🔌 API Endpoints

### Menu
```bash
GET /api/menu
# Returns all menu items in JSON
```

### Order Creation
```bash
POST /pos/orders
Content-Type: application/json

{
  "items": [
    {"menu_item_id": 1, "quantity": 2},
    {"menu_item_id": 2, "quantity": 1}
  ]
}
```

### Get Order
```bash
GET /pos/orders/1
# Returns order details with total
```

### Update Order Status
```bash
PUT /pos/orders/1/status
Content-Type: application/json

{"status": "cooking"}
# Valid statuses: pending, cooking, ready, served
```

### View Pending Orders (KDS)
```bash
GET /kds/orders
# Returns all pending orders with item details
```

### Analytics
```bash
GET /analytics/sales
# Returns total_orders, total_items, total_revenue
```

---

## 📂 File Locations

- **Database:** `instance/app.db`
- **Templates:** `templates/`
- **Routes:** `blueprints/*/routes.py`
- **Models:** `models.py`
- **Config:** `config.py`
- **Tests:** `test_endpoints.py`

---

## 🔧 Configuration

Edit `config.py` to change:
- Database location
- Secret key
- Supported languages
- Debug mode

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Database locked
```bash
rm instance/app.db
python seed.py
```

### Port already in use
```bash
python app.py --port 5001
```

### CSRF token errors
- Ensure you're posting with correct Content-Type
- Check cookies are enabled
- Clear browser cache

---

## 📊 Database Schema

```sql
-- Users
CREATE TABLE user (
  id INTEGER PRIMARY KEY,
  username VARCHAR(64) UNIQUE NOT NULL,
  password_hash VARCHAR(128),
  role VARCHAR(20) DEFAULT 'waiter'
);

-- Menu Items
CREATE TABLE menu_item (
  id INTEGER PRIMARY KEY,
  name VARCHAR(128),
  description TEXT,
  price FLOAT,
  available BOOLEAN DEFAULT TRUE
);

-- Orders
CREATE TABLE order (
  id INTEGER PRIMARY KEY,
  status VARCHAR(20) DEFAULT 'pending',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Order Items
CREATE TABLE order_item (
  id INTEGER PRIMARY KEY,
  order_id INTEGER,
  menu_item_id INTEGER,
  quantity INTEGER DEFAULT 1,
  FOREIGN KEY (order_id) REFERENCES order(id),
  FOREIGN KEY (menu_item_id) REFERENCES menu_item(id)
);
```

---

## 🚀 Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### Environment Variables
```bash
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
export FLASK_ENV="production"
```

### Docker (optional)
Create Dockerfile and docker-compose.yml for containerization

---

## 📈 Monitoring

### Check Database Size
```bash
ls -lh instance/app.db
```

### View Recent Logs
```bash
tail -f app.log
```

### Count Records
```bash
python -c "from models import *; from app import create_app; app = create_app(); 
ctx = app.app_context(); ctx.push(); 
print(f'Orders: {Order.query.count()}')"
```

---

## 🔐 Security Notes

1. Change default passwords in production
2. Use strong SECRET_KEY
3. Enable HTTPS
4. Use environment variables for secrets
5. Regularly backup database
6. Monitor for suspicious login attempts

---

## 📞 Support

For issues or questions:
1. Check BETA_LAUNCH_REPORT.md
2. Review test_endpoints.py for API examples
3. Check Flask documentation: flask.palletsprojects.com
4. Review blueprints for implementation examples

---

**Ready to launch! Good luck!** 🎉
