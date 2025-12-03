import unittest
from app import create_app
from extensions import convert_currency

class TestCurrencyConversion(unittest.TestCase):
    """Test currency conversion utility function"""
    
    def setUp(self):
        self.app = create_app()
        self.rates = self.app.config.get('EXCHANGE_RATES', {})
    
    def test_convert_currency_usd_to_eur(self):
        """Test converting USD to EUR"""
        amount = 100.0
        converted = convert_currency(amount, 'USD', 'EUR', self.rates)
        self.assertAlmostEqual(converted, 92.0, places=2)
    
    def test_convert_currency_usd_to_gbp(self):
        """Test converting USD to GBP"""
        amount = 100.0
        converted = convert_currency(amount, 'USD', 'GBP', self.rates)
        self.assertAlmostEqual(converted, 79.0, places=2)
    
    def test_convert_currency_usd_to_inr(self):
        """Test converting USD to INR"""
        amount = 1.0
        converted = convert_currency(amount, 'USD', 'INR', self.rates)
        self.assertAlmostEqual(converted, 83.12, places=2)
    
    def test_convert_currency_same_currency(self):
        """Test converting to same currency (should return unchanged)"""
        amount = 100.0
        converted = convert_currency(amount, 'USD', 'USD', self.rates)
        self.assertEqual(converted, 100.0)
    
    def test_convert_currency_cross_currency(self):
        """Test converting between two non-USD currencies (EUR to GBP)"""
        amount = 100.0
        converted = convert_currency(amount, 'EUR', 'GBP', self.rates)
        expected = (100.0 / 0.92) * 0.79
        self.assertAlmostEqual(converted, expected, places=1)
    
    def test_convert_currency_rounds_to_2_decimals(self):
        """Test that conversion rounds to 2 decimal places"""
        amount = 33.33
        converted = convert_currency(amount, 'USD', 'EUR', self.rates)
        self.assertEqual(len(str(converted).split('.')[-1]), 2)
    
    def test_convert_currency_eur_to_usd(self):
        """Test converting EUR to USD (reverse conversion)"""
        amount = 92.0
        converted = convert_currency(amount, 'EUR', 'USD', self.rates)
        self.assertAlmostEqual(converted, 100.0, places=2)
    
    def test_convert_currency_inr_to_gbp(self):
        """Test converting INR to GBP"""
        amount = 1000.0
        converted = convert_currency(amount, 'INR', 'GBP', self.rates)
        expected = (1000.0 / 83.12) * 0.79
        self.assertAlmostEqual(converted, expected, places=1)
    
    def test_convert_currency_large_amounts(self):
        """Test converting large amounts"""
        amount = 1000000.0
        converted = convert_currency(amount, 'USD', 'EUR', self.rates)
        self.assertAlmostEqual(converted, 920000.0, places=0)
    
    def test_all_supported_currencies(self):
        """Test that all supported currencies can be converted"""
        supported = ['USD', 'EUR', 'GBP', 'INR', 'RON', 'CAD', 'AUD', 'JPY', 'CNY', 'AED']
        amount = 100.0
        for from_curr in supported:
            for to_curr in supported:
                try:
                    converted = convert_currency(amount, from_curr, to_curr, self.rates)
                    self.assertIsInstance(converted, float)
                    self.assertGreater(converted, 0)
                except Exception as e:
                    self.fail(f"Conversion from {from_curr} to {to_curr} failed: {e}")

if __name__ == '__main__':
    unittest.main()
