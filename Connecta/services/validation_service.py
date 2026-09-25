"""
Validation Service for Connecta
===============================
Provides business rule validation for contact data inputs.
"""

import re
from typing import Tuple, List, Dict, Any, Optional


class ValidationService:
    """Validates contact input fields and detects potential duplicates."""

    @staticmethod
    def validate_contact(name: str, phone: str, email: str = "") -> Tuple[bool, str]:
        """
        Validate essential contact fields.
        Returns:
            (is_valid, error_message)
        """
        clean_name = (name or "").strip()
        clean_phone = (phone or "").strip()
        clean_email = (email or "").strip()

        # 1. Name is required
        if not clean_name:
            return False, "Full Name is required and cannot be empty."

        if len(clean_name) < 2:
            return False, "Full Name must be at least 2 characters long."

        # 2. Phone is required
        if not clean_phone:
            return False, "Phone Number is required and cannot be empty."

        # Check digits in phone
        digits = re.sub(r"\D", "", clean_phone)
        if len(digits) < 7 or len(digits) > 15:
            return False, "Please enter a valid phone number (7 to 15 digits)."

        # Ensure no invalid characters in phone string
        if not re.match(r"^[\d\s+\-().]{7,25}$", clean_phone):
            return False, "Phone number contains invalid characters."

        # 3. Email is optional, but if provided, validate format
        if clean_email:
            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_pattern, clean_email):
                return False, "Please enter a valid email address (e.g. name@example.com)."

        return True, ""

    @staticmethod
    def check_duplicate_phone(
        contacts: List[Dict[str, Any]],
        phone: str,
        current_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Check if another contact already exists with the same phone number.
        Returns the existing contact's name if a duplicate is found, else None.
        """
        target_digits = re.sub(r"\D", "", phone or "")
        if not target_digits:
            return None

        for contact in contacts:
            if current_id and contact.get("id") == current_id:
                continue
            existing_digits = re.sub(r"\D", "", contact.get("phone", ""))
            if existing_digits == target_digits:
                return contact.get("name", "Unknown Contact")

        return None
