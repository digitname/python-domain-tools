import tldextract
import re
from typing import List, Tuple

def extract_domains(text: str) -> List[str]:
    """Extract unique domains from the given text."""
    # Implementation omitted for brevity

def validate_domain(domain: str) -> bool:
    """Validate the given domain string."""
    # Implementation omitted for brevity

def categorize_domain(domain: str) -> Tuple[str, str]:
    """Categorize the given domain."""
    # Implementation omitted for brevity

def add_custom_rule(rule: str, category: str) -> None:
    """Add a custom rule to the domain categorization."""
    # Implementation omitted for brevity

def remove_custom_rule(rule: str) -> None:
    """Remove a custom rule from the domain categorization."""
    # Implementation omitted for brevity

def load_custom_rules() -> List[Tuple[str, str]]:
    """Load custom rules for domain categorization."""
    # Implementation omitted for brevity
