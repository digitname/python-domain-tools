import re
from bs4 import BeautifulSoup
import markdown
import tldextract

def extract_domains(text, file_type='text'):
    if file_type == 'html':
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
    elif file_type == 'markdown':
        html = markdown.markdown(text)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()

    domain_pattern = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]\b'
    domains = re.findall(domain_pattern, text, re.IGNORECASE)
    return list(set(domains))  # Remove duplicates

def validate_domain(domain):
    return bool(re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', domain))

def categorize_domain(domain):
    extracted = tldextract.extract(domain)
    
    # Check for common TLDs
    if extracted.suffix in ['com', 'org', 'net', 'edu', 'gov']:
        return f'Common TLD (.{extracted.suffix})'
    
    # Check for country code TLDs
    if len(extracted.suffix) == 2:
        return f'Country Code TLD (.{extracted.suffix})'
    
    # Check for generic TLDs
    if len(extracted.suffix) > 2:
        return f'Generic TLD (.{extracted.suffix})'
    
    # Check for subdomains
    if extracted.subdomain:
        return 'Subdomain'
    
    return 'Other'
