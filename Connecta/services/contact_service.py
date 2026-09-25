"""
Contact Service for Connecta
============================
Centralizes business logic, in-memory state, search, sorting, filtering,
and CRUD operations for contacts.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from .storage_service import StorageService
from .validation_service import ValidationService


class ContactService:
    """Manages contact business operations and state."""

    VALID_CATEGORIES = ["Family", "Friends", "Work", "College", "Other"]

    def __init__(self, storage_service: Optional[StorageService] = None):
        self.storage = storage_service or StorageService()
        self.contacts: List[Dict[str, Any]] = []
        self.load()

    def load(self) -> None:
        """Load contacts from storage."""
        self.contacts = self.storage.load_contacts()

    def save(self) -> bool:
        """Persist contacts to storage."""
        return self.storage.save_contacts(self.contacts)

    def get_all(self) -> List[Dict[str, Any]]:
        """Return shallow copy of all contacts."""
        return list(self.contacts)

    def get_by_id(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Find a contact by its unique id."""
        for c in self.contacts:
            if c.get("id") == contact_id:
                return c
        return None

    def add_contact(self, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validate and create a new contact.
        """
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()

        is_valid, err_msg = ValidationService.validate_contact(name, phone, email)
        if not is_valid:
            return False, err_msg, None

        # Check duplicate phone warning (still allowed if user wishes, but we note it)
        duplicate_name = ValidationService.check_duplicate_phone(self.contacts, phone)
        if duplicate_name:
            # We reject exact duplicate phone numbers to prevent clutter
            return False, f"A contact '{duplicate_name}' already exists with this phone number.", None

        category = data.get("category", "Other")
        if category not in self.VALID_CATEGORIES:
            category = "Other"

        new_contact = {
            "id": f"c_{uuid.uuid4().hex[:8]}",
            "name": name,
            "phone": phone,
            "email": email,
            "address": data.get("address", "").strip(),
            "category": category,
            "notes": data.get("notes", "").strip(),
            "favorite": bool(data.get("favorite", False)),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        self.contacts.append(new_contact)
        saved = self.save()
        if not saved:
            return False, "Failed to persist contact to storage file.", None

        return True, f"Contact '{name}' added successfully!", new_contact

    def update_contact(self, contact_id: str, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validate and update an existing contact.
        """
        contact = self.get_by_id(contact_id)
        if not contact:
            return False, "Contact not found.", None

        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()

        is_valid, err_msg = ValidationService.validate_contact(name, phone, email)
        if not is_valid:
            return False, err_msg, None

        # Check duplicate phone for other contacts
        duplicate_name = ValidationService.check_duplicate_phone(self.contacts, phone, current_id=contact_id)
        if duplicate_name:
            return False, f"Another contact '{duplicate_name}' already has this phone number.", None

        category = data.get("category", contact.get("category", "Other"))
        if category not in self.VALID_CATEGORIES:
            category = "Other"

        # Update in-place
        contact["name"] = name
        contact["phone"] = phone
        contact["email"] = email
        contact["address"] = data.get("address", "").strip()
        contact["category"] = category
        contact["notes"] = data.get("notes", "").strip()
        contact["favorite"] = bool(data.get("favorite", contact.get("favorite", False)))

        saved = self.save()
        if not saved:
            return False, "Failed to persist changes to storage file.", None

        return True, f"Contact '{name}' updated successfully!", contact

    def delete_contact(self, contact_id: str) -> Tuple[bool, str]:
        """
        Delete a contact by id.
        """
        contact = self.get_by_id(contact_id)
        if not contact:
            return False, "Contact not found."

        name = contact.get("name", "Contact")
        self.contacts = [c for c in self.contacts if c.get("id") != contact_id]
        saved = self.save()
        if not saved:
            return False, "Failed to remove contact from storage file."

        return True, f"Contact '{name}' has been deleted."

    def toggle_favorite(self, contact_id: str) -> Tuple[bool, bool, str]:
        """
        Toggle the favorite status of a contact.
        Returns: (success, is_favorite_now, message)
        """
        contact = self.get_by_id(contact_id)
        if not contact:
            return False, False, "Contact not found."

        contact["favorite"] = not contact.get("favorite", False)
        self.save()
        status_msg = "marked as favorite" if contact["favorite"] else "removed from favorites"
        return True, contact["favorite"], f"{contact.get('name', 'Contact')} {status_msg}."

    def search_and_filter(
        self,
        query: str = "",
        view: str = "all",
        category_filter: str = "All",
        sort_by: str = "Name: A–Z"
    ) -> List[Dict[str, Any]]:
        """
        Filter and sort contacts based on search text, active view, category, and sort order.
        """
        results = list(self.contacts)

        # 1. Filter by view
        if view == "favorites":
            results = [c for c in results if c.get("favorite", False)]
        elif view == "recent":
            # Sort by created_at descending and take top or all
            pass
        elif view.startswith("category:"):
            target_cat = view.split("category:", 1)[1]
            results = [c for c in results if c.get("category", "").lower() == target_cat.lower()]

        # 2. Filter by category dropdown/pill if not "All"
        if category_filter and category_filter != "All":
            results = [c for c in results if c.get("category", "").lower() == category_filter.lower()]

        # 3. Search query across name, phone, email, address, notes
        clean_q = (query or "").strip().lower()
        if clean_q:
            results = [
                c for c in results
                if clean_q in c.get("name", "").lower()
                or clean_q in c.get("phone", "").lower()
                or clean_q in c.get("email", "").lower()
                or clean_q in c.get("address", "").lower()
                or clean_q in c.get("notes", "").lower()
            ]

        # 4. Sort results
        if sort_by == "Name: A–Z":
            results.sort(key=lambda c: c.get("name", "").lower())
        elif sort_by == "Name: Z–A":
            results.sort(key=lambda c: c.get("name", "").lower(), reverse=True)
        elif sort_by == "Recently Added":
            results.sort(key=lambda c: c.get("created_at", ""), reverse=True)
        elif sort_by == "Oldest First":
            results.sort(key=lambda c: c.get("created_at", ""))
        else:
            results.sort(key=lambda c: c.get("name", "").lower())

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate summary counts for dashboard and sidebar badges.
        """
        total = len(self.contacts)
        favorites = sum(1 for c in self.contacts if c.get("favorite", False))
        with_email = sum(1 for c in self.contacts if c.get("email", "").strip())
        with_phone = sum(1 for c in self.contacts if c.get("phone", "").strip())

        category_counts = {cat: 0 for cat in self.VALID_CATEGORIES}
        for c in self.contacts:
            cat = c.get("category", "Other")
            if cat in category_counts:
                category_counts[cat] += 1
            else:
                category_counts["Other"] += 1

        return {
            "total": total,
            "favorites": favorites,
            "with_email": with_email,
            "with_phone": with_phone,
            "categories": category_counts,
        }
