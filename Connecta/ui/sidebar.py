"""
Sidebar Navigation Component for Connecta
=========================================
Clean vertical navigation sidebar with application branding, live counter badges,
category filters, theme switch, and Add Contact CTA.
"""

import customtkinter as ctk
from typing import Callable, Dict, Any, List
from . import theme
try:
    from services.contact_service import ContactService
except ImportError:
    from ..services.contact_service import ContactService


class Sidebar(ctk.CTkFrame):
    """Vertical navigation sidebar."""

    def __init__(
        self,
        parent,
        on_view_change: Callable[[str], None],
        on_add_click: Callable[[], None],
        on_theme_toggle: Callable[[], None],
        **kwargs
    ):
        super().__init__(parent, fg_color=theme.BG_SIDEBAR, width=240, corner_radius=0, **kwargs)
        self.pack_propagate(False)

        self.on_view_change = on_view_change
        self.on_add_click = on_add_click
        self.on_theme_toggle = on_theme_toggle

        self.active_view = "all"
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}

        self._build_ui()

    def _build_ui(self):
        # Top Branding
        brand_box = ctk.CTkFrame(self, fg_color="transparent")
        brand_box.pack(fill="x", padx=18, pady=(24, 16))

        logo_row = ctk.CTkFrame(brand_box, fg_color="transparent")
        logo_row.pack(anchor="w")

        lbl_logo = ctk.CTkLabel(
            logo_row,
            text="📇",
            font=("Segoe UI", 22),
        )
        lbl_logo.pack(side="left", padx=(0, 8))

        lbl_name = ctk.CTkLabel(
            logo_row,
            text="Connecta",
            font=("Segoe UI", 18, "bold"),
            text_color=theme.TEXT_MAIN,
        )
        lbl_name.pack(side="left")

        lbl_tagline = ctk.CTkLabel(
            brand_box,
            text="Your contacts, beautifully organized.",
            font=("Segoe UI", 10),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        lbl_tagline.pack(anchor="w", pady=(2, 0))

        # Divider
        divider = ctk.CTkFrame(self, height=1, fg_color=theme.BORDER_LIGHT)
        divider.pack(fill="x", padx=16, pady=(0, 14))

        # Main Navigation Items
        self.nav_box = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_box.pack(fill="x", padx=14, pady=0)

        self._add_nav_item("all", "👥", "All Contacts")
        self._add_nav_item("favorites", "⭐", "Favorites")
        self._add_nav_item("recent", "🕒", "Recently Added")

        # Category Group Header
        lbl_cat = ctk.CTkLabel(
            self,
            text="CATEGORIES",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        lbl_cat.pack(anchor="w", padx=22, pady=(16, 6))

        # Category items
        cat_icons = {
            "Work": "💼",
            "Family": "🏠",
            "Friends": "🤝",
            "College": "🎓",
            "Other": "📁",
        }
        for cat in ContactService.VALID_CATEGORIES:
            icon = cat_icons.get(cat, "📁")
            self._add_nav_item(f"category:{cat}", icon, cat)

        # Bottom Area
        bottom_box = ctk.CTkFrame(self, fg_color="transparent")
        bottom_box.pack(side="bottom", fill="x", padx=16, pady=20)

        # Theme Toggle Button
        self.btn_theme = ctk.CTkButton(
            bottom_box,
            text="🌓 Toggle Theme",
            font=("Segoe UI", 11),
            fg_color=theme.BG_INPUT,
            text_color=theme.TEXT_MAIN,
            hover_color=theme.BORDER_LIGHT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=34,
            corner_radius=8,
            cursor="hand2",
            command=self.on_theme_toggle,
        )
        self.btn_theme.pack(fill="x", pady=(0, 10))

        # Add Contact CTA
        btn_add = ctk.CTkButton(
            bottom_box,
            text="+ Add Contact",
            font=("Segoe UI", 13, "bold"),
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            text_color=theme.TEXT_INVERSE,
            height=42,
            corner_radius=8,
            cursor="hand2",
            command=self.on_add_click,
        )
        btn_add.pack(fill="x")

        # Set initial active view style
        self.set_active_view("all")

    def _add_nav_item(self, view_id: str, icon: str, label: str):
        btn = ctk.CTkButton(
            self.nav_box,
            text=f"  {icon}  {label}",
            anchor="w",
            font=("Segoe UI", 12),
            fg_color="transparent",
            text_color=theme.TEXT_MAIN,
            hover_color=theme.BG_CARD_HOVER,
            height=36,
            corner_radius=8,
            cursor="hand2",
            command=lambda v=view_id: self._select_view(v),
        )
        btn.pack(fill="x", pady=2)
        self.nav_buttons[view_id] = btn

    def _select_view(self, view_id: str):
        self.set_active_view(view_id)
        self.on_view_change(view_id)

    def set_active_view(self, view_id: str):
        self.active_view = view_id
        for vid, btn in self.nav_buttons.items():
            if vid == view_id:
                btn.configure(
                    fg_color=theme.PRIMARY_LIGHT,
                    text_color=theme.PRIMARY,
                    font=("Segoe UI", 12, "bold"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=theme.TEXT_MAIN,
                    font=("Segoe UI", 12),
                )

    def update_badge_counts(self, stats: Dict[str, Any]):
        """Update navigation item labels with live counts."""
        total = stats.get("total", 0)
        favorites = stats.get("favorites", 0)
        categories = stats.get("categories", {})

        if "all" in self.nav_buttons:
            self.nav_buttons["all"].configure(text=f"  👥  All Contacts  ({total})")

        if "favorites" in self.nav_buttons:
            self.nav_buttons["favorites"].configure(text=f"  ⭐  Favorites  ({favorites})")

        cat_icons = {
            "Work": "💼",
            "Family": "🏠",
            "Friends": "🤝",
            "College": "🎓",
            "Other": "📁",
        }
        for cat, icon in cat_icons.items():
            vid = f"category:{cat}"
            if vid in self.nav_buttons:
                cnt = categories.get(cat, 0)
                self.nav_buttons[vid].configure(text=f"  {icon}  {cat}  ({cnt})")
