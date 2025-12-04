# ServeoPOS - Restaurant POS & Management System

A comprehensive, multi-tenant point-of-sale (POS) and restaurant management system built with Flask and SQLAlchemy. Features role-based access control, inventory management, multi-currency support, tax calculation, and comprehensive analytics.

## 🚀 Quick Start

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/aidnitech/serveopos.git
cd serveopos

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python << 'EOF'
from app import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
EOF

# 5. Seed sample data (optional)
python seed.py
python seed_menu.py

# 6. Run the application
python app.py
```

Visit http://localhost:5000 and login with:
- **Email**: admin@example.com
- **Password**: admin123

### Production Deployment

Deploy to PythonAnywhere in minutes:

**Option 1: Quick Automated Deployment**
```bash
bash DEPLOY.sh your_pythonanywhere_username
```

**Option 2: Follow Step-by-Step Guide**
See [PYTHONANYWHERE_DEPLOYMENT.md](./PYTHONANYWHERE_DEPLOYMENT.md) for comprehensive instructions.

## ✨ Features

### Core POS Features
- ✅ Real-time order management
- ✅ Multiple payment methods
- ✅ Receipt printing
- ✅ Kitchen display system (KDS)
- ✅ Table management
- ✅ Split bills & item modifications

### Restaurant Management
- ✅ Menu management (items, categories, pricing)
- ✅ Inventory tracking and low-stock alerts
- ✅ Recipe & ingredient management
- ✅ Staff management with roles
- ✅ Staff shift scheduling

### Financial Features
- ✅ Multi-currency support with live exchange rates
- ✅ Tax calculation (VAT, GST, custom rules)
- ✅ Comprehensive sales analytics
- ✅ Revenue reports by period/item/category
- ✅ Payment reconciliation
- ✅ Daily settlement reports

### Admin & Multi-Tenant
- ✅ Multi-restaurant management
- ✅ Role-based access control (Admin, Manager, Waiter, Chef)
- ✅ Audit logging for compliance
- ✅ Data isolation between restaurants
- ✅ Restaurant configuration management

### User Experience
- ✅ Multi-language support (English, Spanish, Portuguese, Hindi)
- ✅ Responsive web interface
- ✅ Two-factor authentication (2FA)
- ✅ Barcode/QR code support
- ✅ Mobile-friendly POS interface

## 📋 Documentation

- **[PYTHONANYWHERE_DEPLOYMENT.md](./PYTHONANYWHERE_DEPLOYMENT.md)** - Complete PythonAnywhere deployment guide
- **[QUICKSTART.md](./QUICKSTART.md)** - Quick start guide with examples
- **[API_REFERENCE.md](./API_REFERENCE.md)** - API endpoint documentation
- **[VERIFICATION_REPORT.md](./VERIFICATION_REPORT.md)** - Test results and feature verification

## 🏗️ Architecture

### Technology Stack
- **Framework**: Flask 3.1.2
- **ORM**: SQLAlchemy 2.0.44
- **Database**: SQLite (dev), PostgreSQL (prod recommended)
- **Authentication**: Flask-Login with password hashing
- **Internationalization**: Flask-Babel
- **Testing**: pytest with comprehensive coverage

### Project Structure
```
serveopos/
├── app.py                 # Flask application factory
├── models.py              # SQLAlchemy data models
├── config.py              # Configuration management
├── blueprints/            # Feature blueprints (admin, pos, inventory, etc.)
├── services/              # Business logic (tax, payments, exchange rates)
├── static/                # CSS, JavaScript, images
├── templates/             # HTML templates
├── migrations/            # Database migrations (Alembic)
├── tests/                 # Unit and integration tests
├── conftest.py            # pytest configuration and fixtures
└── requirements*.txt      # Python dependencies
```

## 🧪 Testing

Run the full test suite:

```bash
# All tests
python -m pytest -v

# Specific test file
python -m pytest tests/test_endpoints.py -v

# With coverage
python -m pytest --cov=blueprints --cov=services --cov=models

