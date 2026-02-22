"""
Data validation utilities for lead collection
"""
import re
from typing import Dict, Any, Optional
from datetime import datetime

def validate_email(email: str) -> bool:
    """Validate email format using regex"""
    if not email or not isinstance(email, str):
        return False

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))

def validate_phone(phone: str) -> bool:
    """Validate phone number - basic length and format check"""
    if not phone or not isinstance(phone, str):
        return False

    # Remove spaces, hyphens, parentheses for validation
    cleaned = re.sub(r'[\s\-\(\)]', '', phone.strip())

    # Must be between 7-15 digits (international format)
    if not re.match(r'^\+?\d{7,15}$', cleaned):
        return False

    return True

def validate_required_fields(lead_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate that all required fields are present and not null
    Returns dict of field -> error_message for failed validations
    """
    errors = {}
    required_fields = ['full_name', 'phone', 'email', 'location', 'job_type']

    for field in required_fields:
        value = lead_data.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            errors[field] = f"{field} is required"
        elif field == 'email' and not validate_email(str(value)):
            errors['email'] = "Invalid email format"
        elif field == 'phone' and not validate_phone(str(value)):
            errors['phone'] = "Invalid phone number format"

    return errors

def sanitize_string(value: str) -> str:
    """Sanitize string input by trimming and basic cleaning"""
    if not isinstance(value, str):
        return ""
    return value.strip()

def format_lead_data(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format and sanitize lead data"""
    formatted = {}

    # Sanitize string fields
    string_fields = ['full_name', 'email', 'location', 'job_type']
    for field in string_fields:
        if field in lead_data:
            formatted[field] = sanitize_string(str(lead_data[field]))

    # Phone number formatting
    if 'phone' in lead_data:
        phone = str(lead_data['phone']).strip()
        # Ensure it starts with + if it looks like an international number
        if phone and not phone.startswith('+') and len(re.sub(r'\D', '', phone)) > 10:
            phone = '+' + phone
        formatted['phone'] = phone

    return formatted

def create_lead_record(
    phone: str,
    lead_data: Dict[str, Any],
    language_code: str,
    consent_status: str = "Granted",
    consent_version: str = "v1.0"
) -> Dict[str, Any]:
    """
    Create a complete lead record for storage
    """
    now = datetime.utcnow().isoformat()

    record = {
        "timestamp": now,
        "phone": phone,
        "language_code": language_code,
        "consent_status": consent_status,
        "consent_timestamp": now,
        "consent_version": consent_version
    }

    # Add lead data fields
    formatted_data = format_lead_data(lead_data)
    record.update(formatted_data)

    return record

