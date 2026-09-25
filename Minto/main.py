#!/usr/bin/env python3
"""
MINTO - Personal Task Manager
Tagline: "Plan it. Do it. Done."

A modern, aesthetic, cozy, and lightweight desktop To-Do List application.
Built using Python 3 and Tkinter (Python Standard Library).
"""

import os
import sys
import json
from datetime import date, datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

# Reconfigure stdout/stderr for unicode console logging on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Enable High-DPI awareness on Windows for crisp typography
if sys.platform.startswith("win"):
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# ==============================================================================
# DESIGN SYSTEM & COLOR PALETTE
# Cozy, minimal, sage green and warm linen aesthetic
# ==============================================================================

COLORS = {
    # Base Application
    "bg_app": "#F5F3ED",            # Soft warm linen background
    "bg_card": "#FFFFFF",           # Card background
    "bg_card_hover": "#FCFBF8",     # Card subtle hover
    "bg_card_completed": "#FAF8F5", # Soft completed background
    "border": "#E5E1D5",            # Warm soft border
    "border_completed": "#ECE9E1",  # Subtle completed border
    
    # Primary Accent (Sage / Matcha Green)
    "primary": "#4A6F52",           # Signature Sage Green
    "primary_hover": "#3D5D44",     # Deeper sage for hover
    "primary_light": "#EDF4EE",     # Very soft sage tint
    "primary_fg": "#FFFFFF",        # White text for primary buttons
    
    # Typography
    "text_main": "#243026",         # Deep woodland charcoal
    "text_muted": "#6E7B70",        # Muted sage-gray for secondary text
    "text_light": "#9BA69D",        # Subtle gray for placeholders/dates
    "text_completed": "#A0ABA2",    # Faded gray for completed tasks
    
    # Progress Bar
    "progress_track": "#E4DFD5",    # Neutral cream track
    "progress_fill": "#4A6F52",     # Sage fill
    
    # Priority Badges (Dot, Background, Foreground)
    "prio_high_dot": "#E25A48",
    "prio_high_bg": "#FDF0ED",
    "prio_high_fg": "#C8412F",
    
    "prio_med_dot": "#E2931D",
    "prio_med_bg": "#FEF5E7",
    "prio_med_fg": "#B5700A",
    
    "prio_low_dot": "#4C9A66",
    "prio_low_bg": "#EDF7EF",
    "prio_low_fg": "#37774B",
    
    # Category Badges (Background, Foreground)
    "cat_general_bg": "#F0F2F4",
    "cat_general_fg": "#4C5B6B",
    
    "cat_study_bg": "#EDF2FE",
    "cat_study_fg": "#345EC7",
    
    "cat_work_bg": "#F4EDFD",
    "cat_work_fg": "#7539BE",
    
    "cat_personal_bg": "#FDF1E8",
    "cat_personal_fg": "#C85822",
    
    "cat_project_bg": "#E3F6F3",
    "cat_project_fg": "#1C8273",
    
    # Due Date Badges
    "due_today_bg": "#EDF6EE",
    "due_today_fg": "#2F6E3F",
    
    "due_tomorrow_bg": "#F5F3EC",
    "due_tomorrow_fg": "#676357",
    
    "due_overdue_bg": "#FCECE9",
    "due_overdue_fg": "#C83B2B",
    
    # Danger & Action Buttons
    "danger": "#D9534F",
    "danger_hover": "#C9302C",
    "danger_bg": "#FDF0EE",
    "danger_fg": "#C83B2B",
    
    "action_bg": "#F4F2EB",
    "action_hover": "#E9E6DC",
    "action_fg": "#49564B",
}

FONT_FAMILY = "Segoe UI" if sys.platform.startswith("win") else "Helvetica"


def get_font(size=10, weight="normal", slant="roman", underline=False, overstrike=False):
    """Utility to build a consistent font tuple or dict."""
    return (FONT_FAMILY, size, weight)


# ==============================================================================
# DATA LAYER - TASK MANAGER
# Handles JSON persistence, CRUD, search, filter, and progress stats
# ==============================================================================

