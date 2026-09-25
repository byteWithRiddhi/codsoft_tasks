"""
Theme and Design Tokens for Connecta
====================================
Defines color palettes for light and dark modes, typography, category badges,
and deterministic avatar color hashing.
"""

import hashlib
from typing import Tuple, Dict

# ---------------------------------------------------------
# COLOR TOKENS (Light Mode / Dark Mode)
# CustomTkinter supports tuple format: (light_color, dark_color)
# ---------------------------------------------------------

# Primary Brand (Indigo)
PRIMARY = ("#4F46E5", "#6366F1")
PRIMARY_HOVER = ("#4338CA", "#4F46E5")
PRIMARY_LIGHT = ("#EEF2FF", "#312E81")

# Backgrounds
BG_APP = ("#F8FAFC", "#0F172A")
BG_SIDEBAR = ("#FFFFFF", "#1E293B")
BG_CARD = ("#FFFFFF", "#1E293B")
BG_CARD_HOVER = ("#F1F5F9", "#334155")
BG_CARD_SELECTED = ("#EEF2FF", "#312E81")
BG_INPUT = ("#F8FAFC", "#0F172A")
BG_HEADER = ("#FFFFFF", "#1E293B")

# Borders & Dividers
BORDER_LIGHT = ("#E2E8F0", "#334155")
BORDER_SUBTLE = ("#F1F5F9", "#1E293B")

# Typography Colors
TEXT_MAIN = ("#0F172A", "#F8FAFC")
TEXT_MUTED = ("#64748B", "#94A3B8")
TEXT_SECONDARY = ("#475569", "#CBD5E1")
TEXT_INVERSE = ("#FFFFFF", "#FFFFFF")

# Semantic States
SUCCESS = ("#10B981", "#34D399")
DANGER = ("#EF4444", "#F87171")
DANGER_HOVER = ("#DC2626", "#EF4444")
WARNING = ("#F59E0B", "#FBBF24")
STAR_ACTIVE = ("#F59E0B", "#FBBF24")
STAR_INACTIVE = ("#CBD5E1", "#475569")

# Category Pill Colors: (bg_light, bg_dark, text_color)
CATEGORY_THEMES: Dict[str, Dict[str, Tuple[str, str]]] = {
    "Work": {
        "bg": ("#DBEAFE", "#1E3A8A"),
        "text": ("#1E40AF", "#93C5FD"),
    },
    "Family": {
        "bg": ("#F3E8FF", "#581C87"),
        "text": ("#6B21A8", "#D8B4FE"),
    },
    "Friends": {
        "bg": ("#D1FAE5", "#064E3B"),
        "text": ("#065F46", "#6EE7B7"),
    },
    "College": {
        "bg": ("#FEF3C7", "#78350F"),
        "text": ("#92400E", "#FDE68A"),
    },
    "Other": {
        "bg": ("#F1F5F9", "#334155"),
        "text": ("#475569", "#CBD5E1"),
    },
}

# Avatar Background Palettes (Consistent, soft, modern tones)
AVATAR_COLORS = [
    "#4F46E5",  # Indigo
    "#0891B2",  # Cyan
    "#059669",  # Emerald
    "#D97706",  # Amber
    "#E11D48",  # Rose
    "#7C3AED",  # Violet
    "#2563EB",  # Royal Blue
    "#0D9488",  # Teal
]


def get_avatar_color(name: str) -> str:
    """Generate a consistent avatar background color based on name hash."""
    if not name:
        return AVATAR_COLORS[0]
    md5_int = int(hashlib.md5(name.strip().lower().encode("utf-8")).hexdigest(), 16)
    return AVATAR_COLORS[md5_int % len(AVATAR_COLORS)]


def get_initials(name: str) -> str:
    """Generate 1 or 2 capital initials from contact name."""
    clean = (name or "").strip()
    if not clean:
        return "?"
    parts = clean.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return clean[:2].upper()
