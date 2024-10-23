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

    # List of known new gTLDs
    new_gtlds = ['app', 'blog', 'shop', 'store', 'tech', 'dev', 'io', 'ai', 'co', 'startup', 'online']

    if not extracted.suffix:
        return "Invalid Domain"
    elif extracted.subdomain:
        return "Subdomain"
    elif extracted.suffix in new_gtlds or len(extracted.suffix.split('.')) > 1:
        return f"New gTLD (.{extracted.suffix})"
    elif extracted.suffix == "com":
        return "Common TLD (.com)"
    elif extracted.suffix in ["org", "net", "edu", "gov"]:
        return f"Common TLD (.{extracted.suffix})"
    else:
        return f"Other TLD (.{extracted.suffix})"


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
