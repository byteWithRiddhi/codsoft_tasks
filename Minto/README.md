# MINTO — Modern SaaS Productivity Workspace

> **"Plan it. Do it. Done."**

MINTO is a premium, modern, and interactive productivity dashboard inspired by Linear, Notion, Sunsama, and Motion. It bridges seamless task management, timeline scheduling, and category-driven productivity insights into an elegant SaaS-style desktop and mobile-responsive workspace.

---

## 🌟 Visual Design & SaaS Experience

- **Refined SaaS Color Palette**: Soft warm off-white background (`#F7F8FC`), crisp white surface cards (`#FFFFFF`), deep woodland charcoal text (`#20222B`), and modern indigo/violet accents (`#4F46E5`).
- **Dark Mode Support**: Instant toggle between Light Mode and Dark Mode (`#0B0E14` / `#151922`), saved in browser `localStorage`.
- **Lucide Iconography**: Consistent, modern vector icons across all sidebar links, badges, action buttons, and status indicators.
- **Micro-Interactions**: Animated custom checkboxes, smooth card elevations, interactive calendar cells, and real-time Chart.js velocity graphs.
- **Zero Tailwind Dependency**: Crafted cleanly with modern CSS variables and Bootstrap 5 responsive grid principles.

---

## ✨ Features & Architecture

### 1. 🧭 Modern Navigation Sidebar
- **Brand Identity**: Sleek Minto logo mark with leaf checkmark icon.
- **User Profile**: Personalized profile badge for **Riddhi** with online status indicator.
- **Primary Views**:
  - **Overview**: Personalized morning greeting, 5 KPI metrics, Today's Focus, Progress Overview, Upcoming Schedule, and Recent Activity feed.
  - **My Tasks**: Dedicated task management with status tabs (*All, Today, Upcoming, Completed, Overdue*), multi-factor filters (Priority, Category, Status), sorting, and List/Grid view toggle.
  - **Calendar**: Interactive monthly and weekly planner displaying tasks on due dates with click-to-add functionality.
  - **Projects**: Category-based project cards (*Study, Project, Work, Personal, General*) tracking completion velocity.
  - **Analytics**: Real-time productivity insights with 4 dynamic charts (Weekly Activity Trend, Status Breakdown, Priority Distribution, Category Share).
  - **Notes**: Built-in scratchpad for capturing thoughts, meeting memos, and study notes.
  - **Settings**: Profile customization, appearance toggle, and 1-click JSON export.
- **Collapsible & Mobile Ready**: Sidebar collapses with one click and adapts into a slide-out drawer on tablets and mobile phones.

### 2. 📊 5-Metric Productivity Overview
- **Total Tasks**: Cumulative task count.
- **Completed**: Finished tasks with progress indicator.
- **Pending**: Current active workload.
- **Overdue**: Critical tasks requiring urgent attention.
- **Completion Rate**: Live percentage with visual circular gauge and dynamic motivational quote.

### 3. 📝 Interactive Task Management & Modals
- **Custom Animated Checkboxes**: Smooth checkmark animation with strikethrough transition.
- **Task Metadata**: Colored priority pills (🔴 High, 🟡 Medium, 🟢 Low), category badges, and relative due-date pills (*Today, Tomorrow, Overdue*).
- **Quick Add / Edit Modal**: Form supporting title validation, multiline notes, due date (with quick preset chips: *Today, Tomorrow, +3 Days, Next Week*), due time, priority, category, and status.
- **Safe Deletion**: Modal confirmation protects against accidental deletion.

### 4. 💾 100% Data Preservation & REST API
- All tasks continue to persist locally in [`tasks.json`](tasks.json).
- Notes are persistently stored in [`notes.json`](notes.json).
- Activity logs are maintained in [`activity.json`](activity.json).
- Built-in Flask REST API:
  - `GET /api/tasks` — List and filter tasks
  - `POST /api/tasks` — Create task
  - `PUT /api/tasks/<id>` — Update task
  - `PATCH /api/tasks/<id>/toggle` — Toggle completion
  - `DELETE /api/tasks/<id>` — Delete task
  - `GET /api/stats` — Real-time metrics and chart data
  - `GET /api/notes` & `POST /api/notes` — Scratchpad operations
  - `GET /api/activity` — Recent activity feed

---

## 📁 Project Structure

```
Minto/
├── app.py                 # Flask server & REST API endpoints
├── main.py                # Unified launcher (web browser auto-open or desktop GUI)
├── tasks.json             # Persistent local JSON task database
├── notes.json             # Persistent local JSON notes database
├── activity.json          # Activity stream storage
├── templates/
│   └── index.html         # Single-Page SaaS dashboard template
├── static/
│   ├── css/
│   │   └── style.css      # SaaS design system, CSS variables, dark mode
│   └── js/
│       └── app.js         # Reactive dashboard, calendar, Chart.js, modals
└── README.md              # Project documentation
```

---

## 🚀 How to Run

### Requirements
- **Python 3.8+** installed.
- Required library: `Flask` (already installed).

### Launching the Application

1. Open your terminal in the project directory:
   ```bash
   cd c:\Users\HP\My_Projects\Minto
   ```

2. Start the modern SaaS workspace:
   ```bash
   python main.py
   ```
   *This will launch the Flask server at `http://127.0.0.1:5000` and automatically open your default web browser.*

3. Alternatively, run via Flask directly:
   ```bash
   python app.py
   ```

4. *Optional*: If you ever want to view the legacy desktop window, run:
   ```bash
   python main.py --gui
   ```

---

## 📱 Responsive Testing

- **Desktop (1200px+)**: Multi-column dashboard with fixed/collapsible sidebar and analytics grids.
- **Tablet (768px – 992px)**: Adaptive cards, stacked widgets, and collapsible navigation.
- **Mobile (< 768px)**: Slide-out offcanvas navigation, single-column task cards, and mobile-friendly touch targets.
