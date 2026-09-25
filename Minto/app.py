#!/usr/bin/env python3
"""
MINTO - Modern SaaS Productivity Application
Flask Backend & REST API
"""

import os
import sys
import json
from datetime import date, datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(BASE_DIR, "tasks.json")
NOTES_FILE = os.path.join(BASE_DIR, "notes.json")
ACTIVITY_FILE = os.path.join(BASE_DIR, "activity.json")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = "minto-saas-secret-key-2026"


# ==============================================================================
# DATA PERSISTENCE HELPERS
# ==============================================================================

def load_json_file(filepath, default_factory):
    if not os.path.exists(filepath):
        data = default_factory()
        save_json_file(filepath, data)
        return data
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default_factory()

def save_json_file(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"Error saving {filepath}: {e}", file=sys.stderr)
        return False

def get_tasks():
    return load_json_file(TASKS_FILE, list)

def save_tasks(tasks):
    return save_json_file(TASKS_FILE, tasks)

def get_notes():
    return load_json_file(NOTES_FILE, list)

def save_notes(notes):
    return save_json_file(NOTES_FILE, notes)

def get_activity():
    return load_json_file(ACTIVITY_FILE, lambda: [
        {
            "id": 1,
            "action": "completed",
            "title": "Attend Python workshop",
            "timestamp": "2026-09-20T11:00:00",
            "type": "task"
        },
        {
            "id": 2,
            "action": "created",
            "title": "python assignment",
            "timestamp": "2026-09-20T09:15:00",
            "type": "task"
        }
    ])

def log_activity(action, title, item_type="task"):
    activities = get_activity()
    new_entry = {
        "id": max([a.get("id", 0) for a in activities], default=0) + 1,
        "action": action,
        "title": title,
        "timestamp": datetime.now().isoformat(),
        "type": item_type
    }
    activities.insert(0, new_entry)
    # Keep last 30 activities
    activities = activities[:30]
    save_json_file(ACTIVITY_FILE, activities)


# ==============================================================================
# FRONTEND ROUTE
# ==============================================================================

@app.route("/")
def index():
    return render_template("index.html")


# ==============================================================================
# TASKS REST API
# ==============================================================================

