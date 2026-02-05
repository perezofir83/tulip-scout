"""Validation utilities."""
import re
from typing import Optional
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def infer_email_pattern(domain: str, name: str = "") -> list[str]:
    """
    Infer possible email patterns for a domain.
    
    Args:
        domain: Company domain (e.g., "example.com")
        name: Full name (e.g., "John Doe")
    
    Returns:
        List of possible email addresses
    """
    patterns = [f"info@{domain}", f"contact@{domain}"]
    
    if name:
        name_parts = name.lower().split()
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            patterns.extend([
                f"{first}.{last}@{domain}",
                f"{first}_{last}@{domain}",
                f"{first}{last}@{domain}",
                f"{first[0]}{last}@{domain}",
                f"{first}.{last[0]}@{domain}",
            ])
    
    return patterns


def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return None


def sanitize_phone(phone: str) -> str:
    """Sanitize phone number (remove special characters)."""
    return re.sub(r'[^\d+]', '', phone)


def validate_linkedin_url(url: str) -> bool:
    """Check if URL is a valid LinkedIn profile/company URL."""
    return bool(re.search(r'linkedin\.com/(in|company)/', url))
