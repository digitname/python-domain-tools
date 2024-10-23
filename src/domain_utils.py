import tldextract
import re
from typing import List, Tuple

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



def extract_domains2(text: str) -> List[str]:
    """Extract unique domains from the given text."""
    domains = set()
    for match in re.finditer(r'\b(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b', text):
        domain = match.group(1)
        if validate_domain(domain):
            domains.add(domain)
    return list(domains)


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

def validate_domain2(domain: str) -> bool:
    """Validate the given domain string."""
    try:
        result = tldextract.extract(domain)
        if result.suffix in ['com', 'org', 'net', 'edu', 'gov', 'co', 'uk', 'de', 'fr', 'ca', 'au', 'in', 'it', 'es', 'nl', 'br', 'ru', 'ch', 'se', 'pl', 'at', 'be', 'dk', 'no', 'fi', 'ie', 'pt', 'mx', 'cz', 'hu', 'gr', 'eu', 'sg', 'hk', 'nz', 'th', 'za', 'vn', 'id', 'tr', 'ph', 'my', 'cl', 'tw', 'ar', 'pe', 'co.uk', 'co.in', 'co.za', 'co.jp', 'co.kr', 'co.id', 'co.th', 'co.uk', 'co.us', 'co.za', 'startup']:
            return True
        else:
            return False
    except Exception:
        return False



def categorize_domain(domain):
    extracted = tldextract.extract(domain)

    # List of known new gTLDs
    new_gtlds = ['app', 'blog', 'shop', 'store', 'tech', 'dev', 'io', 'ai', 'co', 'startup', 'online']

    if not extracted.suffix:
        return "Invalid Domain", ''
    elif extracted.suffix in ['com', 'org', 'net', 'edu', 'gov']:
        return 'generic', extracted.suffix
    elif extracted.suffix in ['co', 'uk', 'de', 'fr', 'ca', 'au', 'in', 'it', 'es', 'nl', 'br', 'ru', 'ch', 'se', 'pl',
                           'at', 'be', 'dk', 'no', 'fi', 'ie', 'pt', 'mx', 'cz', 'hu', 'gr', 'eu', 'sg', 'hk', 'nz',
                           'th', 'za', 'vn', 'id', 'tr', 'ph', 'my', 'cl', 'tw', 'ar', 'pe']:
        return 'country', extracted.suffix
    elif extracted.suffix == 'startup':
        return 'startup', extracted.suffix
    elif extracted.suffix in new_gtlds or len(extracted.suffix.split('.')) > 1:
        return 'New gTLD', '.' + extracted.suffix
    elif extracted.suffix == "com":
        return 'Common TLD', '.com'
    elif extracted.suffix in ["org", "net", "edu", "gov"]:
        return 'Common TLD', '.' + extracted.suffix
    else:
        return 'Other TLD', extracted.suffix


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