@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    tasks = get_tasks()
    today_str = date.today().isoformat()

    # Query params
    query = request.args.get("q", "").strip().lower()
    status_filter = request.args.get("status", "").strip()
    priority_filter = request.args.get("priority", "").strip()
    category_filter = request.args.get("category", "").strip()
    view_tab = request.args.get("tab", "all").strip().lower()

    filtered = []
    for task in tasks:
        # Check title/desc search
        if query:
            t_title = task.get("title", "").lower()
            t_desc = task.get("description", "").lower()
            t_cat = task.get("category", "").lower()
            if query not in t_title and query not in t_desc and query not in t_cat:
                continue

        # Priority filter
        if priority_filter and task.get("priority") != priority_filter:
            continue

        # Category filter
        if category_filter and task.get("category") != category_filter:
            continue

        # Status filter
        t_status = task.get("status")
        is_completed = task.get("completed", False)
        due_date = task.get("due_date", "")

        if status_filter:
            if status_filter == "Completed" and not is_completed:
                continue
            elif status_filter != "Completed" and t_status != status_filter:
                continue

        # View tabs: all, today, upcoming, completed, overdue
        if view_tab == "today":
            if due_date != today_str:
                continue
        elif view_tab == "upcoming":
            if not due_date or due_date <= today_str or is_completed:
                continue
        elif view_tab == "completed":
            if not is_completed:
                continue
        elif view_tab == "overdue":
            if not due_date or due_date >= today_str or is_completed:
                continue

        filtered.append(task)

    return jsonify({"success": True, "tasks": filtered, "total": len(filtered)})


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"success": False, "error": "Task title is required."}), 400

    tasks = get_tasks()
    next_id = max([t.get("id", 0) for t in tasks], default=0) + 1

    status = data.get("status", "To Do")
    completed = data.get("completed", False)
    if status == "Completed":
        completed = True
    elif completed:
        status = "Completed"

    new_task = {
        "id": next_id,
        "title": title,
        "description": data.get("description", "").strip(),
        "due_date": data.get("due_date", "").strip(),
        "due_time": data.get("due_time", "").strip(),
        "priority": data.get("priority", "Medium"),
        "category": data.get("category", "General"),
        "status": status,
        "completed": completed,
        "reminder": data.get("reminder", False),
        "created_at": datetime.now().isoformat()
    }

    tasks.append(new_task)
    save_tasks(tasks)
    log_activity("created", title)

    return jsonify({"success": True, "task": new_task, "message": "Task created successfully."}), 201


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task_by_id(task_id):
    tasks = get_tasks()
    for task in tasks:
        if task.get("id") == task_id:
            return jsonify({"success": True, "task": task})
    return jsonify({"success": False, "error": "Task not found."}), 404


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json() or {}
    tasks = get_tasks()

    for task in tasks:
        if task.get("id") == task_id:
            if "title" in data:
                title = data["title"].strip()
                if not title:
                    return jsonify({"success": False, "error": "Task title cannot be empty."}), 400
                task["title"] = title

            if "description" in data:
                task["description"] = data["description"].strip()
            if "due_date" in data:
                task["due_date"] = data["due_date"].strip()
            if "due_time" in data:
                task["due_time"] = data["due_time"].strip()
            if "priority" in data:
                task["priority"] = data["priority"]
            if "category" in data:
                task["category"] = data["category"]
            if "reminder" in data:
                task["reminder"] = bool(data["reminder"])

            if "status" in data:
                task["status"] = data["status"]
                task["completed"] = (data["status"] == "Completed")
            elif "completed" in data:
                task["completed"] = bool(data["completed"])
                task["status"] = "Completed" if task["completed"] else "To Do"

            save_tasks(tasks)
            log_activity("updated", task["title"])
            return jsonify({"success": True, "task": task, "message": "Task updated successfully."})

    return jsonify({"success": False, "error": "Task not found."}), 404


@app.route("/api/tasks/<int:task_id>/toggle", methods=["PATCH"])
def toggle_task(task_id):
    tasks = get_tasks()
    for task in tasks:
        if task.get("id") == task_id:
            task["completed"] = not task.get("completed", False)
            task["status"] = "Completed" if task["completed"] else "To Do"
            save_tasks(tasks)
            action = "completed" if task["completed"] else "reopened"
            log_activity(action, task["title"])
            return jsonify({
                "success": True,
                "task": task,
                "completed": task["completed"],
                "message": f"Task marked as {'completed' if task['completed'] else 'active'}."
            })

    return jsonify({"success": False, "error": "Task not found."}), 404


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    tasks = get_tasks()
    for i, task in enumerate(tasks):
        if task.get("id") == task_id:
            title = task.get("title", "")
            tasks.pop(i)
            save_tasks(tasks)
            log_activity("deleted", title)
            return jsonify({"success": True, "message": "Task deleted successfully.", "title": title})

    return jsonify({"success": False, "error": "Task not found."}), 404


# ==============================================================================
# STATS & ANALYTICS API
# ==============================================================================