# Smoke tests (verify all features)
python smoke_test.py
```

**Test Status**: ✅ 65/65 unit tests passing | ✅ 7/7 smoke tests passing

## 🔐 Security Features

- Password hashing with Werkzeug
- CSRF protection on all forms
- Session cookies (secure, httponly)
- Role-based access control (RBAC)
- SQL injection prevention (via SQLAlchemy ORM)
- Audit logging for administrative actions
- Two-factor authentication support

## 📦 Installation

### Prerequisites
- Python 3.11+
- pip or poetry
- Virtual environment (recommended)

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-cov black flake8
```

### Production Setup
```bash
# Use production requirements
pip install -r requirements-production.txt

# Configure environment
cp .env.example .env
# Edit .env with production settings
```

## ⚙️ Configuration

Configuration is managed via:

1. **Environment Variables** (`~/.env` or OS environment)
2. **config.py** - Default configurations
3. **PythonAnywhere Web Dashboard** - Runtime settings

See `.env.example` for all available configuration options.

### Key Configuration Variables
```bash
# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///instance/app.db

# Security
CSRF_ENABLED=True
SESSION_COOKIE_SECURE=True

# Internationalization
BABEL_DEFAULT_LOCALE=en
BABEL_SUPPORTED_LOCALES=en,es,pt,hi
```

## 🚢 Deployment

### PythonAnywhere (Recommended for Quick Setup)

1. **Automated**: `bash DEPLOY.sh username`
2. **Manual**: Follow [PYTHONANYWHERE_DEPLOYMENT.md](./PYTHONANYWHERE_DEPLOYMENT.md)

### Other Platforms

Deployable to any platform supporting Flask:
- AWS (Elastic Beanstalk, EC2)
- Heroku
- DigitalOcean
- Google Cloud
- Azure

All require:
- Python 3.11+
- SQLite or PostgreSQL
- Environment variable configuration
- Gunicorn or similar WSGI server

## 📈 Performance & Scalability

- SQLite suitable for small to medium deployments (< 100 concurrent users)
- PostgreSQL recommended for production (> 100 concurrent users)
- Rate limiting enabled to prevent abuse
- Database indexes optimized for common queries
- Caching ready (use Flask-Caching with Redis)

## 🐛 Troubleshooting

### Database Errors
```bash
# Reinitialize schema
python << 'EOF'
from app import create_app
from models import db
app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
EOF
```

### Missing Dependencies
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Template or Import Errors
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

See detailed troubleshooting in [PYTHONANYWHERE_DEPLOYMENT.md](./PYTHONANYWHERE_DEPLOYMENT.md#troubleshooting).

## 📝 Logs & Debugging

### Enable Debug Mode (Development Only)
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### View Application Logs
```bash
# On PythonAnywhere
ssh username@ssh.pythonanywhere.com
tail -f ~/serveopos.log

# Locally
# Check Flask output in terminal
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- All tests pass: `python -m pytest`
- Code follows PEP 8
- Documentation is updated

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Support

- **Issues**: [GitHub Issues](https://github.com/aidnitech/serveopos/issues)
- **Documentation**: See docs folder and README files
- **Email**: support@serveopos.com

## 🗺️ Roadmap

### Completed ✅
- Multi-tenant architecture
- POS functionality
- Inventory management
- Analytics & reporting
- Multi-currency support
- 2FA authentication

### In Progress 🔄
- Mobile app (React Native)
- Advanced analytics dashboard
- Integration with accounting software
- Loyalty program system

### Planned 📋
- AI-powered inventory predictions
- Blockchain receipt verification
- Voice ordering
- Cryptocurrency payment support

## 📊 System Requirements

### Minimum (Development)
- Python 3.11
- 2GB RAM
- 500MB disk space
- SQLite

### Recommended (Production)
- Python 3.12
- 4GB RAM (8GB+ with 100+ concurrent users)
- 5GB disk space (SSD recommended)
- PostgreSQL database
- Redis for caching

## 🔄 Version History

- **v0.1.0** (Current) - Initial release
  - Core POS functionality
  - Inventory management
  - Multi-tenant support
  - 65/65 tests passing

## 📞 Contact

**ServeoPOS Development Team**
- Email: dev@serveopos.com
- GitHub: https://github.com/aidnitech/serveopos

---

**Last Updated**: 2024
**Status**: ✅ Production Ready
**Test Coverage**: 65/65 unit tests + 7/7 smoke tests
