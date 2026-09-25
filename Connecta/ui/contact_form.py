"""
Contact Form Dialog for Connecta
================================
Modern modal window used for both Adding and Editing contacts,
featuring inline error alerts, clear input fields, and category pickers.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any, Callable
from . import theme
try:
    from services.contact_service import ContactService
except ImportError:
    from ..services.contact_service import ContactService


class ContactFormDialog(ctk.CTkToplevel):
    """Modern modal dialog for adding or editing a contact."""

    def __init__(
        self,
        parent: ctk.CTk,
        contact_service: ContactService,
        contact_data: Optional[Dict[str, Any]] = None,
        on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        super().__init__(parent)
        self.contact_service = contact_service
        self.contact_data = contact_data
        self.is_edit_mode = contact_data is not None
        self.on_save = on_save

        title_text = "Edit Contact" if self.is_edit_mode else "Add New Contact"
        self.title(title_text)
        self.geometry("520x680")
        self.minsize(480, 600)
        self.transient(parent)
        self.grab_set()

        self.configure(fg_color=theme.BG_CARD)

        # Center over parent
        self._center_window(parent, 520, 680)

        # Build UI
        self._build_ui()

    def _center_window(self, parent, width, height):
        self.update_idletasks()
        try:
            parent.update_idletasks()
            px = parent.winfo_x()
            py = parent.winfo_y()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + (pw - width) // 2
            y = py + (ph - height) // 2
            self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

    def _build_ui(self):
        # Header Frame
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(24, 12))

        title_str = "Edit Contact" if self.is_edit_mode else "Create New Contact"
        sub_str = "Update contact details below." if self.is_edit_mode else "Fill in the details to add a contact to your book."

        lbl_title = ctk.CTkLabel(
            header,
            text=title_str,
            font=("Segoe UI", 20, "bold"),
            text_color=theme.TEXT_MAIN,
            anchor="w",
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            header,
            text=sub_str,
            font=("Segoe UI", 12),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Inline Error Banner (Hidden by default)
        self.error_frame = ctk.CTkFrame(
            self,
            fg_color=("#FEF2F2", "#7F1D1D"),
            border_color=("#FECACA", "#DC2626"),
            border_width=1,
            corner_radius=8,
        )
        self.lbl_error = ctk.CTkLabel(
            self.error_frame,
            text="",
            font=("Segoe UI", 11, "bold"),
            text_color=("#991B1B", "#FCA5A5"),
            wraplength=420,
            justify="left",
        )
        self.lbl_error.pack(padx=14, pady=8, anchor="w")

        # Scrollable form body
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=30, pady=(0, 14))

        # 1. Full Name *
        self._create_field_label(body, "Full Name *", "Required")
        self.entry_name = ctk.CTkEntry(
            body,
            placeholder_text="e.g. Riddhi Pawar",
            font=("Segoe UI", 13),
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=38,
            corner_radius=8,
        )
        self.entry_name.pack(fill="x", pady=(0, 12))
        self.entry_name.focus_set()

        # 2. Phone Number *
        self._create_field_label(body, "Phone Number *", "Required")
        self.entry_phone = ctk.CTkEntry(
            body,
            placeholder_text="e.g. +91 98765 43210",
            font=("Segoe UI", 13),
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=38,
            corner_radius=8,
        )
        self.entry_phone.pack(fill="x", pady=(0, 12))

        # 3. Email Address
        self._create_field_label(body, "Email Address", "Optional")
        self.entry_email = ctk.CTkEntry(
            body,
            placeholder_text="e.g. name@example.com",
            font=("Segoe UI", 13),
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=38,
            corner_radius=8,
        )
        self.entry_email.pack(fill="x", pady=(0, 12))

        # 4. Physical Address
        self._create_field_label(body, "Address", "Optional")
        self.entry_address = ctk.CTkEntry(
            body,
            placeholder_text="e.g. 42 Marine Drive, Mumbai",
            font=("Segoe UI", 13),
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=38,
            corner_radius=8,
        )
        self.entry_address.pack(fill="x", pady=(0, 12))

        # 5. Category Selection
        self._create_field_label(body, "Category", "Select group")
        self.category_var = ctk.StringVar(value="Work")
        self.category_opt = ctk.CTkOptionMenu(
            body,
            values=ContactService.VALID_CATEGORIES,
            variable=self.category_var,
            font=("Segoe UI", 12),
            fg_color=theme.BG_INPUT,
            text_color=theme.TEXT_MAIN,
            button_color=theme.PRIMARY,
            button_hover_color=theme.PRIMARY_HOVER,
            dropdown_fg_color=theme.BG_CARD,
            dropdown_text_color=theme.TEXT_MAIN,
            height=38,
            corner_radius=8,
        )
        self.category_opt.pack(fill="x", pady=(0, 12))

        # 6. Notes
        self._create_field_label(body, "Notes", "Additional notes or reminders")
        self.text_notes = ctk.CTkTextbox(
            body,
            font=("Segoe UI", 12),
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=70,
            corner_radius=8,
        )
        self.text_notes.pack(fill="x", pady=(0, 14))

        # 7. Favorite Switch
        self.fav_var = ctk.BooleanVar(value=False)
        self.fav_switch = ctk.CTkSwitch(
            body,
            text="⭐ Mark as Favorite Contact",
            variable=self.fav_var,
            font=("Segoe UI", 12, "bold"),
            text_color=theme.TEXT_MAIN,
            progress_color=theme.WARNING,
        )
        self.fav_switch.pack(anchor="w", pady=(2, 8))

        # Populate if edit mode
        if self.is_edit_mode and self.contact_data:
            self._populate_fields(self.contact_data)

        # Footer Buttons
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=30, pady=(0, 20))

        btn_cancel = ctk.CTkButton(
            footer,
            text="Cancel",
            font=("Segoe UI", 12, "bold"),
            fg_color=theme.BG_INPUT,
            text_color=theme.TEXT_MAIN,
            hover_color=theme.BORDER_LIGHT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=40,
            width=100,
            corner_radius=8,
            cursor="hand2",
            command=self.destroy,
        )
        btn_cancel.pack(side="right", padx=(10, 0))

        btn_save_text = "Save Changes" if self.is_edit_mode else "Save Contact"
        btn_save = ctk.CTkButton(
            footer,
            text=btn_save_text,
            font=("Segoe UI", 12, "bold"),
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            text_color=theme.TEXT_INVERSE,
            height=40,
            width=130,
            corner_radius=8,
            cursor="hand2",
            command=self._handle_save,
        )
        btn_save.pack(side="right")

    def _create_field_label(self, parent, label_text: str, hint_text: str):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 3))

        lbl = ctk.CTkLabel(
            row,
            text=label_text,
            font=("Segoe UI", 12, "bold"),
            text_color=theme.TEXT_MAIN,
            anchor="w",
        )
        lbl.pack(side="left")

        if hint_text:
            hint = ctk.CTkLabel(
                row,
                text=f"({hint_text})",
                font=("Segoe UI", 10),
                text_color=theme.TEXT_MUTED,
                anchor="w",
            )
            hint.pack(side="left", padx=(6, 0))

    def _populate_fields(self, data: Dict[str, Any]):
        self.entry_name.insert(0, data.get("name", ""))
        self.entry_phone.insert(0, data.get("phone", ""))
        self.entry_email.insert(0, data.get("email", ""))
        self.entry_address.insert(0, data.get("address", ""))

        category = data.get("category", "Work")
        if category in ContactService.VALID_CATEGORIES:
            self.category_var.set(category)
        else:
            self.category_var.set("Other")

        notes = data.get("notes", "")
        if notes:
            self.text_notes.insert("1.0", notes)

        self.fav_var.set(bool(data.get("favorite", False)))

    def _show_error(self, message: str):
        self.lbl_error.configure(text=f"⚠ {message}")
        self.error_frame.pack(fill="x", padx=30, pady=(0, 10), before=self.entry_name.master)

    def _handle_save(self):
        name = self.entry_name.get().strip()
        phone = self.entry_phone.get().strip()
        email = self.entry_email.get().strip()
        address = self.entry_address.get().strip()
        category = self.category_var.get()
        notes = self.text_notes.get("1.0", "end-1c").strip()
        favorite = self.fav_var.get()

        form_dict = {
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "category": category,
            "notes": notes,
            "favorite": favorite,
        }

        if self.is_edit_mode:
            contact_id = self.contact_data.get("id")
            success, msg, updated = self.contact_service.update_contact(contact_id, form_dict)
            if not success:
                self._show_error(msg)
                return
            if self.on_save:
                self.on_save(updated)
            self.destroy()
        else:
            success, msg, created = self.contact_service.add_contact(form_dict)
            if not success:
                self._show_error(msg)
                return
            if self.on_save:
                self.on_save(created)
            self.destroy()