@app.route("/api/stats", methods=["GET"])
def get_stats():
    tasks = get_tasks()
    today_str = date.today().isoformat()

    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("completed", False))
    pending = total - completed

    # Overdue calculation (due_date < today and not completed)
    overdue = 0
    for t in tasks:
        d = t.get("due_date", "")
        if d and d < today_str and not t.get("completed", False):
            overdue += 1

    completion_rate = round((completed / total * 100) if total > 0 else 0)

    # Priority distribution
    priority_counts = {"High": 0, "Medium": 0, "Low": 0}
    for t in tasks:
        p = t.get("priority", "Medium")
        if p in priority_counts:
            priority_counts[p] += 1

    # Category breakdown
    category_counts = {}
    for t in tasks:
        c = t.get("category", "General")
        category_counts[c] = category_counts.get(c, 0) + 1

    # Status distribution
    status_counts = {
        "To Do": sum(1 for t in tasks if t.get("status") == "To Do" and not t.get("completed")),
        "In Progress": sum(1 for t in tasks if t.get("status") == "In Progress"),
        "Completed": completed,
        "Overdue": overdue,
        "On Hold": sum(1 for t in tasks if t.get("status") == "On Hold")
    }

    # Weekly timeline (last 7 days)
    weekly_labels = []
    weekly_created = []
    weekly_completed = []
    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)
        day_str = day.isoformat()
        weekly_labels.append(day.strftime("%a"))
        # Counts
        due_on_day = sum(1 for t in tasks if t.get("due_date") == day_str)
        weekly_created.append(due_on_day)
        weekly_completed.append(sum(1 for t in tasks if t.get("due_date") == day_str and t.get("completed")))

    # Motivational status
    if total == 0:
        quote = "Your day is clear ✨ Ready to start something new?"
    elif completion_rate == 100:
        quote = "All done! Outstanding productivity today ✨"
    elif completion_rate >= 70:
        quote = "Incredible momentum! You're almost at the finish line."
    elif completion_rate >= 40:
        quote = "Great pace! Keep moving one task at a time."
    else:
        quote = "Plan it. Do it. Done. Let's make today count!"

    # Most productive category
    most_productive_cat = "General"
    max_cat_count = -1
    for cat, count in category_counts.items():
        if count > max_cat_count:
            max_cat_count = count
            most_productive_cat = cat

    return jsonify({
        "success": True,
        "stats": {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "overdue_tasks": overdue,
            "completion_rate": completion_rate,
            "motivational_quote": quote,
            "most_productive_category": most_productive_cat,
            "priority_counts": priority_counts,
            "category_counts": category_counts,
            "status_counts": status_counts,
            "weekly_data": {
                "labels": weekly_labels,
                "created": weekly_created,
                "completed": weekly_completed
            }
        }
    })


# ==============================================================================
# NOTES REST API
# ==============================================================================

@app.route("/api/notes", methods=["GET"])
def list_notes():
    notes = get_notes()
    return jsonify({"success": True, "notes": notes})


@app.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"success": False, "error": "Note title is required."}), 400

    notes = get_notes()
    next_id = max([n.get("id", 0) for n in notes], default=0) + 1
    new_note = {
        "id": next_id,
        "title": title,
        "content": data.get("content", "").strip(),
        "category": data.get("category", "General"),
        "color": data.get("color", "#6366F1"),
        "updated_at": datetime.now().isoformat()
    }
    notes.insert(0, new_note)
    save_notes(notes)
    log_activity("created", f"Note: {title}", item_type="note")

    return jsonify({"success": True, "note": new_note, "message": "Note created."}), 201


@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json() or {}
    notes = get_notes()
    for note in notes:
        if note.get("id") == note_id:
            if "title" in data:
                note["title"] = data["title"].strip()
            if "content" in data:
                note["content"] = data["content"].strip()
            if "category" in data:
                note["category"] = data["category"]
            if "color" in data:
                note["color"] = data["color"]
            note["updated_at"] = datetime.now().isoformat()
            save_notes(notes)
            return jsonify({"success": True, "note": note, "message": "Note updated."})
    return jsonify({"success": False, "error": "Note not found."}), 404


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    notes = get_notes()
    for i, note in enumerate(notes):
        if note.get("id") == note_id:
            title = note.get("title", "")
            notes.pop(i)
            save_notes(notes)
            log_activity("deleted", f"Note: {title}", item_type="note")
            return jsonify({"success": True, "message": "Note deleted."})
    return jsonify({"success": False, "error": "Note not found."}), 404


# ==============================================================================
# ACTIVITY API
# ==============================================================================

@app.route("/api/activity", methods=["GET"])
def get_activities():
    activities = get_activity()
    return jsonify({"success": True, "activities": activities})


# ==============================================================================
# RUN SERVER
# ==============================================================================

def run_app(port=5000, debug=False):
    print(f" * Starting Minto Workspace on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=debug)


if __name__ == "__main__":
    run_app(debug=True)
