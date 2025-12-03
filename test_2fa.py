"""Unit tests for Two-Factor Authentication (TOTP)"""
import unittest
from app import create_app
from extensions import db
from models import User
from services.totp import generate_totp_secret, verify_totp_token, use_backup_code, get_totp_current_token
from werkzeug.security import generate_password_hash


class TestTOTPService(unittest.TestCase):
    """Test TOTP service functions"""
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        with self.app.app_context():
            db.create_all()
    
    def test_generate_totp_secret(self):
        """Test TOTP secret generation with QR code and backup codes"""
        result = generate_totp_secret('test_user', issuer='TestApp')
        
        self.assertIn('secret', result)
        self.assertIn('qr_code_data_uri', result)
        self.assertIn('backup_codes', result)
        self.assertIn('backup_codes_hashed', result)
        
        # Secret should be base32
        self.assertTrue(all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567' for c in result['secret']))
        
        # Should have 10 backup codes
        self.assertEqual(len(result['backup_codes']), 10)
        
        # QR code should be data URI
        self.assertTrue(result['qr_code_data_uri'].startswith('data:image/png;base64,'))
    
    def test_verify_totp_token_valid(self):
        """Test verifying a valid TOTP token"""
        result = generate_totp_secret('test_user')
        secret = result['secret']
        
        # Get current token
        token = get_totp_current_token(secret)
        self.assertIsNotNone(token)
        
        # Should verify
        self.assertTrue(verify_totp_token(secret, token))
    
    def test_verify_totp_token_invalid(self):
        """Test that invalid TOTP tokens are rejected"""
        result = generate_totp_secret('test_user')
        secret = result['secret']
        
        # Wrong token should fail
        self.assertFalse(verify_totp_token(secret, '000000'))
        self.assertFalse(verify_totp_token(secret, '999999'))
    
    def test_backup_code_consumption(self):
        """Test consuming backup codes"""
        result = generate_totp_secret('test_user')
        plaintext_codes = result['backup_codes']
        hashed_json = result['backup_codes_hashed']
        
        # Use first backup code
        first_code = plaintext_codes[0]
        consume_result = use_backup_code(hashed_json, first_code)
        
        self.assertTrue(consume_result['valid'])
        self.assertEqual(consume_result['codes_remaining'], 9)


if __name__ == '__main__':
    unittest.main()
