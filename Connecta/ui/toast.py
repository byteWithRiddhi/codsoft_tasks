"""
Toast Notification Component for Connecta
=========================================
Non-disruptive, auto-dismissing in-app notification banner.
"""

import customtkinter as ctk
from typing import Optional
from . import theme


class ToastManager:
    """Manages displaying non-intrusive toast messages over a parent container."""

    def __init__(self, parent_widget: ctk.CTkFrame):
        self.parent = parent_widget
        self.current_toast: Optional[ctk.CTkFrame] = None
        self._after_id: Optional[str] = None

    def show(self, message: str, level: str = "success", duration_ms: int = 2800):
        """
        Display a toast message.
        Levels: 'success', 'error', 'info', 'warning'
        """
        # Cancel any pending auto-dismiss
        if self._after_id:
            try:
                self.parent.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

        # Remove existing toast if visible
        if self.current_toast:
            try:
                self.current_toast.destroy()
            except Exception:
                pass
            self.current_toast = None

        # Styling according to level
        if level == "success":
            icon = "✓"
            bg_color = ("#ECFDF5", "#064E3B")
            border_color = ("#A7F3D0", "#059669")
            text_color = ("#065F46", "#6EE7B7")
        elif level == "error":
            icon = "✕"
            bg_color = ("#FEF2F2", "#7F1D1D")
            border_color = ("#FECACA", "#DC2626")
            text_color = ("#991B1B", "#FCA5A5")
        elif level == "warning":
            icon = "⚠"
            bg_color = ("#FFFBEB", "#78350F")
            border_color = ("#FDE68A", "#D97706")
            text_color = ("#92400E", "#FDE68A")
        else:  # info
            icon = "ℹ"
            bg_color = ("#EEF2FF", "#312E81")
            border_color = ("#C7D2FE", "#4F46E5")
            text_color = ("#3730A3", "#C7D2FE")

        toast = ctk.CTkFrame(
            self.parent,
            fg_color=bg_color,
            border_color=border_color,
            border_width=1,
            corner_radius=8,
        )
        self.current_toast = toast

        content_box = ctk.CTkFrame(toast, fg_color="transparent")
        content_box.pack(fill="x", padx=14, pady=8)

        lbl_icon = ctk.CTkLabel(
            content_box,
            text=icon,
            font=("Segoe UI", 12, "bold"),
            text_color=text_color,
            width=20,
        )
        lbl_icon.pack(side="left", padx=(0, 8))

        lbl_msg = ctk.CTkLabel(
            content_box,
            text=message,
            font=("Segoe UI", 11, "bold"),
            text_color=text_color,
            anchor="w",
        )
        lbl_msg.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_close = ctk.CTkButton(
            content_box,
            text="✕",
            font=("Segoe UI", 10),
            text_color=text_color,
            fg_color="transparent",
            hover_color=bg_color,
            width=20,
            height=20,
            command=self.dismiss,
            cursor="hand2",
        )
        btn_close.pack(side="right")

        # Place toast at bottom right or top center
        toast.place(relx=0.5, rely=0.04, anchor="n")

        # Auto-dismiss after duration
        self._after_id = self.parent.after(duration_ms, self.dismiss)

    def dismiss(self):
        """Dismiss the current toast notification."""
        if self.current_toast:
            try:
                self.current_toast.destroy()
            except Exception:
                pass
            self.current_toast = None
        self._after_id = None
