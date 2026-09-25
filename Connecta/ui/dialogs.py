"""
Dialog Components for Connecta
==============================
Styled modal dialogs including deletion confirmations.
"""

import customtkinter as ctk
from typing import Callable, Optional
from . import theme


class ConfirmDeleteDialog(ctk.CTkToplevel):
    """Modern modal confirmation dialog for contact deletion."""

    def __init__(
        self,
        parent: ctk.CTk,
        contact_name: str,
        on_confirm: Callable[[], None],
        on_cancel: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent)
        self.title("Confirm Deletion")
        self.geometry("420x240")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.configure(fg_color=theme.BG_CARD)
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        # Center over parent
        self._center_window(parent, 420, 240)

        # Layout
        self._build_ui(contact_name)

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

    def _build_ui(self, contact_name: str):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=26, pady=22)

        # Top icon and heading
        top_row = ctk.CTkFrame(container, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))

        icon_badge = ctk.CTkLabel(
            top_row,
            text="⚠️",
            font=("Segoe UI", 20),
            width=36,
            height=36,
            fg_color=("rgba(239, 68, 68, 0.1)", "rgba(239, 68, 68, 0.2)"),
            corner_radius=18,
        )
        icon_badge.pack(side="left", padx=(0, 12))

        title_box = ctk.CTkFrame(top_row, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True)

        lbl_title = ctk.CTkLabel(
            title_box,
            text="Delete Contact?",
            font=("Segoe UI", 16, "bold"),
            text_color=theme.TEXT_MAIN,
            anchor="w",
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box,
            text="This action is permanent and cannot be undone.",
            font=("Segoe UI", 11),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        lbl_sub.pack(anchor="w")

        # Contact info highlight box
        info_card = ctk.CTkFrame(
            container,
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            corner_radius=8,
        )
        info_card.pack(fill="x", pady=(8, 18))

        lbl_target = ctk.CTkLabel(
            info_card,
            text=f"Delete '{contact_name}' from your contact book?",
            font=("Segoe UI", 12, "bold"),
            text_color=theme.TEXT_MAIN,
            wraplength=340,
            justify="left",
        )
        lbl_target.pack(padx=14, pady=10, anchor="w")

        # Action buttons
        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(fill="x")

        btn_cancel = ctk.CTkButton(
            btn_box,
            text="Cancel",
            font=("Segoe UI", 12, "bold"),
            fg_color=theme.BG_INPUT,
            text_color=theme.TEXT_MAIN,
            hover_color=theme.BORDER_LIGHT,
            border_color=theme.BORDER_LIGHT,
            border_width=1,
            height=36,
            width=100,
            corner_radius=8,
            cursor="hand2",
            command=self._cancel,
        )
        btn_cancel.pack(side="right", padx=(10, 0))

        btn_delete = ctk.CTkButton(
            btn_box,
            text="Delete Contact",
            font=("Segoe UI", 12, "bold"),
            fg_color=theme.DANGER,
            hover_color=theme.DANGER_HOVER,
            text_color=theme.TEXT_INVERSE,
            height=36,
            corner_radius=8,
            cursor="hand2",
            command=self._confirm,
        )
        btn_delete.pack(side="right")

    def _cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.destroy()

    def _confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.destroy()
