import unittest
from app import app, extract_domains

class TestDomainExtractor(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_extract_domains(self):
        text = "Visit example.com or test.org for more information."
        domains = extract_domains(text)
        self.assertEqual(set(domains), {"example.com", "test.org"})

    def test_index_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_domain_extraction_post(self):
        response = self.app.post('/', data={
            'text': 'Check out example.com',
            'file_type': 'text'
        })
        self.assertIn(b'example.com', response.data)

    def test_search(self):
        # First, add a domain to the database
        self.app.post('/', data={
            'text': 'Visit example.com',
            'file_type': 'text'
        })
        
        # Then search for it
        response = self.app.get('/search?query=example')
        self.assertIn(b'example.com', response.data)

    def test_export_csv(self):
        # Add a domain to the database
        self.app.post('/', data={
            'text': 'Visit example.com',
            'file_type': 'text'
        })
        
        response = self.app.get('/export?format=csv')
        self.assertEqual(response.mimetype, 'text/csv')
        self.assertIn(b'example.com', response.data)

    def test_export_json(self):
        # Add a domain to the database
        self.app.post('/', data={
            'text': 'Visit example.com',
            'file_type': 'text'
        })
        
        response = self.app.get('/export?format=json')
        self.assertEqual(response.mimetype, 'application/json')
        self.assertIn(b'example.com', response.data)

if __name__ == '__main__':
    unittest.main()
