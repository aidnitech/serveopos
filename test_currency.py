import unittest
from app import create_app
from extensions import db, convert_currency
from models import User, MenuItem, Invoice, Collection, Payment, Transaction
from datetime import datetime

class TestCurrencyConversion(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.rates = self.app.config.get('EXCHANGE_RATES', {})
    
    def test_convert_currency_usd_to_eur(self):
        """Test converting USD to EUR"""
        amount = 100.0
        converted = convert_currency(amount, 'USD', 'EUR', self.rates)
        # 100 USD * 0.92 = 92 EUR
        self.assertAlmostEqual(converted, 92.0, places=2)
    
    def test_convert_currency_usd_to_gbp(self):
        """Test converting USD to GBP"""
        amount = 100.0
        converted = convert_currency(amount, 'USD', 'GBP', self.rates)
        # 100 USD * 0.79 = 79 GBP
        self.assertAlmostEqual(converted, 79.0, places=2)
    
    def test_convert_currency_usd_to_inr(self):
        """Test converting USD to INR"""
        amount = 1.0
        converted = convert_currency(amount, 'USD', 'INR', rates)
        # 1 USD * 83.12 = 83.12 INR
        self.assertAlmostEqual(converted, 83.12, places=2)
    
    def test_convert_currency_same_currency(self):
        """Test converting to same currency (should return unchanged)"""
        rates = self.app.config.get('EXCHANGE_RATES', {})
        amount = 100.0
        converted = convert_currency(amount, 'USD', 'USD', rates)
        self.assertEqual(converted, 100.0)
    
    def test_convert_currency_cross_currency(self):
        """Test converting between two non-USD currencies (EUR to GBP)"""
        rates = self.app.config.get('EXCHANGE_RATES', {})
        amount = 100.0
        # 100 EUR = 100 / 0.92 USD ≈ 108.7 USD
        # 108.7 USD * 0.79 GBP ≈ 85.86 GBP
        converted = convert_currency(amount, 'EUR', 'GBP', rates)
        expected = (100.0 / 0.92) * 0.79
        self.assertAlmostEqual(converted, expected, places=1)
    
    def test_convert_currency_rounds_to_2_decimals(self):
        """Test that conversion rounds to 2 decimal places"""
        rates = self.app.config.get('EXCHANGE_RATES', {})
        amount = 33.33
        converted = convert_currency(amount, 'USD', 'EUR', rates)
        # Should have exactly 2 decimal places
        self.assertEqual(len(str(converted).split('.')[-1]), 2)
    
    def test_user_currency_preference_in_menu_endpoint(self):
        """Test that menu endpoint returns prices in user's selected currency"""
        with self.app.app_context():
            # Create a menu item with USD price
            item = MenuItem(name='Test Item', description='Test', price=100.0, available=True)
            db.session.add(item)
            db.session.commit()
            
            # Login as EUR user and check menu price
            with self.client:
                self.client.post('/auth/login', data={'username': 'user_eur', 'password': 'pass'}, follow_redirects=True)
                response = self.client.get('/admin/api/menu')
                self.assertEqual(response.status_code, 200)
                data = response.get_json()
                self.assertGreater(len(data), 0)
                # Price should be converted to EUR (100 * 0.92 = 92)
                self.assertAlmostEqual(data[0]['price'], 92.0, places=2)
    
    def test_user_currency_endpoint_update(self):
        """Test updating user's currency preference"""
        with self.app.app_context():
            with self.client:
                # Login and update currency
                self.client.post('/auth/login', data={'username': 'user_usd', 'password': 'pass'}, follow_redirects=True)
                response = self.client.put('/admin/api/users/1/currency', 
                                          json={'currency': 'eur'},
                                          content_type='application/json')
                self.assertEqual(response.status_code, 200)
                data = response.get_json()
                self.assertEqual(data['currency'], 'EUR')
                
                # Verify currency was updated in database
                user = User.query.get(1)
                self.assertEqual(user.currency, 'EUR')
    
    def test_invalid_currency_rejected(self):
        """Test that invalid currency codes are rejected"""
        with self.app.app_context():
            with self.client:
                self.client.post('/auth/login', data={'username': 'user_usd', 'password': 'pass'}, follow_redirects=True)
                response = self.client.put('/admin/api/users/1/currency',
                                          json={'currency': 'XXX'},
                                          content_type='application/json')
                self.assertEqual(response.status_code, 400)
                data = response.get_json()
                self.assertIn('error', data)

class TestCurrencyInvoices(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test users
            self.user_usd = User(username='user_usd', password_hash='pass', role='admin', currency='USD')
            self.user_eur = User(username='user_eur', password_hash='pass', role='admin', currency='EUR')
            
            # Create test invoices
            inv1 = Invoice(invoice_number='INV-001', customer_name='Customer 1', total=100.0, status='issued', issued_at=datetime.utcnow())
            inv2 = Invoice(invoice_number='INV-002', customer_name='Customer 2', total=500.0, status='issued', issued_at=datetime.utcnow())
            
            db.session.add_all([self.user_usd, self.user_eur, inv1, inv2])
            db.session.commit()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_invoices_converted_in_user_currency(self):
        """Test that invoices API returns amounts in user's currency"""
        with self.app.app_context():
            with self.client:
                # Login as EUR user
                self.client.post('/auth/login', data={'username': 'user_eur', 'password': 'pass'}, follow_redirects=True)
                response = self.client.get('/admin/api/invoices')
                self.assertEqual(response.status_code, 200)
                data = response.get_json()
                self.assertGreater(len(data), 0)
                # First invoice: 100 USD * 0.92 = 92 EUR
                self.assertAlmostEqual(data[0]['total'], 92.0, places=2)

class TestCurrencyCollections(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test users
            self.user_usd = User(username='user_usd', password_hash='pass', role='admin', currency='USD')
            self.user_gbp = User(username='user_gbp', password_hash='pass', role='admin', currency='GBP')
            
            # Create test collections with payments
            col1 = Collection(customer_name='Customer A', total_amount=200.0, paid_amount=100.0, balance=100.0, status='pending')
            pay1 = Payment(collection_id=1, amount=100.0, payment_method='cash', reference_id='REF-001', received_by='User', payment_date=datetime.utcnow())
            
            db.session.add_all([self.user_usd, self.user_gbp, col1])
            db.session.commit()
            
            pay1.collection_id = col1.id
            db.session.add(pay1)
            db.session.commit()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_collections_converted_in_user_currency(self):
        """Test that collections API returns amounts in user's currency"""
        with self.app.app_context():
            with self.client:
                # Login as GBP user
                self.client.post('/auth/login', data={'username': 'user_gbp', 'password': 'pass'}, follow_redirects=True)
                response = self.client.get('/admin/api/collections')
                self.assertEqual(response.status_code, 200)
                data = response.get_json()
                self.assertGreater(len(data), 0)
                # Collection: 200 USD * 0.79 = 158 GBP
                self.assertAlmostEqual(data[0]['total'], 158.0, places=2)
                # Paid: 100 USD * 0.79 = 79 GBP
                self.assertAlmostEqual(data[0]['paid'], 79.0, places=2)

if __name__ == '__main__':
    unittest.main()