class TaskManager:
    """Manages task data lifecycle with JSON persistence."""

    def __init__(self, filepath="tasks.json"):
        self.filepath = filepath
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Loads tasks from JSON. Recovers gracefully if file is corrupt or missing."""
        if not os.path.exists(self.filepath):
            self.tasks = self._get_default_tasks()
            self.save_tasks()
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.tasks = data
                else:
                    self.tasks = self._get_default_tasks()
                    self.save_tasks()
        except (json.JSONDecodeError, OSError):
            self.tasks = self._get_default_tasks()
            self.save_tasks()

    def save_tasks(self):
        """Saves current task list to JSON file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=4, ensure_ascii=False)
        except OSError as e:
            print(f"Error saving tasks: {e}", file=sys.stderr)

    def _get_default_tasks(self):
        """Default seed tasks matching user specification."""
        today_str = date.today().isoformat()
        tomorrow_str = (date.today() + timedelta(days=1)).isoformat()
        future_str = (date.today() + timedelta(days=3)).isoformat()

        return [
            {
                "id": 1,
                "title": "Complete Java assignment",
                "description": "Finish inheritance and interface questions",
                "due_date": today_str,
                "priority": "High",
                "category": "Study",
                "completed": False
            },
            {
                "id": 2,
                "title": "Submit internship task",
                "description": "Review final checklist and upload repository link",
                "due_date": today_str,
                "priority": "Medium",
                "category": "Work",
                "completed": True
            },
            {
                "id": 3,
                "title": "Study for NPTEL",
                "description": "Watch Week 4 lecture videos and make summary notes",
                "due_date": tomorrow_str,
                "priority": "Medium",
                "category": "Study",
                "completed": False
            },
            {
                "id": 4,
                "title": "Work on project documentation",
                "description": "Write system design section and component breakdown",
                "due_date": future_str,
                "priority": "Low",
                "category": "Project",
                "completed": False
            }
        ]

    def _get_next_id(self):
        if not self.tasks:
            return 1
        return max(t.get("id", 0) for t in self.tasks) + 1

    def add_task(self, title, description="", due_date="", priority="Medium", category="General"):
        title = title.strip()
        if not title:
            raise ValueError("Task title is required.")

        task = {
            "id": self._get_next_id(),
            "title": title,
            "description": description.strip(),
            "due_date": due_date.strip(),
            "priority": priority if priority in ["Low", "Medium", "High"] else "Medium",
            "category": category if category in ["General", "Study", "Work", "Personal", "Project"] else "General",
            "completed": False
        }
        self.tasks.append(task)
        self.save_tasks()
        return task

    def update_task(self, task_id, title, description="", due_date="", priority="Medium", category="General"):
        title = title.strip()
        if not title:
            raise ValueError("Task title is required.")

        for task in self.tasks:
            if task.get("id") == task_id:
                task["title"] = title
                task["description"] = description.strip()
                task["due_date"] = due_date.strip()
                task["priority"] = priority if priority in ["Low", "Medium", "High"] else "Medium"
                task["category"] = category if category in ["General", "Study", "Work", "Personal", "Project"] else "General"
                self.save_tasks()
                return task
        return None

    def delete_task(self, task_id):
        initial_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.get("id") != task_id]
        if len(self.tasks) < initial_count:
            self.save_tasks()
            return True
        return False

    def toggle_completed(self, task_id):
        for task in self.tasks:
            if task.get("id") == task_id:
                task["completed"] = not task.get("completed", False)
                self.save_tasks()
                return task.get("completed")
        return None

    def get_task(self, task_id):
        for task in self.tasks:
            if task.get("id") == task_id:
                return task
        return None

    def get_filtered_tasks(self, query="", filter_mode="All"):
        today_str = date.today().isoformat()
        results = []
        q = query.strip().lower()

        for task in self.tasks:
            is_completed = task.get("completed", False)
            task_due = task.get("due_date", "")

            # Filter Mode
            if filter_mode == "Active" and is_completed:
                continue
            if filter_mode == "Completed" and not is_completed:
                continue
            if filter_mode == "Today" and task_due != today_str:
                continue

            # Search Query
            if q:
                title = task.get("title", "").lower()
                desc = task.get("description", "").lower()
                cat = task.get("category", "").lower()
                if q not in title and q not in desc and q not in cat:
                    continue

            results.append(task)
        return results

    def get_progress_stats(self):
        total = len(self.tasks)
        if total == 0:
            return {
                "total": 0,
                "completed": 0,
                "remaining": 0,
                "percentage": 0,
                "message": "Your day is clear ✨"
            }

        completed = sum(1 for t in self.tasks if t.get("completed", False))
        remaining = total - completed
        percentage = round((completed / total) * 100)

        if percentage == 0:
            message = "Let's get started."
        elif percentage < 50:
            message = "You're making progress."
        elif percentage < 100:
            message = "Keep going!"
        else:
            message = "Everything's done. Nice work! ✨"

        return {
            "total": total,
            "completed": completed,
            "remaining": remaining,
            "percentage": percentage,
            "message": message
        }

    @staticmethod
    def format_due_date(due_date_str):
        """Returns tuple of (formatted_string, is_overdue, badge_type)."""
        if not due_date_str:
            return None, False, "none"

        try:
            due = date.fromisoformat(due_date_str)
            today = date.today()
            diff = (due - today).days

            if diff < 0:
                return "⚠ Overdue", True, "overdue"
            elif diff == 0:
                return "📅 Today", False, "today"
            elif diff == 1:
                return "📅 Tomorrow", False, "tomorrow"
            else:
                return f"📅 {due.strftime('%b %d')}", False, "normal"
        except (ValueError, TypeError):
            return f"📅 {due_date_str}", False, "normal"


# ==============================================================================
# CUSTOM UI WIDGETS
# Custom Canvas-based Checkbox, Smooth Progress Bar, and Badges
# ==============================================================================

class SmoothProgressBar(tk.Canvas):
    """A clean, rounded aesthetic progress bar drawn on a Canvas."""

    def __init__(self, parent, height=14, **kwargs):
        super().__init__(
            parent,
            height=height,
            bg=COLORS["bg_card"],
            highlightthickness=0,
            **kwargs
        )
        self.height = height
        self.percentage = 0
        self.bind("<Configure>", self._on_resize)

    def set_progress(self, percentage):
        self.percentage = max(0, min(100, percentage))
        self._draw()

    def _on_resize(self, event=None):
        self._draw()

    def _draw(self):
        self.delete("all")
        width = self.winfo_width()
        height = self.height
        if width <= 10:
            return

        radius = height // 2
        track_color = COLORS["progress_track"]
        fill_color = COLORS["progress_fill"]

        # 1. Draw rounded background track
        self._draw_pill(0, 0, width, height, radius, track_color)

        # 2. Draw progress fill
        if self.percentage > 0:
            fill_width = max(height, int(width * (self.percentage / 100.0)))
            fill_width = min(width, fill_width)
            self._draw_pill(0, 0, fill_width, height, radius, fill_color)

    def _draw_pill(self, x1, y1, x2, y2, r, fill):
        if x2 - x1 < 2 * r:
            self.create_oval(x1, y1, x2, y2, fill=fill, outline="")
            return

        # Left arc, right arc, and center rect
        self.create_arc(x1, y1, x1 + 2 * r, y2, start=90, extent=180, fill=fill, outline="")
        self.create_arc(x2 - 2 * r, y1, x2, y2, start=270, extent=180, fill=fill, outline="")
        self.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline="")


