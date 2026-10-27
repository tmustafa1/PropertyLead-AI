"""
utils.py - Utility functions for PropertyLead AI
Contains input validation, privacy protection (masking), and formatting helpers.
"""

import re
from datetime import datetime, date

# Regular expressions for validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)]{7,16}$")


def validate_lead_input(name: str, phone: str, email: str, budget: float, followup_date: str) -> tuple[bool, str]:
    """
    Validates form inputs for creating or updating a lead.
    Returns: (is_valid: bool, error_message: str)
    """
    # Name validation
    if not name or len(name.strip()) < 2:
        return False, "Customer name must be at least 2 characters long."
    
    if len(name.strip()) > 80:
        return False, "Customer name is too long (maximum 80 characters)."

    # Phone validation
    clean_phone = phone.strip()
    if not clean_phone:
        return False, "Phone number is required."
    
    # Strip spaces and dashes to check digit length
    digits_only = re.sub(r"\D", "", clean_phone)
    if len(digits_only) < 7 or len(digits_only) > 15:
        return False, "Phone number must contain between 7 and 15 digits."
    
    if not PHONE_REGEX.match(clean_phone):
        return False, "Phone number format is invalid. Use digits, optional '+' and dashes."

    # Email validation (optional field, but if provided must be valid)
    if email and email.strip():
        if not EMAIL_REGEX.match(email.strip()):
            return False, "Email address format is invalid (e.g. client@example.com)."

    # Budget validation
    try:
        budget_val = float(budget)
        if budget_val < 0:
            return False, "Budget cannot be negative."
    except (ValueError, TypeError):
        return False, "Budget must be a valid number."

    # Follow-up date validation
    if followup_date:
        try:
            if isinstance(followup_date, (datetime, date)):
                pass
            else:
                datetime.strptime(str(followup_date), "%Y-%m-%d")
        except ValueError:
            return False, "Follow-up date must be in YYYY-MM-DD format."

    return True, ""


def mask_phone(phone: str) -> str:
    """
    Masks a phone number for privacy display (e.g., +91 98765 43210 -> +91 ••••• •3210).
    Protects client data when sharing screens or working in public spaces.
    """
    if not phone:
        return "N/A"
    digits = re.sub(r"\D", "", phone)
    if len(digits) <= 4:
        return "•••• " + digits
    visible_last = digits[-4:]
    masked_part = "•" * (len(digits) - 4)
    # Group masked digits nicely
    grouped_mask = " ".join([masked_part[i:i+4] for i in range(0, len(masked_part), 4)])
    return f"{grouped_mask} {visible_last}".strip()


def mask_email(email: str) -> str:
    """
    Masks an email for privacy display (e.g., john.doe@gmail.com -> j•••e@gmail.com).
    """
    if not email or "@" not in email:
        return email or "N/A"
    
    try:
        user, domain = email.split("@", 1)
        if len(user) <= 2:
            masked_user = user[0] + "•••"
        else:
            masked_user = user[0] + "•" * (len(user) - 2) + user[-1]
        return f"{masked_user}@{domain}"
    except Exception:
        return "••••@••••.com"


def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """
    Formats a numeric budget into a clean, human-readable currency string.
    Example: 250000 -> $250,000
    """
    if amount is None:
        return "N/A"
    try:
        amt = float(amount)
        if amt >= 1_000_000:
            return f"{currency_symbol}{amt/1_000_000:.2f}M"
        return f"{currency_symbol}{amt:,.0f}"
    except (ValueError, TypeError):
        return str(amount)


def sanitize_text(text: str) -> str:
    """
    Basic sanitizer to clean whitespace and strip unwanted null bytes.
    """
    if not text:
        return ""
    return str(text).replace("\x00", "").strip()
