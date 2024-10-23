import unittest
from app import app, init_db
from domain_extractor import extract_domains, validate_domain, categorize_domain

class TestDomainExtractor(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_db()

    def test_extract_domains(self):
        text = "Visit example.com or test.org for more information."
        domains = extract_domains(text)
        self.assertEqual(set(domains), {"example.com", "test.org"})

    def test_validate_domain(self):
        self.assertTrue(validate_domain("example.com"))
        self.assertFalse(validate_domain("invalid-domain"))

    def test_categorize_domain(self):
        self.assertEqual(categorize_domain("example.com"), "Common TLD (.com)")
        self.assertEqual(categorize_domain("example.co.uk"), "Country Code TLD (.uk)")

    def test_index_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_login(self):
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)

    def test_bulk_import(self):
        # First, log in
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        # Then try to access bulk import page
        response = self.app.get('/bulk_import')
        self.assertEqual(response.status_code, 302)  # Redirect to login page

if __name__ == '__main__':
    unittest.main()
