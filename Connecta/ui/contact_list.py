"""
Contact List View for Connecta
==============================
Main view containing dashboard stat chips, real-time multi-field search,
sorting controls, scrollable card-based contact rows, and polished empty states.
"""

import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional
from . import theme


class ContactListView(ctk.CTkFrame):
    """Middle main content area managing contact search, cards, and empty states."""

    def __init__(
        self,
        parent,
        on_select_contact: Callable[[Dict[str, Any]], None],
        on_favorite_toggle: Callable[[str], None],
        on_add_contact_click: Callable[[], None],
        on_search_or_sort_change: Callable[[], None],
        **kwargs
    ):
        super().__init__(parent, fg_color=theme.BG_APP, corner_radius=0, **kwargs)

        self.on_select_contact = on_select_contact
        self.on_favorite_toggle = on_favorite_toggle
        self.on_add_contact_click = on_add_contact_click
        self.on_search_or_sort_change = on_search_or_sort_change

        self.selected_contact_id: Optional[str] = None
        self.card_widgets: Dict[str, ctk.CTkFrame] = {}

        self._build_ui()

    def _build_ui(self):
        # 1. Top Header Area
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=24, pady=(22, 12))

        title_row = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_row.pack(fill="x")

        self.lbl_title = ctk.CTkLabel(
            title_row,
            text="All Contacts",
            font=("Segoe UI", 22, "bold"),
            text_color=theme.TEXT_MAIN,
        )
        self.lbl_title.pack(side="left")

        self.lbl_count_badge = ctk.CTkLabel(
            title_row,
            text="0 contacts",
            font=("Segoe UI", 11, "bold"),
            fg_color=theme.PRIMARY_LIGHT,
            text_color=theme.PRIMARY,
            corner_radius=12,
            padx=10,
            pady=2,
        )
        self.lbl_count_badge.pack(side="left", padx=(10, 0))

        self.lbl_subtitle = ctk.CTkLabel(
            self.header_frame,
            text="Manage your personal and professional network.",
            font=("Segoe UI", 11),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        self.lbl_subtitle.pack(anchor="w", pady=(2, 8))

        # Stat Summary Chips
        self.stats_row = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.stats_row.pack(fill="x", pady=(2, 6))

        self.chip_total = self._create_stat_chip(self.stats_row, "👥 Total", "0")
        self.chip_favs = self._create_stat_chip(self.stats_row, "⭐ Favorites", "0")
        self.chip_email = self._create_stat_chip(self.stats_row, "✉️ With Email", "0")
        self.chip_phone = self._create_stat_chip(self.stats_row, "📞 With Phone", "0")

        # 2. Search and Filter Bar
        controls_card = ctk.CTkFrame(
            self,
            fg_color=theme.BG_CARD,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            corner_radius=10,
        )
        controls_card.pack(fill="x", padx=24, pady=(0, 14))

        controls_inner = ctk.CTkFrame(controls_card, fg_color="transparent")
        controls_inner.pack(fill="x", padx=12, pady=10)

        lbl_search_icon = ctk.CTkLabel(
            controls_inner,
            text="🔍",
            font=("Segoe UI", 13),
        )
        lbl_search_icon.pack(side="left", padx=(0, 6))

        # Real-time search entry
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.on_search_or_sort_change())

        self.search_entry = ctk.CTkEntry(
            controls_inner,
            textvariable=self.search_var,
            placeholder_text="Search by name, phone, email, address...",
            font=("Segoe UI", 12),
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=36,
            corner_radius=8,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_clear = ctk.CTkButton(
            controls_inner,
            text="Clear",
            font=("Segoe UI", 11),
            fg_color=theme.BG_INPUT,
            text_color=theme.TEXT_SECONDARY,
            hover_color=theme.BORDER_LIGHT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            width=54,
            height=34,
            corner_radius=6,
            cursor="hand2",
            command=self.clear_search,
        )
        self.btn_clear.pack(side="left", padx=(0, 10))

        # Sort dropdown
        lbl_sort = ctk.CTkLabel(
            controls_inner,
            text="Sort:",
            font=("Segoe UI", 11, "bold"),
            text_color=theme.TEXT_MUTED,
        )
        lbl_sort.pack(side="left", padx=(0, 6))

        self.sort_var = ctk.StringVar(value="Name: A–Z")
        self.sort_menu = ctk.CTkOptionMenu(
            controls_inner,
            values=["Name: A–Z", "Name: Z–A", "Recently Added", "Oldest First"],
            variable=self.sort_var,
            command=lambda val: self.on_search_or_sort_change(),
            font=("Segoe UI", 11),
            fg_color=theme.BG_INPUT,
            text_color=theme.TEXT_MAIN,
            button_color=theme.PRIMARY,
            button_hover_color=theme.PRIMARY_HOVER,
            dropdown_fg_color=theme.BG_CARD,
            dropdown_text_color=theme.TEXT_MAIN,
            height=34,
            width=135,
            corner_radius=8,
        )
        self.sort_menu.pack(side="right")

        # 3. Scrollable List of Contact Cards
        self.scroll_list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_list.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # 4. Empty State Container
        self.empty_container = ctk.CTkFrame(self, fg_color="transparent")

    def _create_stat_chip(self, parent, label: str, value: str) -> ctk.CTkLabel:
        chip = ctk.CTkFrame(
            parent,
            fg_color=theme.BG_CARD,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            corner_radius=8,
            height=28,
        )
        chip.pack(side="left", padx=(0, 8))

        lbl = ctk.CTkLabel(
            chip,
            text=f"{label}: {value}",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.TEXT_SECONDARY,
            padx=10,
            pady=4,
        )
        lbl.pack()
        return lbl

    def update_statistics(self, stats: Dict[str, Any]):
        """Update stat chips values."""
        self.chip_total.configure(text=f"👥 Total: {stats.get('total', 0)}")
        self.chip_favs.configure(text=f"⭐ Favorites: {stats.get('favorites', 0)}")
        self.chip_email.configure(text=f"✉️ Email: {stats.get('with_email', 0)}")
        self.chip_phone.configure(text=f"📞 Phone: {stats.get('with_phone', 0)}")

    def set_header_title(self, title: str, subtitle: str = ""):
        self.lbl_title.configure(text=title)
        if subtitle:
            self.lbl_subtitle.configure(text=subtitle)

    def clear_search(self):
        self.search_var.set("")

    def get_search_query(self) -> str:
        return self.search_var.get().strip()

    def get_sort_by(self) -> str:
        return self.sort_var.get()

    def render_contacts(
        self,
        contacts: List[Dict[str, Any]],
        active_view: str,
        selected_id: Optional[str] = None
    ):
        """Render contact cards or appropriate empty state."""
        self.selected_contact_id = selected_id
        self.card_widgets.clear()

        # Update count badge
        count = len(contacts)
        self.lbl_count_badge.configure(text=f"{count} contact{'s' if count != 1 else ''}")

        # Clear scrollable container
        for child in self.scroll_list.winfo_children():
            child.destroy()

        # Check for empty states
        if not contacts:
            self.scroll_list.pack_forget()
            self._render_empty_state(active_view)
            return

        # Hide empty state and show scroll list
        self.empty_container.pack_forget()
        self.scroll_list.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        for contact in contacts:
            self._render_contact_card(contact)

    def _render_contact_card(self, contact: Dict[str, Any]):
        cid = contact.get("id", "")
        name = contact.get("name", "Unknown Contact")
        phone = contact.get("phone", "")
        email = contact.get("email", "")
        category = contact.get("category", "Other")
        is_favorite = contact.get("favorite", False)

        is_selected = (cid == self.selected_contact_id)
        card_bg = theme.BG_CARD_SELECTED if is_selected else theme.BG_CARD
        card_border = theme.PRIMARY if is_selected else theme.BORDER_LIGHT
        border_w = 2 if is_selected else 1

        card = ctk.CTkFrame(
            self.scroll_list,
            fg_color=card_bg,
            border_color=card_border,
            border_width=border_w,
            corner_radius=10,
            cursor="hand2",
        )
        card.pack(fill="x", pady=4)
        self.card_widgets[cid] = card

        # Click on card triggers selection
        card.bind("<Button-1>", lambda event, c=contact: self.on_select_contact(c))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)
        inner.bind("<Button-1>", lambda event, c=contact: self.on_select_contact(c))

        # Avatar initials badge
        avatar_bg = theme.get_avatar_color(name)
        initials = theme.get_initials(name)
        avatar = ctk.CTkFrame(
            inner,
            width=42,
            height=42,
            corner_radius=21,
            fg_color=avatar_bg,
        )
        avatar.pack_propagate(False)
        avatar.pack(side="left", padx=(0, 12))
        avatar.bind("<Button-1>", lambda event, c=contact: self.on_select_contact(c))

        lbl_init = ctk.CTkLabel(
            avatar,
            text=initials,
            font=("Segoe UI", 13, "bold"),
            text_color="#FFFFFF",
        )
        lbl_init.pack(expand=True)
        lbl_init.bind("<Button-1>", lambda event, c=contact: self.on_select_contact(c))

        # Details middle block
        info_col = ctk.CTkFrame(inner, fg_color="transparent")
        info_col.pack(side="left", fill="x", expand=True)
        info_col.bind("<Button-1>", lambda event, c=contact: self.on_select_contact(c))

        # Row 1: Name + Category Pill
        row1 = ctk.CTkFrame(info_col, fg_color="transparent")
        row1.pack(fill="x")
        row1.bind("<Button-1>", lambda event, c=contact: self.on_select_contact(c))

        lbl_name = ctk.CTkLabel(
            row1,
            text=name,
            font=("Segoe UI", 13, "bold"),
            text_color=theme.TEXT_MAIN,
            anchor="w",
        )
        lbl_name.pack(side="left")
        lbl_name.bind("<Button-1>", lambda event, c=contact: self.on_select_contact(c))

        # Category Badge
        cat_meta = theme.CATEGORY_THEMES.get(category, theme.CATEGORY_THEMES["Other"])
        lbl_cat = ctk.CTkLabel(
            row1,
            text=f" {category} ",
            font=("Segoe UI", 9, "bold"),
            fg_color=cat_meta["bg"],
            text_color=cat_meta["text"],
            corner_radius=4,
            padx=6,
            pady=1,
        )
        lbl_cat.pack(side="left", padx=(8, 0))
        lbl_cat.bind("<Button-1>", lambda event, c=contact: self.on_select_contact(c))

        # Row 2: Phone & Email preview
        row2 = ctk.CTkFrame(info_col, fg_color="transparent")
        row2.pack(fill="x", pady=(2, 0))
        row2.bind("<Button-1>", lambda event, c=contact: self.on_select_contact(c))

        lbl_phone = ctk.CTkLabel(
            row2,
            text=f"📞 {phone}",
            font=("Segoe UI", 11),
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        lbl_phone.pack(side="left", padx=(0, 12))
        lbl_phone.bind("<Button-1>", lambda event, c=contact: self.on_select_contact(c))

        if email:
            lbl_email = ctk.CTkLabel(
                row2,
                text=f"✉️ {email}",
                font=("Segoe UI", 11),
                text_color=theme.TEXT_MUTED,
                anchor="w",
            )
            lbl_email.pack(side="left")
            lbl_email.bind("<Button-1>", lambda event, c=contact: self.on_select_contact(c))

        # Right Favorite Star Toggle Button
        star_char = "★" if is_favorite else "☆"
        star_color = theme.WARNING if is_favorite else theme.TEXT_MUTED

        btn_star = ctk.CTkButton(
            inner,
            text=star_char,
            font=("Segoe UI", 16, "bold"),
            fg_color="transparent",
            text_color=star_color,
            hover_color=theme.BG_CARD_HOVER,
            width=34,
            height=34,
            corner_radius=17,
            cursor="hand2",
            command=lambda c_id=cid: self.on_favorite_toggle(c_id),
        )
        btn_star.pack(side="right", padx=(8, 0))

    def _render_empty_state(self, active_view: str):
        """Display an expressive empty state depending on current view/search."""
        for child in self.empty_container.winfo_children():
            child.destroy()

        self.empty_container.pack(fill="both", expand=True, padx=24, pady=40)

        query = self.get_search_query()

        if query:
            icon = "🔍"
            heading = "No contacts match your search"
            subtext = f"We couldn't find any contacts matching '{query}'. Try another search term."
            cta_text = "Clear Search Filter"
            cta_cmd = self.clear_search
        elif active_view == "favorites":
            icon = "⭐"
            heading = "No favorite contacts yet"
            subtext = "Star contacts to pin them here for fast, one-click access."
            cta_text = "+ Add a Contact"
            cta_cmd = self.on_add_contact_click
        elif active_view.startswith("category:"):
            cat_name = active_view.split("category:", 1)[1]
            icon = "📁"
            heading = f"No {cat_name} contacts found"
            subtext = f"You haven't added any contacts under the '{cat_name}' category yet."
            cta_text = f"+ Add {cat_name} Contact"
            cta_cmd = self.on_add_contact_click
        else:
            icon = "📇"
            heading = "No contacts yet"
            subtext = "Start building your personal contact list. All your contacts will appear here."
            cta_text = "+ Add Your First Contact"
            cta_cmd = self.on_add_contact_click

        card = ctk.CTkFrame(
            self.empty_container,
            fg_color=theme.BG_CARD,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            corner_radius=12,
        )
        card.pack(fill="both", expand=True, padx=20, pady=20)

        box = ctk.CTkFrame(card, fg_color="transparent")
        box.place(relx=0.5, rely=0.5, anchor="center")

        lbl_icon = ctk.CTkLabel(
            box,
            text=icon,
            font=("Segoe UI", 42),
        )
        lbl_icon.pack(pady=(0, 10))

        lbl_head = ctk.CTkLabel(
            box,
            text=heading,
            font=("Segoe UI", 16, "bold"),
            text_color=theme.TEXT_MAIN,
        )
        lbl_head.pack(pady=(0, 6))

        lbl_desc = ctk.CTkLabel(
            box,
            text=subtext,
            font=("Segoe UI", 12),
            text_color=theme.TEXT_MUTED,
            wraplength=320,
            justify="center",
        )
        lbl_desc.pack(pady=(0, 16))

        btn_cta = ctk.CTkButton(
            box,
            text=cta_text,
            font=("Segoe UI", 12, "bold"),
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            text_color=theme.TEXT_INVERSE,
            height=38,
            corner_radius=8,
            cursor="hand2",
            command=cta_cmd,
        )
        btn_cta.pack()
