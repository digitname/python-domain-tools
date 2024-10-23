import re
from bs4 import BeautifulSoup
import markdown

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
    # This is a basic validation. You might want to implement more sophisticated checks.
    return bool(re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', domain))

def categorize_domain(domain):
    # This is a placeholder function. You might want to implement more sophisticated categorization.
    tld = domain.split('.')[-1]
    if tld in ['com', 'org', 'net']:
        return 'Common TLD'
    elif len(tld) == 2:
        return 'Country Code TLD'
    else:
        return 'Other TLD'
