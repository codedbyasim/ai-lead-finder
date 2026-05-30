"""
Utility Functions for AI Lead Finder System
Common functions for data cleaning, validation, and formatting
"""

import re
from typing import Optional
from urllib.parse import urlparse
import validators
import logging

logger = logging.getLogger(__name__)


def clean_email(email: str) -> str:
    """Clean and normalize email address"""
    if not email:
        return ""
    
    email = email.strip().lower()
    # Remove common prefixes
    email = email.replace('mailto:', '')
    return email


def clean_phone(phone: str) -> str:
    """Clean and normalize phone number"""
    if not phone:
        return ""
    
    # Remove common prefixes and formatting
    phone = phone.strip()
    phone = phone.replace('tel:', '').replace('phone:', '').replace('call:', '')
    phone = re.sub(r'[^\d+\-\s()]', '', phone)
    return phone.strip()


def validate_url(url: str) -> bool:
    """Validate if string is a valid URL"""
    if not url:
        return False
    
    try:
        result = validators.url(url)
        return result is True
    except:
        return False


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return ""


def normalize_text(text: str) -> str:
    """Normalize text by removing extra whitespace"""
    if not text:
        return ""
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def is_valid_email(email: str) -> bool:
    """Check if email is valid"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """Check if phone number is valid"""
    if not phone:
        return False
    
    # Remove formatting
    digits = re.sub(r'[^\d]', '', phone)
    
    # Check if it has reasonable length (7-15 digits)
    return 7 <= len(digits) <= 15


def format_phone_pakistani(phone: str) -> str:
    """Format phone number in Pakistani format"""
    if not phone:
        return ""
    
    # Extract digits
    digits = re.sub(r'[^\d]', '', phone)
    
    # If starts with 92, format as +92-XX-XXXXXXX
    if digits.startswith('92'):
        if len(digits) == 12:  # 92XXXXXXXXXX
            return f"+92-{digits[2:4]}-{digits[4:]}"
        elif len(digits) == 11:  # 92XXXXXXXXX
            return f"+92-{digits[2:5]}-{digits[5:]}"
    
    # If starts with 0, format as 0XX-XXXXXXX
    elif digits.startswith('0'):
        if len(digits) == 11:  # 0XXXXXXXXXX
            return f"{digits[0:3]}-{digits[3:]}"
        elif len(digits) == 10:  # 0XXXXXXXXX
            return f"{digits[0:4]}-{digits[4:]}"
    
    return phone


def extract_emails_from_text(text: str) -> list:
    """Extract all email addresses from text"""
    if not text:
        return []
    
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, text)
    
    # Clean and validate
    valid_emails = []
    for email in emails:
        cleaned = clean_email(email)
        if is_valid_email(cleaned):
            valid_emails.append(cleaned)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_emails = []
    for email in valid_emails:
        if email not in seen:
            seen.add(email)
            unique_emails.append(email)
    
    return unique_emails


def extract_phones_from_text(text: str) -> list:
    """Extract all phone numbers from text"""
    if not text:
        return []
    
    # Pakistani format: +92 or 0 followed by digits
    patterns = [
        r'\+92[-\s]?\d{2,4}[-\s]?\d{7,8}',  # +92-XX-XXXXXXX
        r'0\d{2,4}[-\s]?\d{7,8}',  # 0XX-XXXXXXX
        r'\+\d{1,4}[-\s]?\d{1,4}[-\s]?\d{4,10}',  # International
    ]
    
    phones = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        phones.extend(matches)
    
    # Clean and validate
    valid_phones = []
    for phone in phones:
        cleaned = clean_phone(phone)
        if is_valid_phone(cleaned):
            valid_phones.append(cleaned)
    
    # Remove duplicates
    return list(set(valid_phones))


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to maximum length"""
    if not text:
        return ""
    
    text = normalize_text(text)
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def safe_get(dictionary: dict, key: str, default: any = "") -> any:
    """Safely get value from dictionary"""
    try:
        return dictionary.get(key, default)
    except:
        return default