class CustomCheckbox(tk.Canvas):
    """A cozy rounded checkbox that smoothly reflects completed state."""

    def __init__(self, parent, checked=False, on_toggle=None, size=22):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=COLORS["bg_card"],
            highlightthickness=0,
            cursor="hand2"
        )
        self.size = size
        self.checked = checked
        self.on_toggle = on_toggle
        self.is_hovered = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def set_checked(self, checked, bg_color=None):
        self.checked = checked
        if bg_color:
            self.configure(bg=bg_color)
        self._draw()

    def _on_enter(self, event=None):
        self.is_hovered = True
        self._draw()

    def _on_leave(self, event=None):
        self.is_hovered = False
        self._draw()

    def _on_click(self, event=None):
        self.checked = not self.checked
        self._draw()
        if self.on_toggle:
            self.on_toggle(self.checked)

    def _draw(self):
        self.delete("all")
        s = self.size
        pad = 2
        r = 5  # corner radius

        if self.checked:
            fill = COLORS["primary"]
            border = COLORS["primary"]
            # Draw rounded box
            self.create_oval(pad, pad, pad + 2 * r, pad + 2 * r, fill=fill, outline="")
            self.create_oval(s - pad - 2 * r, pad, s - pad, pad + 2 * r, fill=fill, outline="")
            self.create_oval(pad, s - pad - 2 * r, pad + 2 * r, s - pad, fill=fill, outline="")
            self.create_oval(s - pad - 2 * r, s - pad - 2 * r, s - pad, s - pad, fill=fill, outline="")
            self.create_rectangle(pad + r, pad, s - pad - r, s - pad, fill=fill, outline="")
            self.create_rectangle(pad, pad + r, s - pad, s - pad - r, fill=fill, outline="")

            # Crisp checkmark
            points = [
                (pad + 4, s // 2),
                (pad + 8, s - pad - 5),
                (s - pad - 4, pad + 5)
            ]
            self.create_line(points, fill="#FFFFFF", width=2, capstyle="round", joinstyle="round")
        else:
            fill = "#FFFFFF"
            border = COLORS["primary"] if self.is_hovered else "#C2BEB4"

            # Draw rounded border box
            self.create_oval(pad, pad, pad + 2 * r, pad + 2 * r, fill=fill, outline=border)
            self.create_oval(s - pad - 2 * r, pad, s - pad, pad + 2 * r, fill=fill, outline=border)
            self.create_oval(pad, s - pad - 2 * r, pad + 2 * r, s - pad, fill=fill, outline=border)
            self.create_oval(s - pad - 2 * r, s - pad - 2 * r, s - pad, s - pad, fill=fill, outline=border)
            self.create_rectangle(pad + r, pad, s - pad - r, s - pad, fill=fill, outline=border)
            self.create_rectangle(pad, pad + r, s - pad, s - pad - r, fill=fill, outline=border)
            self.create_rectangle(pad + 1, pad + 1, s - pad - 1, s - pad - 1, fill=fill, outline="")


class AestheticBadge(tk.Frame):
    """Pill badge for Priority, Category, or Due Date."""

    def __init__(self, parent, text, bg_color, fg_color, dot_color=None, font_size=8):
        super().__init__(parent, bg=bg_color, padx=7, pady=2)
        self.configure(highlightbackground=bg_color, highlightthickness=1)

        col = 0
        if dot_color:
            dot = tk.Label(
                self,
                text="●",
                font=(FONT_FAMILY, font_size - 1),
                bg=bg_color,
                fg=dot_color
            )
            dot.grid(row=0, column=col, padx=(0, 3))
            col += 1

        lbl = tk.Label(
            self,
            text=text,
            font=(FONT_FAMILY, font_size, "bold"),
            bg=bg_color,
            fg=fg_color
        )
        lbl.grid(row=0, column=col)


# ==============================================================================
# MODAL DIALOGS
# Add Task, Edit Task, Delete Confirmation
# ==============================================================================

class TaskDialog(tk.Toplevel):
    """Cozy popup for adding or editing a task."""

    def __init__(self, parent, title="Add New Task", task=None, on_save=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=COLORS["bg_app"])

        self.task = task
        self.on_save = on_save
        self.result = None

        # Center popup over parent
        self.geometry("480x560")
        self._center_window(parent)

        self._build_ui()
        self.bind("<Escape>", lambda e: self.destroy())

    def _center_window(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()

        w = 480
        h = 560
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")

    def _build_ui(self):
        # Card container with soft border
        card = tk.Frame(
            self,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=28,
            pady=24
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        # Header
        header_frame = tk.Frame(card, bg=COLORS["bg_card"])
        header_frame.pack(fill="x", pady=(0, 16))

        icon = "🌱" if not self.task else "✏️"
        title_text = "Add New Task" if not self.task else "Edit Task"
        tk.Label(
            header_frame,
            text=f"{icon}  {title_text}",
            font=(FONT_FAMILY, 15, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_main"]
        ).pack(side="left")

        # Subtitle
        sub_text = "Organize what needs to get done." if not self.task else "Update the details for this task."
        tk.Label(
            card,
            text=sub_text,
            font=(FONT_FAMILY, 9),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        ).pack(anchor="w", pady=(0, 14))

        # Title Field
        tk.Label(
            card,
            text="Task Title *",
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_main"]
        ).pack(anchor="w", pady=(0, 4))

        title_wrap = tk.Frame(card, bg=COLORS["border"], padx=1, pady=1)
        title_wrap.pack(fill="x", pady=(0, 10))
        self.title_entry = tk.Entry(
            title_wrap,
            font=(FONT_FAMILY, 10),
            relief="flat",
            bg="#FFFFFF",
            fg=COLORS["text_main"],
            insertbackground=COLORS["primary"]
        )
        self.title_entry.pack(fill="x", ipady=5, padx=6)
        if self.task:
            self.title_entry.insert(0, self.task.get("title", ""))

        # Error label (hidden by default)
        self.error_label = tk.Label(
            card,
            text="",
            font=(FONT_FAMILY, 8),
            bg=COLORS["bg_card"],
            fg=COLORS["danger"]
        )
        self.error_label.pack(anchor="w", pady=(0, 4))

        # Description Field
        tk.Label(
            card,
            text="Description",
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_main"]
        ).pack(anchor="w", pady=(0, 4))

        desc_wrap = tk.Frame(card, bg=COLORS["border"], padx=1, pady=1)
        desc_wrap.pack(fill="x", pady=(0, 12))
        self.desc_text = tk.Text(
            desc_wrap,
            font=(FONT_FAMILY, 9),
            relief="flat",
            bg="#FFFFFF",
            fg=COLORS["text_main"],
            insertbackground=COLORS["primary"],
            height=3,
            wrap="word"
        )
        self.desc_text.pack(fill="x", padx=6, pady=4)
        if self.task and self.task.get("description"):
            self.desc_text.insert("1.0", self.task.get("description", ""))

        # Due Date Field + Quick Presets
        date_header = tk.Frame(card, bg=COLORS["bg_card"])
        date_header.pack(fill="x", pady=(0, 4))

        tk.Label(
            date_header,
            text="Due Date (YYYY-MM-DD)",
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_main"]
        ).pack(side="left")

        date_wrap = tk.Frame(card, bg=COLORS["border"], padx=1, pady=1)
        date_wrap.pack(fill="x", pady=(0, 6))
        self.date_entry = tk.Entry(
            date_wrap,
            font=(FONT_FAMILY, 10),
            relief="flat",
            bg="#FFFFFF",
            fg=COLORS["text_main"],
            insertbackground=COLORS["primary"]
        )
        self.date_entry.pack(fill="x", ipady=4, padx=6)
        if self.task and self.task.get("due_date"):
            self.date_entry.insert(0, self.task.get("due_date", ""))

        # Quick Preset Buttons
        chips_frame = tk.Frame(card, bg=COLORS["bg_card"])
        chips_frame.pack(fill="x", pady=(0, 14))

        def set_date_preset(days_ahead):
            d = date.today() + timedelta(days=days_ahead)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, d.isoformat())

        def clear_date():
            self.date_entry.delete(0, tk.END)

        presets = [
            ("Today", 0),
            ("Tomorrow", 1),
            ("+3 Days", 3),
            ("Next Week", 7),
        ]
        for name, days in presets:
            btn = tk.Button(
                chips_frame,
                text=name,
                font=(FONT_FAMILY, 8),
                bg=COLORS["action_bg"],
                fg=COLORS["action_fg"],
                relief="flat",
                cursor="hand2",
                padx=6,
                pady=1,
                command=lambda d=days: set_date_preset(d)
            )
            btn.pack(side="left", padx=(0, 4))

        clear_btn = tk.Button(
            chips_frame,
            text="Clear",
            font=(FONT_FAMILY, 8),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            relief="flat",
            cursor="hand2",
            padx=4,
            pady=1,
            command=clear_date
        )
        clear_btn.pack(side="left")

        # Priority & Category Side-by-Side
        meta_row = tk.Frame(card, bg=COLORS["bg_card"])
        meta_row.pack(fill="x", pady=(0, 16))

        # Priority Selection
        prio_frame = tk.Frame(meta_row, bg=COLORS["bg_card"])
        prio_frame.pack(side="left", fill="x", expand=True, padx=(0, 8))

        tk.Label(
            prio_frame,
            text="Priority",
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_main"]
        ).pack(anchor="w", pady=(0, 4))

        self.priority_var = tk.StringVar(value=self.task.get("priority", "Medium") if self.task else "Medium")
        prio_btn_row = tk.Frame(prio_frame, bg=COLORS["bg_card"])
        prio_btn_row.pack(anchor="w")

        for prio_val in ["Low", "Medium", "High"]:
            rb = tk.Radiobutton(
                prio_btn_row,
                text=prio_val,
                variable=self.priority_var,
                value=prio_val,
                font=(FONT_FAMILY, 9),
                bg=COLORS["bg_card"],
                fg=COLORS["text_main"],
                selectcolor="#FFFFFF",
                activebackground=COLORS["bg_card"],
                highlightthickness=0,
                cursor="hand2"
            )
            rb.pack(side="left", padx=(0, 8))

        # Category Selection
        cat_frame = tk.Frame(meta_row, bg=COLORS["bg_card"])
        cat_frame.pack(side="left", fill="x", expand=True)

        tk.Label(
            cat_frame,
            text="Category",
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_main"]
        ).pack(anchor="w", pady=(0, 4))

        self.category_var = tk.StringVar(value=self.task.get("category", "General") if self.task else "General")
        categories = ["General", "Study", "Work", "Personal", "Project"]
        
        cat_dropdown = ttk.Combobox(
            cat_frame,
            textvariable=self.category_var,
            values=categories,
            state="readonly",
            font=(FONT_FAMILY, 9)
        )
        cat_dropdown.pack(fill="x")

        # Bottom Action Buttons
        btn_frame = tk.Frame(card, bg=COLORS["bg_card"])
        btn_frame.pack(fill="x", pady=(8, 0))

        save_text = "Save Task" if not self.task else "Save Changes"
        save_btn = tk.Button(
            btn_frame,
            text=save_text,
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["primary_fg"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["primary_fg"],
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=6,
            command=self._save
        )
        save_btn.pack(side="right", padx=(8, 0))

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=(FONT_FAMILY, 9),
            bg=COLORS["action_bg"],
            fg=COLORS["action_fg"],
            activebackground=COLORS["action_hover"],
            activeforeground=COLORS["action_fg"],
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=self.destroy
        )
        cancel_btn.pack(side="right")

        self.title_entry.focus_set()

    def _save(self):
        title = self.title_entry.get().strip()
        if not title:
            self.error_label.config(text="⚠ Task title is required.")
            self.title_entry.focus_set()
            return

        due_date = self.date_entry.get().strip()
        if due_date:
            try:
                # Validate date format
                date.fromisoformat(due_date)
            except ValueError:
                self.error_label.config(text="⚠ Please use YYYY-MM-DD for due date (e.g. 2026-09-12).")
                self.date_entry.focus_set()
                return

        description = self.desc_text.get("1.0", tk.END).strip()
        priority = self.priority_var.get()
        category = self.category_var.get()

        self.result = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "priority": priority,
            "category": category
        }

        if self.on_save:
            self.on_save(self.result)

        self.destroy()


class ConfirmDeleteDialog(tk.Toplevel):
    """A clean modal confirmation popup for deleting a task."""

    def __init__(self, parent, task_title, on_confirm):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Delete Task")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg_app"])

        self.on_confirm = on_confirm

        self.geometry("380x210")
        self._center_window(parent)

        self._build_ui(task_title)
        self.bind("<Escape>", lambda e: self.destroy())

    def _center_window(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()

        w = 380
        h = 210
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")

    def _build_ui(self, task_title):
        card = tk.Frame(
            self,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=24,
            pady=20
        )
        card.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(
            card,
            text="🗑️  Delete this task?",
            font=(FONT_FAMILY, 12, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_main"]
        ).pack(anchor="w", pady=(0, 8))

        # Truncate title if too long
        display_title = f'"{task_title}"' if len(task_title) < 40 else f'"{task_title[:37]}..."'
        tk.Label(
            card,
            text=display_title,
            font=(FONT_FAMILY, 10, "italic"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            wraplength=320,
            justify="left"
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            card,
            text="This action cannot be undone.",
            font=(FONT_FAMILY, 8),
            bg=COLORS["bg_card"],
            fg=COLORS["text_light"]
        ).pack(anchor="w", pady=(0, 16))

        btn_row = tk.Frame(card, bg=COLORS["bg_card"])
        btn_row.pack(fill="x")

        del_btn = tk.Button(
            btn_row,
            text="Delete",
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["danger"],
            fg="#FFFFFF",
            activebackground=COLORS["danger_hover"],
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=5,
            command=self._confirm
        )
        del_btn.pack(side="right", padx=(8, 0))

        cancel_btn = tk.Button(
            btn_row,
            text="Cancel",
            font=(FONT_FAMILY, 9),
            bg=COLORS["action_bg"],
            fg=COLORS["action_fg"],
            activebackground=COLORS["action_hover"],
            activeforeground=COLORS["action_fg"],
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=5,
            command=self.destroy
        )
        cancel_btn.pack(side="right")

    def _confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.destroy()


# ==============================================================================
# TASK CARD COMPONENT
# Clean aesthetic card showing checkbox, title, badges, edit & delete
# ==============================================================================

class TaskCard(tk.Frame):
    """An individual aesthetic task card."""

    def __init__(self, parent, task, on_toggle, on_edit, on_delete):
        is_completed = task.get("completed", False)
        bg = COLORS["bg_card_completed"] if is_completed else COLORS["bg_card"]
        border = COLORS["border_completed"] if is_completed else COLORS["border"]

        super().__init__(
            parent,
            bg=bg,
            highlightbackground=border,
            highlightthickness=1,
            padx=16,
            pady=12
        )
        self.task = task
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.bg = bg

        self._build_ui()

    def _build_ui(self):
        is_completed = self.task.get("completed", False)

        # 1. Left Checkbox
        left_box = tk.Frame(self, bg=self.bg)
        left_box.pack(side="left", anchor="n", padx=(0, 14), pady=(2, 0))

        self.checkbox = CustomCheckbox(
            left_box,
            checked=is_completed,
            on_toggle=lambda checked: self.on_toggle(self.task.get("id"))
        )
        self.checkbox.set_checked(is_completed, bg_color=self.bg)
        self.checkbox.pack()

        # 2. Right Action Buttons
        right_box = tk.Frame(self, bg=self.bg)
        right_box.pack(side="right", anchor="n", padx=(10, 0))

        edit_btn = tk.Button(
            right_box,
            text="Edit",
            font=(FONT_FAMILY, 8, "bold"),
            bg=COLORS["action_bg"],
            fg=COLORS["action_fg"],
            activebackground=COLORS["action_hover"],
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2,
            command=lambda: self.on_edit(self.task.get("id"))
        )
        edit_btn.pack(side="left", padx=(0, 4))

        del_btn = tk.Button(
            right_box,
            text="Delete",
            font=(FONT_FAMILY, 8, "bold"),
            bg=COLORS["action_bg"],
            fg=COLORS["danger"],
            activebackground=COLORS["danger_bg"],
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2,
            command=lambda: self.on_delete(self.task.get("id"))
        )
        del_btn.pack(side="left")

        # 3. Middle Content Area
        mid_box = tk.Frame(self, bg=self.bg)
        mid_box.pack(side="left", fill="both", expand=True)

        # Task Title
        title_font = (FONT_FAMILY, 11, "bold") if not is_completed else (FONT_FAMILY, 11, "overstrike")
        title_fg = COLORS["text_completed"] if is_completed else COLORS["text_main"]

        title_lbl = tk.Label(
            mid_box,
            text=self.task.get("title", ""),
            font=title_font,
            bg=self.bg,
            fg=title_fg,
            anchor="w",
            justify="left",
            wraplength=480
        )
        title_lbl.pack(fill="x", anchor="w")

        # Description (if present)
        desc = self.task.get("description", "").strip()
        if desc:
            desc_fg = COLORS["text_light"] if is_completed else COLORS["text_muted"]
            desc_lbl = tk.Label(
                mid_box,
                text=desc,
                font=(FONT_FAMILY, 9),
                bg=self.bg,
                fg=desc_fg,
                anchor="w",
                justify="left",
                wraplength=480
            )
            desc_lbl.pack(fill="x", anchor="w", pady=(2, 6))

        # Badges Row (Due Date, Priority, Category)
        badges_row = tk.Frame(mid_box, bg=self.bg)
        badges_row.pack(anchor="w", pady=(4 if not desc else 0, 0))

        # Due Date Badge
        due_text, is_overdue, due_type = TaskManager.format_due_date(self.task.get("due_date", ""))
        if due_text:
            if is_completed:
                due_bg = COLORS["action_bg"]
                due_fg = COLORS["text_completed"]
            elif is_overdue:
                due_bg = COLORS["due_overdue_bg"]
                due_fg = COLORS["due_overdue_fg"]
            elif due_type == "today":
                due_bg = COLORS["due_today_bg"]
                due_fg = COLORS["due_today_fg"]
            else:
                due_bg = COLORS["due_tomorrow_bg"]
                due_fg = COLORS["due_tomorrow_fg"]

            AestheticBadge(badges_row, due_text, due_bg, due_fg).pack(side="left", padx=(0, 6))

        # Priority Badge
        prio = self.task.get("priority", "Medium")
        if prio == "High":
            p_bg, p_fg, p_dot = COLORS["prio_high_bg"], COLORS["prio_high_fg"], COLORS["prio_high_dot"]
        elif prio == "Low":
            p_bg, p_fg, p_dot = COLORS["prio_low_bg"], COLORS["prio_low_fg"], COLORS["prio_low_dot"]
        else:
            p_bg, p_fg, p_dot = COLORS["prio_med_bg"], COLORS["prio_med_fg"], COLORS["prio_med_dot"]

        if is_completed:
            p_bg = COLORS["action_bg"]
            p_fg = COLORS["text_completed"]
            p_dot = COLORS["text_completed"]

        AestheticBadge(badges_row, prio, p_bg, p_fg, dot_color=p_dot).pack(side="left", padx=(0, 6))

        # Category Badge
        cat = self.task.get("category", "General")
        cat_colors = {
            "General": (COLORS["cat_general_bg"], COLORS["cat_general_fg"]),
            "Study": (COLORS["cat_study_bg"], COLORS["cat_study_fg"]),
            "Work": (COLORS["cat_work_bg"], COLORS["cat_work_fg"]),
            "Personal": (COLORS["cat_personal_bg"], COLORS["cat_personal_fg"]),
            "Project": (COLORS["cat_project_bg"], COLORS["cat_project_fg"]),
        }
        c_bg, c_fg = cat_colors.get(cat, (COLORS["cat_general_bg"], COLORS["cat_general_fg"]))
        if is_completed:
            c_bg = COLORS["action_bg"]
            c_fg = COLORS["text_completed"]

        AestheticBadge(badges_row, cat, c_bg, c_fg).pack(side="left")


# ==============================================================================
# MAIN APPLICATION WINDOW
# MintoApp
# ==============================================================================

class MintoApp(tk.Tk):
    """Main Minto Application Window."""

    def __init__(self):
        super().__init__()
        self.title("MINTO - Plan it. Do it. Done.")
        self.geometry("900x670")
        self.minsize(760, 520)
        self.configure(bg=COLORS["bg_app"])

        # Center window on user screen
        self._center_window(900, 670)

        self.manager = TaskManager()
        self.filter_mode = "All"  # All, Active, Completed, Today
        self.search_query = ""
        self.toast_after_id = None

        self._build_ui()
        self.refresh_task_list()

    def _center_window(self, width, height):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")

    def _build_ui(self):
        """Constructs the complete layout."""
        # Top banner with shadow border
        self.main_container = tk.Frame(self, bg=COLORS["bg_app"])
        self.main_container.pack(fill="both", expand=True, padx=28, pady=(20, 16))

        # 1. Header Section
        self._build_header(self.main_container)

        # 2. Toast Banner (for non-blocking friendly feedback)
        self.toast_frame = tk.Frame(self.main_container, bg=COLORS["bg_app"], height=24)
        self.toast_frame.pack(fill="x", pady=(2, 4))
        self.toast_label = tk.Label(
            self.toast_frame,
            text="",
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["bg_app"],
            fg=COLORS["primary"]
        )
        self.toast_label.pack(side="left")

        # 3. Today's Progress Section Card
        self._build_progress_section(self.main_container)

        # 4. Action Bar (Search + Filter Chips + Add Task Button)
        self._build_action_bar(self.main_container)

        # 5. Tasks Area Header
        self._build_section_header(self.main_container)

        # 6. Scrollable Tasks Area
        self._build_scrollable_task_list(self.main_container)

        # 7. Bottom Motivational Footer
        footer = tk.Label(
            self.main_container,
            text="“Keep moving, one task at a time.”",
            font=(FONT_FAMILY, 9, "italic"),
            bg=COLORS["bg_app"],
            fg=COLORS["text_light"]
        )
        footer.pack(side="bottom", pady=(10, 0))

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=COLORS["bg_app"])
        header.pack(fill="x", pady=(0, 4))

        # Left Branding
        brand_frame = tk.Frame(header, bg=COLORS["bg_app"])
        brand_frame.pack(side="left")

        brand_row = tk.Frame(brand_frame, bg=COLORS["bg_app"])
        brand_row.pack(anchor="w")

        tk.Label(
            brand_row,
            text="🌱",
            font=(FONT_FAMILY, 18),
            bg=COLORS["bg_app"],
            fg=COLORS["primary"]
        ).pack(side="left", padx=(0, 6))

        tk.Label(
            brand_row,
            text="MINTO",
            font=(FONT_FAMILY, 20, "bold"),
            bg=COLORS["bg_app"],
            fg=COLORS["primary"]
        ).pack(side="left")

        tk.Label(
            brand_frame,
            text="Plan it. Do it. Done.",
            font=(FONT_FAMILY, 10, "italic"),
            bg=COLORS["bg_app"],
            fg=COLORS["text_muted"]
        ).pack(anchor="w", padx=(30, 0), pady=(0, 0))

        # Right Date Display
        today_formatted = date.today().strftime("%A, %B %d")
        date_card = tk.Frame(
            header,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=12,
            pady=6
        )
        date_card.pack(side="right", anchor="center")

        tk.Label(
            date_card,
            text=f"📅  {today_formatted}",
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        ).pack()

    def _build_progress_section(self, parent):
        self.progress_card = tk.Frame(
            parent,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=20,
            pady=14
        )
        self.progress_card.pack(fill="x", pady=(0, 14))

        # Top line: Title & Percentage
        top_line = tk.Frame(self.progress_card, bg=COLORS["bg_card"])
        top_line.pack(fill="x", pady=(0, 8))

        tk.Label(
            top_line,
            text="Today's Progress",
            font=(FONT_FAMILY, 11, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_main"]
        ).pack(side="left")

        self.progress_pct_label = tk.Label(
            top_line,
            text="0%",
            font=(FONT_FAMILY, 12, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["primary"]
        )
        self.progress_pct_label.pack(side="right")

        # Custom Canvas Progress Bar
        self.progress_bar = SmoothProgressBar(self.progress_card, height=12)
        self.progress_bar.pack(fill="x", pady=(0, 10))

        # Bottom line: Motivational quote and counts
        bottom_line = tk.Frame(self.progress_card, bg=COLORS["bg_card"])
        bottom_line.pack(fill="x")

        self.motivational_label = tk.Label(
            bottom_line,
            text="Let's get started.",
            font=(FONT_FAMILY, 9, "italic"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        )
        self.motivational_label.pack(side="left")

        self.stats_label = tk.Label(
            bottom_line,
            text="0 tasks • 0 completed • 0 remaining",
            font=(FONT_FAMILY, 9),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        )
        self.stats_label.pack(side="right")

    def _build_action_bar(self, parent):
        action_bar = tk.Frame(parent, bg=COLORS["bg_app"])
        action_bar.pack(fill="x", pady=(0, 12))

        # Left: Search Bar Box
        search_wrap = tk.Frame(
            action_bar,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=8,
            pady=4
        )
        search_wrap.pack(side="left", fill="x", expand=True, padx=(0, 12))

        tk.Label(
            search_wrap,
            text="🔍",
            font=(FONT_FAMILY, 9),
            bg=COLORS["bg_card"],
            fg=COLORS["text_light"]
        ).pack(side="left", padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_wrap,
            textvariable=self.search_var,
            font=(FONT_FAMILY, 10),
            relief="flat",
            bg=COLORS["bg_card"],
            fg=COLORS["text_main"],
            insertbackground=COLORS["primary"]
        )
        self.search_entry.pack(side="left", fill="x", expand=True)

        # Placeholder management
        self.placeholder_text = "Search tasks..."
        self._set_search_placeholder()
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)
        self.search_var.trace_add("write", self._on_search_change)

        # Clear search button (✕)
        self.clear_search_btn = tk.Label(
            search_wrap,
            text="✕",
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_light"],
            cursor="hand2"
        )
        self.clear_search_btn.bind("<Button-1>", lambda e: self._clear_search())

        # Middle: Filter Buttons
        self.filter_frame = tk.Frame(action_bar, bg=COLORS["bg_app"])
        self.filter_frame.pack(side="left", padx=(0, 12))

        self.filter_buttons = {}
        for f_name in ["All", "Active", "Completed", "Today"]:
            btn = tk.Button(
                self.filter_frame,
                text=f_name,
                font=(FONT_FAMILY, 9, "bold"),
                relief="flat",
                cursor="hand2",
                padx=10,
                pady=4,
                command=lambda name=f_name: self.set_filter(name)
            )
            btn.pack(side="left", padx=2)
            self.filter_buttons[f_name] = btn

        self._update_filter_button_styles()

        # Right: Add Task Primary Button
        add_btn = tk.Button(
            action_bar,
            text="+ Add Task",
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["primary_fg"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["primary_fg"],
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=5,
            command=self.open_add_task_dialog
        )
        add_btn.pack(side="right")

    def _build_section_header(self, parent):
        self.section_header = tk.Frame(parent, bg=COLORS["bg_app"])
        self.section_header.pack(fill="x", pady=(0, 6))

        self.section_title_lbl = tk.Label(
            self.section_header,
            text="TODAY'S TASKS",
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["bg_app"],
            fg=COLORS["text_muted"]
        )
        self.section_title_lbl.pack(side="left")

        self.task_count_badge = tk.Label(
            self.section_header,
            text="",
            font=(FONT_FAMILY, 8, "bold"),
            bg=COLORS["border"],
            fg=COLORS["text_main"],
            padx=6,
            pady=1
        )
        self.task_count_badge.pack(side="left", padx=(8, 0))

    def _build_scrollable_task_list(self, parent):
        """Scrollable container for task cards."""
        self.scroll_container = tk.Frame(parent, bg=COLORS["bg_app"])
        self.scroll_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.scroll_container,
            bg=COLORS["bg_app"],
            highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self.scroll_container,
            orient="vertical",
            command=self.canvas.yview
        )

        self.cards_frame = tk.Frame(self.canvas, bg=COLORS["bg_app"])
        self.cards_window = self.canvas.create_window(
            (0, 0),
            window=self.cards_frame,
            anchor="nw"
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Automatically adjust scroll region and width
        self.cards_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.cards_window, width=e.width)
        )

        # Mousewheel binding across canvas and child widgets
        self._bind_mousewheel(self)

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        for child in widget.winfo_children():
            self._bind_mousewheel(child)

    def _on_mousewheel(self, event):
        # On Windows, event.delta is positive for scrolling up, negative for scrolling down
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ==========================================================================
    # SEARCH & FILTER LOGIC
    # ==========================================================================

    def _set_search_placeholder(self):
        if not self.search_query:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, self.placeholder_text)
            self.search_entry.config(fg=COLORS["text_light"])

    def _on_search_focus_in(self, event):
        if self.search_entry.get() == self.placeholder_text:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=COLORS["text_main"])

    def _on_search_focus_out(self, event):
        if not self.search_entry.get().strip():
            self._set_search_placeholder()
            self.clear_search_btn.pack_forget()

    def _on_search_change(self, *args):
        val = self.search_var.get()
        if val == self.placeholder_text:
            return

        self.search_query = val.strip()
        if self.search_query:
            self.clear_search_btn.pack(side="right", padx=(4, 2))
        else:
            self.clear_search_btn.pack_forget()

        self.refresh_task_list()

    def _clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.search_query = ""
        self._set_search_placeholder()
        self.clear_search_btn.pack_forget()
        self.refresh_task_list()

    def set_filter(self, filter_name):
        self.filter_mode = filter_name
        self._update_filter_button_styles()
        self.refresh_task_list()

    def _update_filter_button_styles(self):
        for name, btn in self.filter_buttons.items():
            if name == self.filter_mode:
                btn.config(
                    bg=COLORS["primary"],
                    fg=COLORS["primary_fg"],
                    activebackground=COLORS["primary_hover"],
                    activeforeground=COLORS["primary_fg"]
                )
            else:
                btn.config(
                    bg=COLORS["action_bg"],
                    fg=COLORS["action_fg"],
                    activebackground=COLORS["action_hover"],
                    activeforeground=COLORS["action_fg"]
                )

    # ==========================================================================
    # PROGRESS & TASK REFRESH
    # ==========================================================================

    def show_toast(self, message):
        """Shows a friendly non-blocking notification toast."""
        self.toast_label.config(text=message)
        if self.toast_after_id:
            self.after_cancel(self.toast_after_id)
        self.toast_after_id = self.after(3000, lambda: self.toast_label.config(text=""))

    def update_progress(self):
        stats = self.manager.get_progress_stats()
        pct = stats["percentage"]

        self.progress_pct_label.config(text=f"{pct}%")
        self.progress_bar.set_progress(pct)
        self.motivational_label.config(text=stats["message"])

        if stats["total"] == 0:
            self.stats_label.config(text="0 tasks")
        else:
            self.stats_label.config(
                text=f"{stats['total']} tasks • {stats['completed']} completed • {stats['remaining']} remaining"
            )

    def refresh_task_list(self):
        """Clears and re-renders task cards based on search and filters."""
        # 1. Update Progress Header
        self.update_progress()

        # 2. Update Section Title
        filter_titles = {
            "All": "ALL TASKS",
            "Active": "ACTIVE TASKS",
            "Completed": "COMPLETED TASKS",
            "Today": "TODAY'S TASKS"
        }
        self.section_title_lbl.config(text=filter_titles.get(self.filter_mode, "TASKS"))

        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        # 3. Retrieve filtered tasks
        filtered_tasks = self.manager.get_filtered_tasks(
            query=self.search_query,
            filter_mode=self.filter_mode
        )

        self.task_count_badge.config(text=str(len(filtered_tasks)))

        # 4. Handle Empty States
        if not filtered_tasks:
            self._render_empty_state()
            return

        # 5. Render Cards
        for task in filtered_tasks:
            card = TaskCard(
                self.cards_frame,
                task=task,
                on_toggle=self.toggle_task,
                on_edit=self.open_edit_task_dialog,
                on_delete=self.confirm_delete_task
            )
            card.pack(fill="x", expand=True, pady=(0, 10))
            self._bind_mousewheel(card)

    def _render_empty_state(self):
        """Displays cozy minimal empty state."""
        empty_box = tk.Frame(
            self.cards_frame,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=20,
            pady=36
        )
        empty_box.pack(fill="x", pady=20)
        self._bind_mousewheel(empty_box)

        if len(self.manager.tasks) == 0:
            # Entire list is empty
            tk.Label(
                empty_box,
                text="✨",
                font=(FONT_FAMILY, 32),
                bg=COLORS["bg_card"],
                fg=COLORS["primary"]
            ).pack(pady=(0, 6))

            tk.Label(
                empty_box,
                text="No tasks yet",
                font=(FONT_FAMILY, 14, "bold"),
                bg=COLORS["bg_card"],
                fg=COLORS["text_main"]
            ).pack(pady=(0, 4))

            tk.Label(
                empty_box,
                text="“Add something to get started.”",
                font=(FONT_FAMILY, 10, "italic"),
                bg=COLORS["bg_card"],
                fg=COLORS["text_muted"]
            ).pack(pady=(0, 14))

            tk.Button(
                empty_box,
                text="+ Add Task",
                font=(FONT_FAMILY, 9, "bold"),
                bg=COLORS["primary"],
                fg=COLORS["primary_fg"],
                activebackground=COLORS["primary_hover"],
                activeforeground=COLORS["primary_fg"],
                relief="flat",
                cursor="hand2",
                padx=14,
                pady=6,
                command=self.open_add_task_dialog
            ).pack()

        else:
            # Filter or Search returned 0
            tk.Label(
                empty_box,
                text="🔍",
                font=(FONT_FAMILY, 28),
                bg=COLORS["bg_card"],
                fg=COLORS["text_light"]
            ).pack(pady=(0, 6))

            tk.Label(
                empty_box,
                text="No tasks found.",
                font=(FONT_FAMILY, 13, "bold"),
                bg=COLORS["bg_card"],
                fg=COLORS["text_main"]
            ).pack(pady=(0, 4))

            detail_text = (
                f'No tasks match "{self.search_query}"'
                if self.search_query
                else f"No {self.filter_mode.lower()} tasks found."
            )
            tk.Label(
                empty_box,
                text=detail_text,
                font=(FONT_FAMILY, 9),
                bg=COLORS["bg_card"],
                fg=COLORS["text_muted"]
            ).pack(pady=(0, 12))

            tk.Button(
                empty_box,
                text="Show All Tasks",
                font=(FONT_FAMILY, 9),
                bg=COLORS["action_bg"],
                fg=COLORS["action_fg"],
                activebackground=COLORS["action_hover"],
                relief="flat",
                cursor="hand2",
                padx=12,
                pady=4,
                command=lambda: [self._clear_search(), self.set_filter("All")]
            ).pack()

    # ==========================================================================
    # USER ACTIONS & CRUD
    # ==========================================================================

    def open_add_task_dialog(self):
        def handle_save(data):
            self.manager.add_task(
                title=data["title"],
                description=data["description"],
                due_date=data["due_date"],
                priority=data["priority"],
                category=data["category"]
            )
            self.show_toast("✓ Task added successfully.")
            self.refresh_task_list()

        TaskDialog(self, title="Add New Task", on_save=handle_save)

    def open_edit_task_dialog(self, task_id):
        task = self.manager.get_task(task_id)
        if not task:
            return

        def handle_save(data):
            self.manager.update_task(
                task_id=task_id,
                title=data["title"],
                description=data["description"],
                due_date=data["due_date"],
                priority=data["priority"],
                category=data["category"]
            )
            self.show_toast("✓ Task updated successfully.")
            self.refresh_task_list()

        TaskDialog(self, title="Edit Task", task=task, on_save=handle_save)

    def confirm_delete_task(self, task_id):
        task = self.manager.get_task(task_id)
        if not task:
            return

        def handle_confirm():
            self.manager.delete_task(task_id)
            self.show_toast("🗑️ Task deleted.")
            self.refresh_task_list()

        ConfirmDeleteDialog(self, task_title=task.get("title", ""), on_confirm=handle_confirm)

    def toggle_task(self, task_id):
        new_status = self.manager.toggle_completed(task_id)
        if new_status is not None:
            if new_status:
                self.show_toast("✨ Nice work! Task completed.")
            self.refresh_task_list()


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    import webbrowser
    import threading
    import time

    if "--gui" in sys.argv or "--desktop" in sys.argv:
        print("🌱 Launching MINTO Desktop GUI...")
        app = MintoApp()
        app.mainloop()
        return

    try:
        from app import app as flask_app
        port = 5000
        url = f"http://127.0.0.1:{port}"

        print("=" * 60)
        print("🌱 MINTO - Modern SaaS Productivity Workspace")
        print("   Tagline: 'Plan it. Do it. Done.'")
        print(f" * Dashboard URL: {url}")
        print(" * Tip: Run 'python main.py --gui' to launch the legacy desktop window.")
        print("=" * 60)

        def open_browser():
            time.sleep(1.0)
            webbrowser.open(url)

        threading.Thread(target=open_browser, daemon=True).start()
        flask_app.run(host="127.0.0.1", port=port, debug=False)
    except Exception as e:
        print(f"Notice: Falling back to desktop GUI ({e})...")
        app = MintoApp()
        app.mainloop()


if __name__ == "__main__":
    main()

