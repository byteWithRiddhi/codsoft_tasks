"""
Contact Details Panel for Connecta
==================================
Right-hand preview panel displaying full contact information, large avatar,
category badge, favorite toggle, copy actions, and Edit/Delete triggers.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any, Callable
from . import theme


class ContactDetailsPanel(ctk.CTkFrame):
    """Details panel showing the currently active contact."""

    def __init__(
        self,
        parent,
        on_edit_click: Callable[[Dict[str, Any]], None],
        on_delete_click: Callable[[Dict[str, Any]], None],
        on_favorite_toggle: Callable[[str], None],
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=theme.BG_CARD,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            corner_radius=0,
            **kwargs
        )
        self.on_edit_click = on_edit_click
        self.on_delete_click = on_delete_click
        self.on_favorite_toggle = on_favorite_toggle

        self.current_contact: Optional[Dict[str, Any]] = None

        self._build_ui()

    def _build_ui(self):
        # Container for Empty State
        self.empty_container = ctk.CTkFrame(self, fg_color="transparent")
        self.empty_container.pack(fill="both", expand=True, padx=24, pady=32)

        lbl_icon = ctk.CTkLabel(
            self.empty_container,
            text="👤",
            font=("Segoe UI", 48),
        )
        lbl_icon.pack(pady=(60, 12))

        lbl_head = ctk.CTkLabel(
            self.empty_container,
            text="No Contact Selected",
            font=("Segoe UI", 16, "bold"),
            text_color=theme.TEXT_MAIN,
        )
        lbl_head.pack(pady=(0, 6))

        lbl_desc = ctk.CTkLabel(
            self.empty_container,
            text="Choose a contact from the list to view their complete profile, phone, email, and notes.",
            font=("Segoe UI", 12),
            text_color=theme.TEXT_MUTED,
            wraplength=240,
            justify="center",
        )
        lbl_desc.pack()

        # Container for Contact Profile (Hidden by default)
        self.profile_container = ctk.CTkScrollableFrame(self, fg_color="transparent")

    def show_contact(self, contact: Optional[Dict[str, Any]]):
        """Display contact details or empty state if contact is None."""
        self.current_contact = contact

        # Clean existing profile widgets
        for widget in self.profile_container.winfo_children():
            widget.destroy()

        if not contact:
            self.profile_container.pack_forget()
            self.empty_container.pack(fill="both", expand=True, padx=24, pady=32)
            return

        self.empty_container.pack_forget()
        self.profile_container.pack(fill="both", expand=True, padx=20, pady=20)

        name = contact.get("name", "Unknown Contact")
        initials = theme.get_initials(name)
        avatar_bg = theme.get_avatar_color(name)
        is_favorite = contact.get("favorite", False)
        category = contact.get("category", "Other")

        # Top Avatar + Name Header
        header_card = ctk.CTkFrame(self.profile_container, fg_color="transparent")
        header_card.pack(fill="x", pady=(0, 16))

        # Avatar
        avatar_frame = ctk.CTkFrame(
            header_card,
            width=68,
            height=68,
            corner_radius=34,
            fg_color=avatar_bg,
        )
        avatar_frame.pack_propagate(False)
        avatar_frame.pack(anchor="center", pady=(0, 10))

        lbl_initials = ctk.CTkLabel(
            avatar_frame,
            text=initials,
            font=("Segoe UI", 22, "bold"),
            text_color="#FFFFFF",
        )
        lbl_initials.pack(expand=True)

        # Full Name
        lbl_name = ctk.CTkLabel(
            header_card,
            text=name,
            font=("Segoe UI", 18, "bold"),
            text_color=theme.TEXT_MAIN,
            wraplength=260,
            justify="center",
        )
        lbl_name.pack(anchor="center")

        # Category pill & Favorite badge row
        tag_row = ctk.CTkFrame(header_card, fg_color="transparent")
        tag_row.pack(anchor="center", pady=(6, 12))

        cat_meta = theme.CATEGORY_THEMES.get(category, theme.CATEGORY_THEMES["Other"])
        lbl_cat = ctk.CTkLabel(
            tag_row,
            text=f" {category} ",
            font=("Segoe UI", 11, "bold"),
            fg_color=cat_meta["bg"],
            text_color=cat_meta["text"],
            corner_radius=6,
            padx=8,
            pady=2,
        )
        lbl_cat.pack(side="left", padx=4)

        fav_symbol = "★ Favorite" if is_favorite else "☆ Add Favorite"
        btn_fav = ctk.CTkButton(
            tag_row,
            text=fav_symbol,
            font=("Segoe UI", 11, "bold"),
            fg_color=theme.BG_INPUT,
            text_color=theme.WARNING if is_favorite else theme.TEXT_MUTED,
            hover_color=theme.BORDER_LIGHT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=26,
            corner_radius=6,
            cursor="hand2",
            command=lambda: self.on_favorite_toggle(contact.get("id", "")),
        )
        btn_fav.pack(side="left", padx=4)

        # Action Buttons (Edit / Delete)
        action_bar = ctk.CTkFrame(self.profile_container, fg_color="transparent")
        action_bar.pack(fill="x", pady=(0, 18))

        btn_edit = ctk.CTkButton(
            action_bar,
            text="✏️ Edit Profile",
            font=("Segoe UI", 12, "bold"),
            fg_color=theme.PRIMARY_LIGHT,
            text_color=theme.PRIMARY,
            hover_color=theme.BG_CARD_HOVER,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=36,
            corner_radius=8,
            cursor="hand2",
            command=lambda: self.on_edit_click(contact),
        )
        btn_edit.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_del = ctk.CTkButton(
            action_bar,
            text="🗑️ Delete",
            font=("Segoe UI", 12, "bold"),
            fg_color=("#FEE2E2", "#450A0A"),
            text_color=theme.DANGER,
            hover_color=("#FECACA", "#7F1D1D"),
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=36,
            width=80,
            corner_radius=8,
            cursor="hand2",
            command=lambda: self.on_delete_click(contact),
        )
        btn_del.pack(side="right")

        # Contact Details Card
        info_card = ctk.CTkFrame(
            self.profile_container,
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            corner_radius=10,
        )
        info_card.pack(fill="x", pady=(0, 14))

        # 1. Phone
        phone_val = contact.get("phone", "")
        self._add_detail_row(info_card, "📞 Phone Number", phone_val, allow_copy=True)

        # 2. Email
        email_val = contact.get("email", "")
        self._add_detail_row(info_card, "✉️ Email Address", email_val, allow_copy=bool(email_val))

        # 3. Address
        addr_val = contact.get("address", "")
        self._add_detail_row(info_card, "📍 Physical Address", addr_val, allow_copy=False)

        # 4. Notes
        notes_val = contact.get("notes", "")
        if notes_val:
            self._add_detail_row(info_card, "📝 Notes", notes_val, allow_copy=False)

        # 5. Added on
        date_val = contact.get("created_at", "")
        if date_val:
            self._add_detail_row(info_card, "📅 Date Added", date_val, allow_copy=False, is_last=True)

    def _add_detail_row(
        self,
        parent: ctk.CTkFrame,
        label: str,
        value: str,
        allow_copy: bool = False,
        is_last: bool = False
    ):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(fill="x", padx=14, pady=(10, 10))

        # Label
        lbl_title = ctk.CTkLabel(
            box,
            text=label,
            font=("Segoe UI", 10, "bold"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        lbl_title.pack(anchor="w")

        # Value row
        val_row = ctk.CTkFrame(box, fg_color="transparent")
        val_row.pack(fill="x", pady=(2, 0))

        display_text = value if value else "Not provided"
        text_color = theme.TEXT_MAIN if value else theme.TEXT_MUTED

        lbl_val = ctk.CTkLabel(
            val_row,
            text=display_text,
            font=("Segoe UI", 12 if value else 11),
            text_color=text_color,
            anchor="w",
            wraplength=220,
            justify="left",
        )
        lbl_val.pack(side="left", fill="x", expand=True)

        if allow_copy and value:
            btn_copy = ctk.CTkButton(
                val_row,
                text="Copy",
                font=("Segoe UI", 9, "bold"),
                fg_color=theme.BG_CARD,
                text_color=theme.PRIMARY,
                hover_color=theme.PRIMARY_LIGHT,
                border_color=theme.BORDER_LIGHT,
                border_width=1,
                width=42,
                height=22,
                corner_radius=4,
                cursor="hand2",
                command=lambda v=value: self._copy_to_clipboard(v),
            )
            btn_copy.pack(side="right")

        if not is_last:
            sep = ctk.CTkFrame(parent, height=1, fg_color=theme.BORDER_LIGHT)
            sep.pack(fill="x", padx=14)

    def _copy_to_clipboard(self, text: str):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()
        except Exception:
            pass
