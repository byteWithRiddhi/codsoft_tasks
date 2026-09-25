"""
Storage Service for Connecta
============================
Handles persistent storage of contact records in JSON format.
Guarantees backward compatibility with legacy contact records and ensures
safe atomic file writes.
"""

import json
import os
import shutil
import uuid
from datetime import datetime
from typing import List, Dict, Any


class StorageService:
    """Manages reading, writing, and migrating contacts in contacts.json."""

    def __init__(self, data_file: str = None):
        if data_file is None:
            # Default to contacts.json in project root directory
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_file = os.path.join(project_dir, "contacts.json")
        else:
            self.data_file = os.path.abspath(data_file)

    def load_contacts(self) -> List[Dict[str, Any]]:
        """
        Load contacts from JSON file.
        Automatically migrates legacy contact schemas to support modern fields.
        """
        if not os.path.exists(self.data_file):
            return []

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            if not isinstance(raw_data, list):
                return []

            migrated = []
            for item in raw_data:
                if isinstance(item, dict):
                    migrated.append(self._migrate_contact_record(item))

            return migrated
        except Exception as e:
            # Backup corrupted file if it exists and has content
            try:
                if os.path.getsize(self.data_file) > 0:
                    backup_path = f"{self.data_file}.bak_{int(datetime.now().timestamp())}"
                    shutil.copyfile(self.data_file, backup_path)
            except Exception:
                pass
            return []

    def save_contacts(self, contacts: List[Dict[str, Any]]) -> bool:
        """
        Save contacts list to JSON file using an atomic write pattern.
        """
        temp_file = f"{self.data_file}.tmp"
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(contacts, f, indent=4, ensure_ascii=False)

            # Atomic replace
            shutil.move(temp_file, self.data_file)
            return True
        except Exception:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            return False

    def _migrate_contact_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensures a contact record conforms to the schema with safe defaults.
        Preserves existing fields (name, phone, email, address).
        """
        migrated = dict(record)

        # Unique Identifier
        if "id" not in migrated or not migrated["id"]:
            migrated["id"] = f"c_{uuid.uuid4().hex[:8]}"

        # Standard core fields
        migrated["name"] = str(migrated.get("name", "")).strip()
        migrated["phone"] = str(migrated.get("phone", "")).strip()
        migrated["email"] = str(migrated.get("email", "")).strip()
        migrated["address"] = str(migrated.get("address", "")).strip()

        # Modern upgraded fields with backward-compatible defaults
        if "favorite" not in migrated:
            migrated["favorite"] = False
        else:
            migrated["favorite"] = bool(migrated["favorite"])

        if "category" not in migrated or not migrated["category"]:
            migrated["category"] = "Other"

        if "notes" not in migrated:
            migrated["notes"] = ""
        else:
            migrated["notes"] = str(migrated["notes"])

        if "created_at" not in migrated or not migrated["created_at"]:
            migrated["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        return migrated
