# Connecta 📇
> *Your contacts, beautifully organized.*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter%206.0-4F46E5?style=flat)](https://customtkinter.tomschimansky.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

**Connecta** is a modern, portfolio-ready desktop contact management application built with **Python** and **CustomTkinter**. Designed with contemporary SaaS and productivity application ergonomics, it elevates the traditional contact book into an intuitive, card-based desktop workspace featuring live multi-field search, priority favorites, category segmentation, detailed profile inspection, light/dark themes, and persistent JSON storage.

---

## 📸 Key Highlights & Features

- 🎨 **Modern 3-Column Responsive Layout**:
  - **Left Sidebar**: Navigation, category filters, live count badges, theme switcher, and prominent Add Contact CTA.
  - **Center Feed**: Compact statistic chips, live instant search bar, sort dropdown, and scrollable contact cards.
  - **Right Details Panel**: Profile card with large initials avatar, category tag, star toggle, quick-copy phone/email buttons, notes, and action triggers.
- 🔍 **Real-Time Multi-Field Search**:
  - Dynamically filters contacts as you type across **Name**, **Phone Number**, **Email Address**, **Physical Address**, and **Notes**.
- ⭐ **Favorites & Quick Filters**:
  - One-click star toggle from both the card feed and details preview.
  - Dedicated "Favorites" and "Recently Added" views in the sidebar.
- 🏷️ **Category Tagging**:
  - Organize contacts into **Work**, **Family**, **Friends**, **College**, or **Other** with distinct color badges.
- 🌓 **Dual Theme Engine (Light & Dark)**:
  - Polished Light Mode by default, switchable to Dark Mode with a single click.
- 📝 **Modern Add & Edit Modal Dialogs**:
  - Unified modal form with inline validation, helpful placeholders, and required field indicators.
  - Prevents duplicate phone entries and validates email formats.
- 🔔 **Non-Intrusive Floating Toasts**:
  - Sleek, auto-dismissing toast notifications replace abrupt popup dialogs for all save, update, delete, and favorite operations.
- 💾 **Safe JSON Persistence & Schema Migration**:
  - Automatic atomic writes ensure zero data corruption.
  - 100% backward-compatible: transparently migrates legacy contact files without losing existing records.

---

## 📁 Project Structure

```
ContactBook/
│
├── main.py                     # Application entry point
├── requirements.txt            # Project dependencies (customtkinter, darkdetect, Pillow)
├── contacts.json               # Persistent JSON storage file
├── README.md                   # Complete documentation
│
├── services/                   # Business Logic & Data Persistence Layer
│   ├── __init__.py
│   ├── storage_service.py      # Atomic JSON I/O and legacy schema migration
│   ├── contact_service.py      # In-memory CRUD, search, filter, sort, and stats
│   └── validation_service.py   # Name, phone, and email validation logic
│
├── ui/                         # Presentation Layer (CustomTkinter)
│   ├── __init__.py
│   ├── theme.py                # Design tokens, color palettes, and avatar hash generator
│   ├── app.py                  # Main window layout and view coordinator
│   ├── sidebar.py              # Navigation sidebar with counts and theme toggle
│   ├── contact_list.py         # Contact cards, search bar, sort controls, empty states
│   ├── contact_details.py      # Right details panel with profile info and copy actions
│   ├── contact_form.py         # Modern Add / Edit modal dialog
│   ├── dialogs.py              # Styled delete confirmation modal
│   └── toast.py                # Subtle floating in-app notification toasts
│
└── tests/                      # Automated Unit & Integration Tests
    └── test_connecta.py        # Storage migration, validation, and CRUD test suite
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.8** or higher installed on your system.
- Check your Python version:
  ```bash
  python --version
  ```

### 2. Installation
Clone or navigate to the project directory and install the required dependencies:

```bash
cd ContactBook
python -m pip install -r requirements.txt
```

### 3. Run the Application
Launch Connecta with:

```bash
python main.py
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + N` | Open "Add New Contact" modal |
| `Ctrl + F` | Focus the search input field |
| `Esc` | Clear active search filter |

---

## 🧪 Running Automated Tests

Run the full unit and integration test suite:

```bash
python -m unittest tests/test_connecta.py
```

All 6 test suites verify schema migration, validation constraints, full CRUD cycles, search and sorting filters, and headless UI initialization.

---

## 🛡️ Backward Compatibility Guarantee

Existing records in `contacts.json` format:
```json
{
    "name": "Riddhi Pawar",
    "phone": "9945884191",
    "email": "abc@gmail.com",
    "address": "31 Akurli Road, Mumbai"
}
```
Are preserved and automatically populated with modern defaults (`id`, `category`, `favorite`, `notes`, `created_at`) when loaded, ensuring legacy data remains safe and functional.
