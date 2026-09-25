"""
Comprehensive Automated Test Suite for Connecta
===============================================
Tests StorageService migration & persistence, ValidationService rules,
ContactService business logic (CRUD, search, filtering, stats),
and UI headless smoke initialization.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from services.storage_service import StorageService
from services.validation_service import ValidationService
from services.contact_service import ContactService


class TestStorageAndMigration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_json = os.path.join(self.test_dir, "test_contacts.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_legacy_schema_migration(self):
        # Write legacy schema (similar to original ContactBook)
        legacy_data = [
            {
                "name": "Legacy User",
                "phone": "9876543210",
                "email": "legacy@example.com",
                "address": "Mumbai"
            }
        ]
        with open(self.test_json, "w", encoding="utf-8") as f:
            json.dump(legacy_data, f)

        storage = StorageService(self.test_json)
        contacts = storage.load_contacts()

        self.assertEqual(len(contacts), 1)
        c = contacts[0]
        self.assertEqual(c["name"], "Legacy User")
        self.assertEqual(c["phone"], "9876543210")
        self.assertEqual(c["email"], "legacy@example.com")
        self.assertEqual(c["address"], "Mumbai")
        # Verify migrated new fields
        self.assertTrue(c["id"].startswith("c_"))
        self.assertFalse(c["favorite"])
        self.assertEqual(c["category"], "Other")
        self.assertEqual(c["notes"], "")
        self.assertTrue("created_at" in c)

    def test_atomic_save_and_reload(self):
        storage = StorageService(self.test_json)
        sample = [
            {
                "id": "c_123",
                "name": "Alice Wonder",
                "phone": "9998887776",
                "email": "alice@test.com",
                "address": "Delhi",
                "category": "Work",
                "favorite": True,
                "notes": "Important",
                "created_at": "2026-09-20 12:00"
            }
        ]
        saved = storage.save_contacts(sample)
        self.assertTrue(saved)
        self.assertTrue(os.path.exists(self.test_json))

        reloaded = storage.load_contacts()
        self.assertEqual(len(reloaded), 1)
        self.assertEqual(reloaded[0]["name"], "Alice Wonder")
        self.assertTrue(reloaded[0]["favorite"])


class TestValidationService(unittest.TestCase):
    def test_validate_contact(self):
        # Empty name
        valid, err = ValidationService.validate_contact("", "9876543210")
        self.assertFalse(valid)
        self.assertIn("Full Name is required", err)

        # Single character name
        valid, err = ValidationService.validate_contact("A", "9876543210")
        self.assertFalse(valid)
        self.assertIn("at least 2 characters", err)

        # Empty phone
        valid, err = ValidationService.validate_contact("Riddhi", "")
        self.assertFalse(valid)
        self.assertIn("Phone Number is required", err)

        # Short phone digits
        valid, err = ValidationService.validate_contact("Riddhi", "12345")
        self.assertFalse(valid)
        self.assertIn("7 to 15 digits", err)

        # Invalid phone characters
        valid, err = ValidationService.validate_contact("Riddhi", "98765abcde")
        self.assertFalse(valid)

        # Valid phone with formatting (+91, hyphens, spaces)
        valid, err = ValidationService.validate_contact("Riddhi", "+91 98765-43210")
        self.assertTrue(valid)

        # Invalid email
        valid, err = ValidationService.validate_contact("Riddhi", "9876543210", "bad-email")
        self.assertFalse(valid)
        self.assertIn("valid email address", err)

        # Valid email
        valid, err = ValidationService.validate_contact("Riddhi", "9876543210", "riddhi@example.com")
        self.assertTrue(valid)
        self.assertEqual(err, "")

        # Optional empty email
        valid, err = ValidationService.validate_contact("Riddhi", "9876543210", "")
        self.assertTrue(valid)


class TestContactService(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_json = os.path.join(self.test_dir, "test_contacts.json")
        self.storage = StorageService(self.test_json)
        self.service = ContactService(self.storage)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_crud_and_favorites(self):
        # Add Contact
        data = {
            "name": "Pratham Ambre",
            "phone": "9988776655",
            "email": "pratham@test.com",
            "address": "Delhi",
            "category": "Work",
            "notes": "Colleague",
            "favorite": False,
        }
        success, msg, contact = self.service.add_contact(data)
        self.assertTrue(success)
        self.assertIsNotNone(contact)
        cid = contact["id"]

        # Verify added
        self.assertEqual(len(self.service.get_all()), 1)
        found = self.service.get_by_id(cid)
        self.assertEqual(found["name"], "Pratham Ambre")

        # Duplicate Phone check on Add
        dup_success, dup_msg, _ = self.service.add_contact({
            "name": "Another Person",
            "phone": "9988776655",
        })
        self.assertFalse(dup_success)
        self.assertIn("already exists", dup_msg)

        # Toggle Favorite
        success, is_fav, _ = self.service.toggle_favorite(cid)
        self.assertTrue(success)
        self.assertTrue(is_fav)
        self.assertTrue(self.service.get_by_id(cid)["favorite"])

        # Update Contact
        update_data = {
            "name": "Pratham Ambre Updated",
            "phone": "9988776655",
            "email": "pratham.updated@test.com",
            "address": "Mumbai",
            "category": "Friends",
            "notes": "Updated note",
            "favorite": True,
        }
        u_success, u_msg, updated = self.service.update_contact(cid, update_data)
        self.assertTrue(u_success)
        self.assertEqual(updated["name"], "Pratham Ambre Updated")
        self.assertEqual(updated["category"], "Friends")

        # Statistics
        stats = self.service.get_statistics()
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["favorites"], 1)
        self.assertEqual(stats["with_email"], 1)
        self.assertEqual(stats["categories"]["Friends"], 1)

        # Delete Contact
        d_success, d_msg = self.service.delete_contact(cid)
        self.assertTrue(d_success)
        self.assertEqual(len(self.service.get_all()), 0)

    def test_search_and_sorting(self):
        self.service.add_contact({"name": "Bob Vance", "phone": "1112223334", "category": "Work"})
        self.service.add_contact({"name": "Alice Smith", "phone": "5556667778", "category": "Family"})
        self.service.add_contact({"name": "Charlie Brown", "phone": "9990001112", "category": "Friends"})

        # Search by name
        res = self.service.search_and_filter(query="alice")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["name"], "Alice Smith")

        # Search by phone
        res = self.service.search_and_filter(query="111222")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["name"], "Bob Vance")

        # Sort Name A-Z
        res_az = self.service.search_and_filter(sort_by="Name: A–Z")
        names = [c["name"] for c in res_az]
        self.assertEqual(names, ["Alice Smith", "Bob Vance", "Charlie Brown"])

        # Sort Name Z-A
        res_za = self.service.search_and_filter(sort_by="Name: Z–A")
        names_za = [c["name"] for c in res_za]
        self.assertEqual(names_za, ["Charlie Brown", "Bob Vance", "Alice Smith"])

        # Filter by Category
        res_fam = self.service.search_and_filter(view="category:Family")
        self.assertEqual(len(res_fam), 1)
        self.assertEqual(res_fam[0]["name"], "Alice Smith")


class TestConnectaAppHeadless(unittest.TestCase):
    def test_headless_instantiation(self):
        """Verify ConnectaApp initializes all UI widgets cleanly without error."""
        from ui.app import ConnectaApp

        # Create a temporary storage file for UI testing
        test_dir = tempfile.mkdtemp()
        test_json = os.path.join(test_dir, "ui_test_contacts.json")
        storage = StorageService(test_json)
        storage.save_contacts([
            {
                "id": "c_1",
                "name": "Harsh Patil",
                "phone": "9876543210",
                "email": "harsh@test.com",
                "address": "Mumbai",
                "category": "Work",
                "favorite": False,
                "notes": "Developer",
                "created_at": "2026-09-20 10:00"
            }
        ])

        app = ConnectaApp(storage_service=storage)
        app.withdraw()  # Don't show window on desktop during automated testing

        # Verify layout components exist
        self.assertIsNotNone(app.sidebar)
        self.assertIsNotNone(app.list_view)
        self.assertIsNotNone(app.details_panel)
        self.assertIsNotNone(app.toast)

        # Test view switching
        app.handle_view_change("favorites")
        self.assertEqual(app.current_view, "favorites")

        # Test theme toggle
        initial_theme = app.current_theme
        app.toggle_theme()
        self.assertNotEqual(app.current_theme, initial_theme)

        # Clean shutdown
        app.destroy()
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
