"""Input validation helpers. Every function returns a cleaned value or raises ValidationError."""
import re
from datetime import date, datetime


class ValidationError(ValueError):
    """Raised when user input is invalid."""


def validate_name(name):
    name = (name or "").strip()
    if len(name) < 2:
        raise ValidationError("Name must be at least 2 characters.")
    return name


def validate_email(email):
    email = (email or "").strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValidationError("Email is not valid (example: a@b.com).")
    return email


def validate_phone(phone):
    phone = (phone or "").strip()
    digits = re.sub(r"[\s\-+()]", "", phone)
    if not digits.isdigit() or not 7 <= len(digits) <= 15:
        raise ValidationError("Phone must contain 7-15 digits.")
    return phone


def validate_date(text):
    try:
        d = datetime.strptime((text or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Date must be YYYY-MM-DD.")
    if d > date.today():
        raise ValidationError("Date cannot be in the future.")
    return d.isoformat()


def validate_item(item):
    item = (item or "").strip()
    if not item:
        raise ValidationError("Item cannot be empty.")
    return item


def validate_amount(value):
    try:
        amount = float(str(value).strip())
    except ValueError:
        raise ValidationError("Amount must be a number.")
    if not 0 < amount < 10_000_000:
        raise ValidationError("Amount must be greater than 0.")
    return round(amount, 2)
