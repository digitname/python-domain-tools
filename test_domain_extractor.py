import unittest
from domain_extractor import extract_domains

class TestDomainExtractor(unittest.TestCase):
    def test_extract_domains(self):
        text = """
        Check out these websites:
        https://www.example.com
        http://subdomain.example.org/page
        https://another-example.com/path/to/page
        This is not a URL: www.not-extracted.com
        """
        expected_domains = ['www.example.com', 'subdomain.example.org', 'another-example.com']
        extracted_domains = extract_domains(text)
        self.assertEqual(set(extracted_domains), set(expected_domains))

if __name__ == '__main__':
    unittest.main()
