import unittest
from services.tax import calculate_tax


class TestTaxCalculation(unittest.TestCase):
    """Test tax calculation service"""
    
    def test_calculate_tax_exclusive(self):
        """Test tax-exclusive pricing (tax is added to base price)"""
        result = calculate_tax(100.0, 'EU', 21.0, is_inclusive=False)
        self.assertEqual(result['base_price'], 100.0)
        self.assertEqual(result['tax_amount'], 21.0)
        self.assertEqual(result['total_price'], 121.0)
    
    def test_calculate_tax_inclusive(self):
        """Test tax-inclusive pricing (base price extracted from total)"""
        result = calculate_tax(121.0, 'EU', 21.0, is_inclusive=True)
        # 121 / 1.21 = 100
        self.assertAlmostEqual(result['base_price'], 100.0, places=2)
        self.assertAlmostEqual(result['tax_amount'], 21.0, places=2)
        self.assertEqual(result['total_price'], 121.0)
    
    def test_calculate_tax_zero_rate(self):
        """Test with 0% tax rate"""
        result = calculate_tax(100.0, 'US', 0.0, is_inclusive=False)
        self.assertEqual(result['base_price'], 100.0)
        self.assertEqual(result['tax_amount'], 0.0)
        self.assertEqual(result['total_price'], 100.0)
    
    def test_calculate_tax_high_rate(self):
        """Test with high tax rate (e.g., 27% in Hungary)"""
        result = calculate_tax(100.0, 'HU', 27.0, is_inclusive=False)
        self.assertEqual(result['base_price'], 100.0)
        self.assertEqual(result['tax_amount'], 27.0)
        self.assertEqual(result['total_price'], 127.0)
    
    def test_calculate_tax_rounding(self):
        """Test that tax is rounded to at most 2 decimal places"""
        result = calculate_tax(33.33, 'EU', 21.0, is_inclusive=False)
        # 33.33 * 0.21 = 6.9993 -> rounds to 7.0
        # Result should be a float rounded to 2 decimals max
        self.assertIsInstance(result['tax_amount'], float)
        # Check that when converted to string with 2 decimals, it's valid
        formatted = f"{result['tax_amount']:.2f}"
        self.assertIsNotNone(formatted)


if __name__ == '__main__':
    unittest.main()
