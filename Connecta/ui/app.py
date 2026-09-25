"""
Main Application Window for Connecta
====================================
Orchestrates Sidebar, Contact List, Details Panel, Toast Notifications,
and Modal Dialogs into a unified responsive desktop experience.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any

from . import theme
from .sidebar import Sidebar
from .contact_list import ContactListView
from .contact_details import ContactDetailsPanel
from .contact_form import ContactFormDialog
from .dialogs import ConfirmDeleteDialog
from .toast import ToastManager

try:
    from services.contact_service import ContactService
    from services.storage_service import StorageService
except ImportError:
    from ..services.contact_service import ContactService
    from ..services.storage_service import StorageService


class ConnectaApp(ctk.CTk):
    """Main Connecta Desktop Application Window."""

    def __init__(self, storage_service: Optional[StorageService] = None):
        super().__init__()

        # Appearance setup
        ctk.set_appearance_mode("light")  # Default light mode
        ctk.set_default_color_theme("blue")

        self.title("Connecta - Contact Manager")
        self.geometry("1120x720")
        self.minsize(940, 580)
        self.configure(fg_color=theme.BG_APP)

        # Services
        self.contact_service = ContactService(storage_service)

        # State tracking
        self.current_view = "all"
        self.selected_contact_id: Optional[str] = None
        self.current_theme = "light"

        # Build main layout
        self._build_layout()

        # Keyboard shortcuts
        self._bind_shortcuts()

        # Initial data render
        self.refresh_ui()

        # Select first contact if available
        all_contacts = self.contact_service.get_all()
        if all_contacts:
            self.select_contact(all_contacts[0])

    def _build_layout(self):
        # 1. Left Sidebar
        self.sidebar = Sidebar(
            self,
            on_view_change=self.handle_view_change,
            on_add_click=self.open_add_modal,
            on_theme_toggle=self.toggle_theme,
        )
        self.sidebar.pack(side="left", fill="y")

        # 2. Right Details Panel (Packed before center so center expands)
        self.details_panel = ContactDetailsPanel(
            self,
            on_edit_click=self.open_edit_modal,
            on_delete_click=self.open_delete_modal,
            on_favorite_toggle=self.handle_favorite_toggle,
            width=320,
        )
        self.details_panel.pack(side="right", fill="y")

        # 3. Center Contact List View
        self.list_view = ContactListView(
            self,
            on_select_contact=self.select_contact,
            on_favorite_toggle=self.handle_favorite_toggle,
            on_add_contact_click=self.open_add_modal,
            on_search_or_sort_change=self.refresh_contact_list,
        )
        self.list_view.pack(side="left", fill="both", expand=True)

        # 4. Toast Notification Manager (attached to list_view for clean overlay)
        self.toast = ToastManager(self.list_view)

    def _bind_shortcuts(self):
        """Keyboard shortcuts for power users."""
        self.bind("<Control-n>", lambda event: self.open_add_modal())
        self.bind("<Control-N>", lambda event: self.open_add_modal())
        self.bind("<Control-f>", lambda event: self._focus_search())
        self.bind("<Control-F>", lambda event: self._focus_search())
        self.bind("<Escape>", lambda event: self.list_view.clear_search())

    def _focus_search(self):
        self.list_view.search_entry.focus_set()

    # ---------------------------------------------------------
    # NAVIGATION & VIEW LOGIC
    # ---------------------------------------------------------
    def handle_view_change(self, view_id: str):
        """Called when a user clicks a sidebar navigation item."""
        self.current_view = view_id

        # Update view title and subtitle in list header
        if view_id == "all":
            self.list_view.set_header_title("All Contacts", "Manage your personal and professional network.")
        elif view_id == "favorites":
            self.list_view.set_header_title("Favorites", "Quick access to your starred priority contacts.")
        elif view_id == "recent":
            self.list_view.set_header_title("Recently Added", "Contacts sorted by most recently created.")
            self.list_view.sort_var.set("Recently Added")
        elif view_id.startswith("category:"):
            cat_name = view_id.split("category:", 1)[1]
            self.list_view.set_header_title(f"{cat_name} Contacts", f"Contacts organized in the {cat_name} category.")

        self.refresh_contact_list()

    def refresh_ui(self):
        """Refresh statistics, badges, and contact list."""
        stats = self.contact_service.get_statistics()
        self.sidebar.update_badge_counts(stats)
        self.list_view.update_statistics(stats)
        self.refresh_contact_list()

    def refresh_contact_list(self):
        """Filter and render contacts based on active view, search, and sort."""
        query = self.list_view.get_search_query()
        sort_by = self.list_view.get_sort_by()

        contacts = self.contact_service.search_and_filter(
            query=query,
            view=self.current_view,
            category_filter="All",
            sort_by=sort_by,
        )

        self.list_view.render_contacts(
            contacts=contacts,
            active_view=self.current_view,
            selected_id=self.selected_contact_id,
        )

        # Update details panel: if selected contact still exists, keep showing it;
        # otherwise, show first matching contact or empty state
        if self.selected_contact_id:
            current = self.contact_service.get_by_id(self.selected_contact_id)
            if current and current in contacts:
                self.details_panel.show_contact(current)
            elif contacts:
                self.select_contact(contacts[0])
            else:
                self.selected_contact_id = None
                self.details_panel.show_contact(None)
        elif contacts:
            self.select_contact(contacts[0])
        else:
            self.details_panel.show_contact(None)

    def select_contact(self, contact: Dict[str, Any]):
        """Select a contact and display in details panel."""
        if not contact:
            self.selected_contact_id = None
            self.details_panel.show_contact(None)
            return

        self.selected_contact_id = contact.get("id")
        self.details_panel.show_contact(contact)
        self.list_view.selected_contact_id = self.selected_contact_id

        # Re-highlight active card in list view
        for cid, card in self.list_view.card_widgets.items():
            if cid == self.selected_contact_id:
                card.configure(
                    fg_color=theme.BG_CARD_SELECTED,
                    border_color=theme.PRIMARY,
                    border_width=2,
                )
            else:
                card.configure(
                    fg_color=theme.BG_CARD,
                    border_color=theme.BORDER_LIGHT,
                    border_width=1,
                )

    # ---------------------------------------------------------
    # CRUD & ACTION HANDLERS
    # ---------------------------------------------------------
    def open_add_modal(self):
        """Open Add Contact modal form."""
        def on_saved(new_contact):
            self.refresh_ui()
            self.select_contact(new_contact)
            self.toast.show(f"Added '{new_contact.get('name')}' successfully!", level="success")

        ContactFormDialog(
            parent=self,
            contact_service=self.contact_service,
            contact_data=None,
            on_save=on_saved,
        )

    def open_edit_modal(self, contact: Dict[str, Any]):
        """Open Edit Contact modal form."""
        def on_saved(updated_contact):
            self.refresh_ui()
            self.select_contact(updated_contact)
            self.toast.show(f"Updated '{updated_contact.get('name')}' successfully!", level="success")

        ContactFormDialog(
            parent=self,
            contact_service=self.contact_service,
            contact_data=contact,
            on_save=on_saved,
        )

    def open_delete_modal(self, contact: Dict[str, Any]):
        """Open delete confirmation modal."""
        cid = contact.get("id")
        name = contact.get("name", "Contact")

        def on_confirm_delete():
            success, msg = self.contact_service.delete_contact(cid)
            if success:
                self.selected_contact_id = None
                self.refresh_ui()
                self.toast.show(msg, level="info")
            else:
                self.toast.show(msg, level="error")

        ConfirmDeleteDialog(
            parent=self,
            contact_name=name,
            on_confirm=on_confirm_delete,
        )

    def handle_favorite_toggle(self, contact_id: str):
        """Toggle favorite state of contact."""
        success, is_fav, msg = self.contact_service.toggle_favorite(contact_id)
        if success:
            self.refresh_ui()
            # If current contact is being viewed in details panel, refresh it
            if self.selected_contact_id == contact_id:
                curr = self.contact_service.get_by_id(contact_id)
                self.details_panel.show_contact(curr)
            self.toast.show(msg, level="info")

    def toggle_theme(self):
        """Toggle between Light and Dark mode."""
        if self.current_theme == "light":
            self.current_theme = "dark"
            ctk.set_appearance_mode("dark")
            self.sidebar.btn_theme.configure(text="☀️ Light Mode")
            self.toast.show("Switched to Dark Mode", level="info")
        else:
            self.current_theme = "light"
            ctk.set_appearance_mode("light")
            self.sidebar.btn_theme.configure(text="🌙 Dark Mode")
            self.toast.show("Switched to Light Mode", level="info")
