# PythonAnywhere Deployment Guide

Complete step-by-step guide to deploy ServeoPOS on PythonAnywhere.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Account Setup](#account-setup)
3. [Manual Deployment Steps](#manual-deployment-steps)
4. [Automated Deployment](#automated-deployment)
5. [Configuration](#configuration)
6. [Database Setup](#database-setup)
7. [Static Files](#static-files)
8. [WSGI Configuration](#wsgi-configuration)
9. [Environment Variables](#environment-variables)
10. [Testing](#testing)
11. [Troubleshooting](#troubleshooting)
12. [Production Best Practices](#production-best-practices)

## Prerequisites

- A PythonAnywhere account (free or paid): https://www.pythonanywhere.com
- GitHub account with ServeoPOS repository access
- SSH key uploaded to PythonAnywhere
- Git installed locally (for repository cloning)

## Account Setup

### 1. Create PythonAnywhere Account

1. Visit https://www.pythonanywhere.com
2. Click "Sign Up"
3. Choose your username (becomes part of your domain: username.pythonanywhere.com)
4. Select your account type (free or paid)
5. Verify your email

### 2. Generate and Upload SSH Key

PythonAnywhere uses SSH for repository access. Set up your SSH key:

1. Log into PythonAnywhere
2. Go to "Account" tab
3. Scroll to "SSH keys" section
4. Click "Add a new SSH key"
5. Copy the key from your local machine (or generate one):
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/pythonanywhere_key -C "your_email@example.com"
   ```
6. Paste the public key content

## Manual Deployment Steps

### Step 1: SSH into PythonAnywhere

```bash
ssh username@ssh.pythonanywhere.com
```

Replace `username` with your PythonAnywhere username.

### Step 2: Clone the Repository

```bash
cd ~
git clone https://github.com/YOUR_GITHUB_USERNAME/serveopos.git
cd serveopos
```

### Step 3: Create Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.12 serveopos
```

This creates a Python 3.12 virtual environment named `serveopos`.

### Step 4: Install Dependencies

```bash
pip install -r requirements-production.txt
```

### Step 5: Set Up Environment Variables

```bash
# Copy example configuration
cp .env.example ~/.env

# Edit the configuration
nano ~/.env
```

Key settings to update:
- `SECRET_KEY`: Generate a random secret key
- `DATABASE_URL`: Point to your database (SQLite on PythonAnywhere)
- `FLASK_ENV`: Set to `production`

### Step 6: Initialize Database

```bash
python << 'EOF'
from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database initialized successfully!")
EOF
```

### Step 7: Create Web App on PythonAnywhere

1. Log into PythonAnywhere web dashboard
2. Go to "Web" tab
3. Click "Add a new web app"
4. Choose "Manual configuration"
5. Select "Python 3.12"
6. Click through to finish

### Step 8: Configure WSGI File

1. In PythonAnywhere Web tab, click on your web app
2. Look for "WSGI configuration file"
3. Click the link to edit it
4. Replace the entire contents with:

```python
import sys
import os

project_path = os.path.expanduser('~/serveopos')
if project_path not in sys.path:
    sys.path.insert(0, project_path)

activate_this = os.path.expanduser('~/.virtualenvs/serveopos/bin/activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})

from dotenv import load_dotenv
load_dotenv(os.path.join(project_path, '.env'))

from app import create_app
application = create_app()
application.config['ENV'] = 'production'
application.config['DEBUG'] = False
```

5. Save the file

### Step 9: Configure Static Files

1. In PythonAnywhere Web tab, scroll to "Static files"
2. Click "Add a new static file mapping"
3. Set URL path: `/static/`
4. Set Directory: `/home/username/serveopos/static`
5. Replace `username` with your PythonAnywhere username

### Step 10: Reload Web App

1. Go to Web tab
2. Click "Reload Web App"
3. Wait 30 seconds for the app to start

### Step 11: Test Your Deployment

Visit https://username.pythonanywhere.com (replace username) in your browser.

You should see the ServeoPOS login page. Test with the default credentials:
- **Email**: admin@example.com
- **Password**: admin123

## Automated Deployment

Use the provided deployment script for faster setup:

```bash
bash DEPLOY.sh your_username
```

This automates steps 1-6 and provides guidance for steps 7-10.

## Configuration

### Essential Settings

Update `~/.env` on PythonAnywhere with:

```bash
# Security
SECRET_KEY=generate_a_random_key_here
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=sqlite:///instance/app.db

# Session
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
CSRF_ENABLED=True

# Domain
PYTHONANYWHERE_DOMAIN=username.pythonanywhere.com
ALLOWED_HOSTS=username.pythonanywhere.com,www.username.pythonanywhere.com
```

### Generate Secret Key

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

Use this output as your `SECRET_KEY` in `.env`.

## Database Setup

### Create Database Directory

```bash
ssh username@ssh.pythonanywhere.com
mkdir -p ~/serveopos/instance
```

### Initialize Schema

```bash
# Via SSH
python << 'EOF'
from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database created successfully!")
EOF
```

### Seed Initial Data (Optional)

```bash
python seed.py
python seed_menu.py
```

## Static Files

Static files (CSS, JavaScript, images) must be configured in PythonAnywhere:

1. Ensure directory `/home/username/serveopos/static/` exists
2. In PythonAnywhere Web tab, configure static file mapping:
   - URL: `/static/`
   - Directory: `/home/username/serveopos/static`
3. Reload web app

## WSGI Configuration

The WSGI file is the entry point for PythonAnywhere's web server. It's located at:
- `/var/www/username_pythonanywhere_com_wsgi.py`

Edit it via PythonAnywhere dashboard or copy the template:

```bash
# Via SSH
cp ~/serveopos/pythonanywhere_wsgi.py /var/www/username_pythonanywhere_com_wsgi.py
```

After any changes, reload the web app from the Web tab.

## Environment Variables

All environment variables should be in `~/.env`:

```bash
# Edit with nano
nano ~/.env

# Then reload the web app
# Go to PythonAnywhere Web tab -> Reload Web App
```

**Important**: PythonAnywhere must be restarted to pick up changes to `.env`.

### Full Environment Template

See `.env.example` in the repository for complete documentation.

## Testing

### Run Tests on PythonAnywhere

```bash
ssh username@ssh.pythonanywhere.com
cd ~/serveopos
source ~/.virtualenvs/serveopos/bin/activate
python -m pytest -v
```

### Test Application Access

1. Navigate to https://username.pythonanywhere.com
2. Login with default admin credentials:
   - Email: `admin@example.com`
   - Password: `admin123`
3. Verify dashboard loads correctly
4. Test basic functionality:
   - Navigate to different sections
   - Try creating a menu item
   - Test POS dashboard
   - Verify multi-tenant isolation

### Run Smoke Tests

```bash
ssh username@ssh.pythonanywhere.com
cd ~/serveopos
source ~/.virtualenvs/serveopos/bin/activate
python smoke_test.py
```

## Troubleshooting

### Web App Shows 500 Error

1. Check error log:
   - PythonAnywhere Web tab -> "Error log"
   - Look for recent errors

2. Check server log:
   - PythonAnywhere Web tab -> "Server log"

3. Verify WSGI file syntax:
   ```bash
   python /var/www/username_pythonanywhere_com_wsgi.py
   ```

4. Verify `.env` file exists and is readable:
   ```bash
   cat ~/.env
   ```

### Database Errors

**Error: "sqlite3.OperationalError: no such table: user"**

```bash
# Reinitialize database
cd ~/serveopos
source ~/.virtualenvs/serveopos/bin/activate
python << 'EOF'
from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database recreated!")
EOF
```

**Error: "database is locked"**

SQLite has limited concurrent access. For production with many users, consider migrating to PostgreSQL:

```bash
# Contact PythonAnywhere support to add PostgreSQL
# Then update DATABASE_URL to point to PostgreSQL
```

### Permission Denied Errors

Make sure file permissions are correct:

```bash
chmod 600 ~/.env
chmod -R 755 ~/serveopos
chmod -R 755 ~/serveopos/static
chmod 777 ~/serveopos/instance
```

### Import Errors

Verify virtual environment is activated in WSGI file:

```python
# In /var/www/username_pythonanywhere_com_wsgi.py
activate_this = os.path.expanduser('~/.virtualenvs/serveopos/bin/activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})
```

### Static Files Not Loading

1. Ensure static file mapping exists in Web tab
2. Verify directory path: `/home/username/serveopos/static`
3. Reload web app
4. Check browser cache (Ctrl+Shift+Delete)

### Changes Not Taking Effect

Always reload the web app after making changes:

1. Go to PythonAnywhere Web tab
2. Click "Reload Web App"
3. Wait 30 seconds
4. Refresh browser (Ctrl+F5)

## Production Best Practices

### 1. Enable HTTPS Only

PythonAnywhere automatically provides HTTPS. Configure in app:

```python
# In config.py
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

### 2. Strong Secret Key

Generate and use a strong secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never use the default or commit it to Git.

### 3. Regular Backups

Download your database regularly:

```bash
# Via SSH
cd ~/serveopos/instance
ls -lah app.db

# Download locally
scp username@ssh.pythonanywhere.com:~/serveopos/instance/app.db ./app.db.backup
```

### 4. Monitor Error Logs

Regularly check PythonAnywhere error logs for issues:

```bash
ssh username@ssh.pythonanywhere.com
tail -f ~/serveopos.log
```

### 5. Keep Dependencies Updated

Periodically update packages (test in development first):

```bash
source ~/.virtualenvs/serveopos/bin/activate
pip install -U -r requirements-production.txt
```

### 6. Enable Rate Limiting

Already configured in the app to prevent abuse:

```python
# In app.py
limiter = Limiter(app, key_func=get_remote_address)
```

### 7. Database Scaling

SQLite works for small to medium deployments. For high traffic:

1. Migrate to PostgreSQL
2. Upgrade PythonAnywhere account to enable database features
3. Update `DATABASE_URL` in `.env`

### 8. Security Headers

Ensure security headers are configured:

```python
# In config.py
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': "'self'",
}
```

### 9. Logging

Enable structured logging for production:

```bash
# In ~/.env
LOG_LEVEL=INFO
```

Check logs regularly for errors and security issues.

### 10. Test Before Deploying

Always test changes locally:

```bash
python -m pytest
python smoke_test.py
```

Then test on PythonAnywhere staging before deploying to production.

## Next Steps

1. **Custom Domain**: Set up your domain in PythonAnywhere Domains tab
2. **Email Configuration**: Configure SMTP for password resets and notifications
3. **Payment Integration**: If accepting payments, configure Stripe or PayPal
4. **Analytics**: Set up Google Analytics or error tracking (Sentry)
5. **Monitoring**: Set up uptime monitoring and alerts

## Support

For PythonAnywhere-specific issues:
- PythonAnywhere Help: https://help.pythonanywhere.com
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/

For ServeoPOS issues:
- GitHub Issues: https://github.com/YOUR_GITHUB_USERNAME/serveopos/issues
- Documentation: See README.md and other guide documents

---

**Last Updated**: 2024
**Version**: 1.0
**Status**: Production Ready
