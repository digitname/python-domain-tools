import re
from bs4 import BeautifulSoup
import markdown
import tldextract
import json

def load_custom_rules():
    try:
        with open('custom_rules.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

custom_rules = load_custom_rules()

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
    
    # Check custom rules first
    for rule, category in custom_rules.items():
        if re.search(rule, domain):
            return category
    
    # Default categorization
    if extracted.suffix in ['com', 'org', 'net', 'edu', 'gov']:
        return f'Common TLD (.{extracted.suffix})'
    
    if len(extracted.suffix) == 2:
        return f'Country Code TLD (.{extracted.suffix})'
    
    if len(extracted.suffix) > 2:
        return f'Generic TLD (.{extracted.suffix})'
    
    if extracted.subdomain:
        return 'Subdomain'
    
    return 'Other'

def add_custom_rule(rule, category):
    custom_rules[rule] = category
    with open('custom_rules.json', 'w') as f:
        json.dump(custom_rules, f)

def remove_custom_rule(rule):
    if rule in custom_rules:
        del custom_rules[rule]
        with open('custom_rules.json', 'w') as f:
            json.dump(custom_rules, f)
        return True
    return False
