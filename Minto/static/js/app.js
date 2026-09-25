/**
 * MINTO - Modern SaaS Productivity Application
 * Interactive Frontend JavaScript
 */

// ==============================================================================
// GLOBAL STATE
// ==============================================================================
const state = {
  tasks: [],
  notes: [],
  activities: [],
  stats: null,
  currentView: "view-overview",
  taskTab: "all",
  filterPriority: "",
  filterCategory: "",
  sortOption: "due_date",
  searchQuery: "",
  viewMode: "list",
  calendarDate: new Date(),
  theme: localStorage.getItem("minto_theme") || "light",
  user: JSON.parse(localStorage.getItem("minto_user")) || {
    name: "Riddhi",
    email: "riddhi@minto.local",
    role: "Productivity Lead"
  },
  charts: {}
};

// ==============================================================================
// INITIALIZATION
// ==============================================================================
document.addEventListener("DOMContentLoaded", () => {
  applyTheme(state.theme);
  applyUserProfile();
  initSidebar();
  initNavigation();
  initSearch();
  initModals();

  // Initial Data Fetch
  loadAllData();

  // Re-render Lucide icons
  refreshIcons();
});

function refreshIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// ==============================================================================
// THEME & USER PROFILE
// ==============================================================================
function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.setAttribute("data-bs-theme", theme);
  localStorage.setItem("minto_theme", theme);

  const icon = document.getElementById("themeIcon");
  if (icon) {
    icon.setAttribute("data-lucide", theme === "dark" ? "sun" : "moon");
    refreshIcons();
  }

  // Re-draw charts with updated palette if available
  if (state.stats) {
    updateAnalyticsCharts(state.stats);
    updateDoughnutProgress(state.stats.completion_rate);
  }
}

function toggleTheme() {
  const newTheme = state.theme === "dark" ? "light" : "dark";
  applyTheme(newTheme);
  showToast(`Switched to ${newTheme} mode`, "info");
}

function applyUserProfile() {
  document.getElementById("sidebarUserName").textContent = state.user.name;
  document.getElementById("greetingHeader").textContent = `Good ${getTimeGreeting()}, ${state.user.name} 👋`;
  document.getElementById("menuUserName").textContent = state.user.name;
  document.getElementById("sidebarUserAvatar").textContent = state.user.name.charAt(0).toUpperCase();
  document.getElementById("topbarUserAvatar").textContent = state.user.name.charAt(0).toUpperCase();

  const nameInput = document.getElementById("settingsUserName");
  const emailInput = document.getElementById("settingsUserEmail");
  const roleInput = document.getElementById("settingsUserRole");
  if (nameInput) nameInput.value = state.user.name;
  if (emailInput) emailInput.value = state.user.email;
  if (roleInput) roleInput.value = state.user.role;

  // Format today's date
  const now = new Date();
  const options = { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' };
  document.getElementById("currentDateDisplay").textContent = now.toLocaleDateString('en-US', options);
}

function getTimeGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "morning";
  if (hour < 17) return "afternoon";
  return "evening";
}

function saveProfileSettings() {
  const name = document.getElementById("settingsUserName").value.trim() || "Riddhi";
  const email = document.getElementById("settingsUserEmail").value.trim() || "riddhi@minto.local";
  const role = document.getElementById("settingsUserRole").value.trim() || "Productivity Lead";

  state.user = { name, email, role };
  localStorage.setItem("minto_user", JSON.stringify(state.user));
  applyUserProfile();
  showToast("Profile settings saved successfully.", "success");
}

// ==============================================================================
// NAVIGATION & SIDEBAR
// ==============================================================================
function initSidebar() {
  const sidebar = document.getElementById("appSidebar");
  const collapseBtn = document.getElementById("sidebarCollapseBtn");
  const mobileToggle = document.getElementById("mobileMenuToggle");

  if (collapseBtn) {
    collapseBtn.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  if (mobileToggle) {
    mobileToggle.addEventListener("click", () => {
      sidebar.classList.toggle("show-mobile");
    });
  }

  // Close mobile sidebar when clicking outside
  document.addEventListener("click", (e) => {
    if (window.innerWidth <= 768 && sidebar.classList.contains("show-mobile")) {
      if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
        sidebar.classList.remove("show-mobile");
      }
    }
  });

  const themeBtn = document.getElementById("themeToggleBtn");
  if (themeBtn) {
    themeBtn.addEventListener("click", toggleTheme);
  }
}

function initNavigation() {
  const navLinks = document.querySelectorAll(".nav-item-link");
  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetView = link.getAttribute("data-view");
      if (targetView) {
        switchView(targetView);
      }
    });
  });

  const quickAdd = document.getElementById("btnQuickAddTask");
  const topbarAdd = document.getElementById("topbarAddTaskBtn");
  if (quickAdd) quickAdd.addEventListener("click", () => openAddTaskModal());
  if (topbarAdd) topbarAdd.addEventListener("click", () => openAddTaskModal());
}

function switchView(viewId) {
  state.currentView = viewId;

  // Toggle active nav links
  document.querySelectorAll(".nav-item-link").forEach((link) => {
    if (link.getAttribute("data-view") === viewId) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });

  // Toggle view panes
  document.querySelectorAll(".view-pane").forEach((pane) => {
    pane.classList.remove("active");
  });
  const targetPane = document.getElementById(viewId);
  if (targetPane) {
    targetPane.classList.add("active");
  }

  // Close mobile sidebar on navigation
  const sidebar = document.getElementById("appSidebar");
  if (sidebar) sidebar.classList.remove("show-mobile");

  // Re-render specific views if needed
  if (viewId === "view-calendar") {
    renderCalendar();
  } else if (viewId === "view-analytics") {
    fetchStats();
  } else if (viewId === "view-projects") {
    renderProjectsView();
  } else if (viewId === "view-notes") {
    renderNotesView();
  }

  refreshIcons();
}

function initSearch() {
  const input = document.getElementById("globalSearchInput");
  if (input) {
    input.addEventListener("input", (e) => {
      state.searchQuery = e.target.value.trim().toLowerCase();
      if (state.currentView !== "view-tasks") {
        switchView("view-tasks");
      }
      renderMyTasksView();
    });
  }
}

// ==============================================================================
// DATA FETCHING
// ==============================================================================
async function loadAllData() {
  await Promise.all([
    fetchTasks(),
    fetchStats(),
    fetchNotes(),
    fetchActivity()
  ]);
}

async function fetchTasks() {
  try {
    const res = await fetch("/api/tasks");
    const data = await res.json();
    if (data.success) {
      state.tasks = data.tasks;
      document.getElementById("navTaskCount").textContent = state.tasks.length;
      renderDashboardOverview();
      renderMyTasksView();
      renderCalendar();
      renderProjectsView();
    }
  } catch (err) {
    console.error("Error fetching tasks:", err);
  }
}

async function fetchStats() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();
    if (data.success) {
      state.stats = data.stats;
      updateKpiCards(data.stats);
      updateDoughnutProgress(data.stats.completion_rate);
      updateAnalyticsCharts(data.stats);
    }
  } catch (err) {
    console.error("Error fetching stats:", err);
  }
}

async function fetchNotes() {
  try {
    const res = await fetch("/api/notes");
    const data = await res.json();
    if (data.success) {
      state.notes = data.notes;
      document.getElementById("navNotesCount").textContent = state.notes.length;
      renderNotesView();
    }
  } catch (err) {
    console.error("Error fetching notes:", err);
  }
}

async function fetchActivity() {
  try {
    const res = await fetch("/api/activity");
    const data = await res.json();
    if (data.success) {
      state.activities = data.activities;
      renderActivityFeed();
    }
  } catch (err) {
    console.error("Error fetching activity:", err);
  }
}

// ==============================================================================
// DASHBOARD OVERVIEW RENDERING
// ==============================================================================
function updateKpiCards(stats) {
  document.getElementById("kpiTotal").textContent = stats.total_tasks;
  document.getElementById("kpiCompleted").textContent = stats.completed_tasks;
  document.getElementById("kpiPending").textContent = stats.pending_tasks;
  document.getElementById("kpiOverdue").textContent = stats.overdue_tasks;
  document.getElementById("kpiRate").textContent = `${stats.completion_rate}%`;

  const quoteSub = document.getElementById("motivationalSubtitle");
  if (quoteSub && stats.motivational_quote) {
    quoteSub.textContent = stats.motivational_quote;
  }

  const quoteCard = document.getElementById("progressQuoteCard");
  if (quoteCard && stats.motivational_quote) {
    quoteCard.textContent = `“${stats.motivational_quote}”`;
  }

  const sidebarQuote = document.getElementById("sidebarQuoteText");
  if (sidebarQuote && stats.motivational_quote) {
    sidebarQuote.textContent = `“${stats.motivational_quote}”`;
  }

  const lineFill = document.getElementById("progressLineFill");
  if (lineFill) {
    lineFill.style.width = `${stats.completion_rate}%`;
  }
}

function renderDashboardOverview() {
  // 1. Today's Focus Tasks (Pending high priority or today's tasks)
  const todayStr = new Date().toISOString().split("T")[0];
  const focusContainer = document.getElementById("todayFocusList");
  focusContainer.innerHTML = "";

  // Prioritize active tasks, especially today's or high priority
  const focusTasks = state.tasks
    .filter(t => !t.completed || t.due_date === todayStr)
    .slice(0, 5);

  if (focusTasks.length === 0) {
    focusContainer.innerHTML = `
      <div class="empty-state-box py-4">
        <div class="empty-state-icon" style="width: 44px; height: 44px;">
          <i data-lucide="sparkles" style="width: 22px;"></i>
        </div>
        <h6 class="fw-bold mb-1">Your Focus is Clear!</h6>
        <p class="small text-muted mb-3">No pending tasks for today. Take a breather or plan ahead.</p>
        <button class="btn btn-sm btn-primary" onclick="openAddTaskModal()">
          <i data-lucide="plus" style="width: 14px;"></i> Add a Task
        </button>
      </div>
    `;
  } else {
    focusTasks.forEach(task => {
      focusContainer.appendChild(createTaskCardElement(task));
    });
  }

  // 2. Upcoming Schedule List
  const scheduleContainer = document.getElementById("upcomingScheduleList");
  scheduleContainer.innerHTML = "";

  const upcomingTasks = state.tasks
    .filter(t => t.due_date && !t.completed)
    .sort((a, b) => a.due_date.localeCompare(b.due_date))
    .slice(0, 4);

  if (upcomingTasks.length === 0) {
    scheduleContainer.innerHTML = `
      <div class="text-center py-3 text-muted small">
        <i data-lucide="calendar-check" style="width: 28px; margin-bottom: 6px; opacity: 0.5;"></i>
        <div>No upcoming deadlines.</div>
      </div>
    `;
  } else {
    upcomingTasks.forEach(task => {
      const item = document.createElement("div");
      item.className = "timeline-item";
      const relDate = formatRelativeDate(task.due_date);
      item.innerHTML = `
        <div class="timeline-date">${relDate.text} ${task.due_time ? '• ' + task.due_time : ''}</div>
        <div class="timeline-title">${escapeHtml(task.title)}</div>
        <div class="small text-muted">${escapeHtml(task.category || 'General')}</div>
      `;
      scheduleContainer.appendChild(item);
    });
  }

  refreshIcons();
}

function renderActivityFeed() {
  const container = document.getElementById("recentActivityList");
  if (!container) return;
  container.innerHTML = "";

  if (state.activities.length === 0) {
    container.innerHTML = `
      <div class="text-center py-3 text-muted small">
        No recent activities logged yet.
      </div>
    `;
    return;
  }

  state.activities.slice(0, 5).forEach(act => {
    const item = document.createElement("div");
    item.className = "activity-feed-item";

    let iconName = "check-circle";
    let actionLabel = "completed";
    if (act.action === "created") {
      iconName = "plus-circle";
      actionLabel = "created";
    } else if (act.action === "updated") {
      iconName = "edit-3";
      actionLabel = "updated";
    } else if (act.action === "deleted") {
      iconName = "trash-2";
      actionLabel = "deleted";
    }

    const timeAgo = formatTimeAgo(act.timestamp);

    item.innerHTML = `
      <div class="activity-feed-icon">
        <i data-lucide="${iconName}" style="width: 14px; height: 14px;"></i>
      </div>
      <div class="activity-feed-text">
        <span>You <strong>${actionLabel}</strong> "${escapeHtml(act.title)}"</span>
        <div class="activity-time">${timeAgo}</div>
      </div>
    `;
    container.appendChild(item);
  });

  refreshIcons();
}

// ==============================================================================
// TASK CARD ELEMENT BUILDER
// ==============================================================================
function createTaskCardElement(task) {
  const card = document.createElement("div");
  card.className = `task-item-card ${task.completed ? "is-completed" : ""}`;
  card.id = `task-card-${task.id}`;

  const relDate = formatRelativeDate(task.due_date);
  const prioClass = task.priority === "High" ? "pill-priority-high" : (task.priority === "Low" ? "pill-priority-low" : "pill-priority-med");
  const dueClass = relDate.isOverdue && !task.completed ? "pill-due overdue" : "pill-due";

  card.innerHTML = `
    <!-- Checkbox -->
    <div class="custom-task-checkbox ${task.completed ? "checked" : ""}" 
         onclick="toggleTaskStatus(${task.id})" title="Toggle status">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
    </div>

    <!-- Body -->
    <div class="task-item-body">
      <div class="task-title-text">${escapeHtml(task.title)}</div>
      ${task.description ? `<div class="task-desc-text">${escapeHtml(task.description)}</div>` : ""}
      
      <div class="task-meta-pills">
        <!-- Priority -->
        <span class="pill-badge ${prioClass}">
          <span>●</span> ${escapeHtml(task.priority || "Medium")}
        </span>

        <!-- Category -->
        <span class="pill-badge pill-category">
          <i data-lucide="tag" style="width: 11px;"></i> ${escapeHtml(task.category || "General")}
        </span>

        <!-- Due Date -->
        ${relDate.text ? `
          <span class="pill-badge ${dueClass}">
            <i data-lucide="${relDate.isOverdue ? 'alert-circle' : 'calendar'}" style="width: 11px;"></i> 
            ${relDate.text} ${task.due_time ? 'at ' + task.due_time : ''}
          </span>
        ` : ""}

        <!-- Status -->
        <span class="pill-badge pill-status">
          ${escapeHtml(task.status || (task.completed ? "Completed" : "To Do"))}
        </span>
      </div>
    </div>

    <!-- Quick Action Dropdown -->
    <div class="dropdown">
      <button class="task-actions-btn" data-bs-toggle="dropdown" aria-expanded="false" title="Options">
        <i data-lucide="more-horizontal" style="width: 16px;"></i>
      </button>
      <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 p-1">
        <li>
          <a class="dropdown-item py-1 small" href="#" onclick="openEditTaskModal(${task.id}); return false;">
            <i data-lucide="edit-2" class="me-2" style="width: 14px;"></i> Edit
          </a>
        </li>
        <li>
          <a class="dropdown-item py-1 small text-danger" href="#" onclick="promptDeleteTask(${task.id}); return false;">
            <i data-lucide="trash-2" class="me-2" style="width: 14px;"></i> Delete
          </a>
        </li>
      </ul>
    </div>
  `;

  return card;
}

// ==============================================================================
// MY TASKS VIEW
// ==============================================================================
function setTaskTab(tab) {
  state.taskTab = tab;
  document.querySelectorAll(".tab-pill-btn").forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-tab") === tab);
  });
  renderMyTasksView();
}

function setViewMode(mode) {
  state.viewMode = mode;
  document.getElementById("btnModeList").classList.toggle("active", mode === "list");
  document.getElementById("btnModeGrid").classList.toggle("active", mode === "grid");
  renderMyTasksView();
}

function applyFilters() {
  state.filterPriority = document.getElementById("filterPriority").value;
  state.filterCategory = document.getElementById("filterCategory").value;
  state.sortOption = document.getElementById("sortTasks").value;
  renderMyTasksView();
}

function renderMyTasksView() {
  const container = document.getElementById("myTasksContainer");
  if (!container) return;
  container.innerHTML = "";

  if (state.viewMode === "grid") {
    container.className = "tasks-grid-view";
  } else {
    container.className = "focus-task-list";
  }

  const todayStr = new Date().toISOString().split("T")[0];

  // 1. Filter Tasks
  let filtered = state.tasks.filter(t => {
    // Search query
    if (state.searchQuery) {
      const match = (t.title || "").toLowerCase().includes(state.searchQuery) ||
                    (t.description || "").toLowerCase().includes(state.searchQuery) ||
                    (t.category || "").toLowerCase().includes(state.searchQuery);
      if (!match) return false;
    }

    // Tabs
    if (state.taskTab === "today" && t.due_date !== todayStr) return false;
    if (state.taskTab === "upcoming" && (!t.due_date || t.due_date <= todayStr || t.completed)) return false;
    if (state.taskTab === "completed" && !t.completed) return false;
    if (state.taskTab === "overdue" && (!t.due_date || t.due_date >= todayStr || t.completed)) return false;

    // Dropdowns
    if (state.filterPriority && t.priority !== state.filterPriority) return false;
    if (state.filterCategory && t.category !== state.filterCategory) return false;

    return true;
  });

  // 2. Sort Tasks
  filtered.sort((a, b) => {
    if (state.sortOption === "priority") {
      const weight = { "High": 3, "Medium": 2, "Low": 1 };
      return (weight[b.priority] || 0) - (weight[a.priority] || 0);
    } else if (state.sortOption === "title") {
      return (a.title || "").localeCompare(b.title || "");
    } else {
      // Due date (empty at end)
      if (!a.due_date) return 1;
      if (!b.due_date) return -1;
      return a.due_date.localeCompare(b.due_date);
    }
  });

  // 3. Render
  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state-box w-100">
        <div class="empty-state-icon">
          <i data-lucide="inbox" style="width: 28px; height: 28px;"></i>
        </div>
        <h5 class="empty-state-title">No tasks found</h5>
        <p class="empty-state-desc">There are no tasks matching the selected filters or search query.</p>
        <button class="btn btn-primary btn-sm" onclick="openAddTaskModal()">
          <i data-lucide="plus" style="width: 14px;"></i> Create Task
        </button>
      </div>
    `;
  } else {
    filtered.forEach(task => {
      container.appendChild(createTaskCardElement(task));
    });
  }

  refreshIcons();
}

// ==============================================================================
// TASK CRUD & ACTIONS
// ==============================================================================
async function toggleTaskStatus(taskId) {
  try {
    const res = await fetch(`/api/tasks/${taskId}/toggle`, { method: "PATCH" });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, "success");
      loadAllData();
    }
  } catch (err) {
    console.error("Error toggling task:", err);
  }
}

function openAddTaskModal(presetDate = "") {
  document.getElementById("taskFormId").value = "";
  document.getElementById("taskForm").reset();
  document.getElementById("taskModalTitle").innerHTML = `
    <i data-lucide="plus-circle" class="me-2" style="width: 20px; color: var(--primary);"></i>
    Create New Task
  `;
  document.getElementById("btnSaveTask").textContent = "Create Task";

  if (presetDate) {
    document.getElementById("taskDueDateInput").value = presetDate;
  }

  const modal = new bootstrap.Modal(document.getElementById("taskModal"));
  modal.show();
  refreshIcons();
}

function openEditTaskModal(taskId) {
  const task = state.tasks.find(t => t.id === taskId);
  if (!task) return;

  document.getElementById("taskFormId").value = task.id;
  document.getElementById("taskTitleInput").value = task.title || "";
  document.getElementById("taskDescInput").value = task.description || "";
  document.getElementById("taskDueDateInput").value = task.due_date || "";
  document.getElementById("taskDueTimeInput").value = task.due_time || "";
  document.getElementById("taskPriorityInput").value = task.priority || "Medium";
  document.getElementById("taskCategoryInput").value = task.category || "General";
  document.getElementById("taskStatusInput").value = task.status || (task.completed ? "Completed" : "To Do");
  document.getElementById("taskReminderCheck").checked = !!task.reminder;

  document.getElementById("taskModalTitle").innerHTML = `
    <i data-lucide="edit-3" class="me-2" style="width: 20px; color: var(--primary);"></i>
    Edit Task
  `;
  document.getElementById("btnSaveTask").textContent = "Save Changes";

  const modal = new bootstrap.Modal(document.getElementById("taskModal"));
  modal.show();
  refreshIcons();
}

async function saveTaskForm(event) {
  event.preventDefault();
  const id = document.getElementById("taskFormId").value;
  const title = document.getElementById("taskTitleInput").value.trim();

  if (!title) {
    document.getElementById("taskTitleInput").classList.add("is-invalid");
    return;
  }
  document.getElementById("taskTitleInput").classList.remove("is-invalid");

  const payload = {
    title: title,
    description: document.getElementById("taskDescInput").value.trim(),
    due_date: document.getElementById("taskDueDateInput").value.trim(),
    due_time: document.getElementById("taskDueTimeInput").value.trim(),
    priority: document.getElementById("taskPriorityInput").value,
    category: document.getElementById("taskCategoryInput").value,
    status: document.getElementById("taskStatusInput").value,
    reminder: document.getElementById("taskReminderCheck").checked
  };

  try {
    let res;
    if (id) {
      res = await fetch(`/api/tasks/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }

    const data = await res.json();
    if (data.success) {
      bootstrap.Modal.getInstance(document.getElementById("taskModal")).hide();
      showToast(data.message, "success");
      loadAllData();
    } else {
      showToast(data.error || "Failed to save task.", "danger");
    }
  } catch (err) {
    console.error("Save error:", err);
    showToast("Error saving task.", "danger");
  }
}

let pendingDeleteId = null;
function promptDeleteTask(taskId) {
  pendingDeleteId = taskId;
  const task = state.tasks.find(t => t.id === taskId);
  const preview = document.getElementById("deleteTaskTitlePreview");
  if (preview && task) {
    preview.textContent = `Are you sure you want to delete "${task.title}"?`;
  }
  const modal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"));
  modal.show();
}

function initModals() {
  const confirmBtn = document.getElementById("btnConfirmDelete");
  if (confirmBtn) {
    confirmBtn.addEventListener("click", async () => {
      if (!pendingDeleteId) return;
      try {
        const res = await fetch(`/api/tasks/${pendingDeleteId}`, { method: "DELETE" });
        const data = await res.json();
        if (data.success) {
          bootstrap.Modal.getInstance(document.getElementById("deleteConfirmModal")).hide();
          showToast(`Task "${data.title}" deleted.`, "warning");
          loadAllData();
        }
      } catch (err) {
        console.error("Delete error:", err);
      } finally {
        pendingDeleteId = null;
      }
    });
  }
}

function setModalDatePreset(daysAhead) {
  const d = new Date();
  d.setDate(d.getDate() + daysAhead);
  document.getElementById("taskDueDateInput").value = d.toISOString().split("T")[0];
}

function clearModalDate() {
  document.getElementById("taskDueDateInput").value = "";
  document.getElementById("taskDueTimeInput").value = "";
}

// ==============================================================================
// CALENDAR VIEW
// ==============================================================================
function navigateCalendar(offset) {
  if (offset === 0) {
    state.calendarDate = new Date();
  } else {
    state.calendarDate.setMonth(state.calendarDate.getMonth() + offset);
  }
  renderCalendar();
}

function renderCalendar() {
  const grid = document.getElementById("calendarGrid");
  if (!grid) return;
  grid.innerHTML = "";

  const year = state.calendarDate.getFullYear();
  const month = state.calendarDate.getMonth();
  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  document.getElementById("calendarMonthTitle").textContent = `${monthNames[month]} ${year}`;

  // Day Headers
  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  dayNames.forEach(d => {
    const h = document.createElement("div");
    h.className = "calendar-header-day";
    h.textContent = d;
    grid.appendChild(h);
  });

  const firstDayIndex = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const prevMonthDays = new Date(year, month, 0).getDate();
  const todayStr = new Date().toISOString().split("T")[0];

  // Previous month trailing days
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    const dayNum = prevMonthDays - i;
    const cell = document.createElement("div");
    cell.className = "calendar-cell is-other-month";
    cell.innerHTML = `<div class="calendar-cell-date">${dayNum}</div>`;
    grid.appendChild(cell);
  }

  // Current month days
  for (let day = 1; day <= daysInMonth; day++) {
    const cellDateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    const cell = document.createElement("div");
    cell.className = `calendar-cell ${cellDateStr === todayStr ? "is-today" : ""}`;
    cell.onclick = () => openAddTaskModal(cellDateStr);

    let html = `<div class="calendar-cell-date">${day}</div>`;

    // Tasks due on this date
    const tasksOnDay = state.tasks.filter(t => t.due_date === cellDateStr);
    tasksOnDay.slice(0, 3).forEach(t => {
      html += `
        <div class="calendar-task-chip ${t.completed ? 'text-decoration-line-through opacity-50' : ''}" title="${escapeHtml(t.title)}">
          ● ${escapeHtml(t.title)}
        </div>
      `;
    });
    if (tasksOnDay.length > 3) {
      html += `<div class="small text-muted" style="font-size: 0.65rem;">+${tasksOnDay.length - 3} more</div>`;
    }

    cell.innerHTML = html;
    grid.appendChild(cell);
  }

  // Next month leading days to complete grid
  const totalCells = firstDayIndex + daysInMonth;
  const nextDays = (7 - (totalCells % 7)) % 7;
  for (let i = 1; i <= nextDays; i++) {
    const cell = document.createElement("div");
    cell.className = "calendar-cell is-other-month";
    cell.innerHTML = `<div class="calendar-cell-date">${i}</div>`;
    grid.appendChild(cell);
  }
}

// ==============================================================================
// PROJECTS VIEW
// ==============================================================================
function renderProjectsView() {
  const container = document.getElementById("projectsCardsRow");
  if (!container) return;
  container.innerHTML = "";

  const categories = [
    { name: "Study", icon: "book-open", color: "var(--cat-study)" },
    { name: "Project", icon: "code-2", color: "var(--cat-project)" },
    { name: "Work", icon: "briefcase", color: "var(--cat-work)" },
    { name: "Personal", icon: "heart", color: "var(--cat-personal)" },
    { name: "General", icon: "folder", color: "var(--cat-general)" }
  ];

  categories.forEach(cat => {
    const catTasks = state.tasks.filter(t => (t.category || "General") === cat.name);
    const total = catTasks.length;
    const completed = catTasks.filter(t => t.completed).length;
    const rate = total > 0 ? Math.round((completed / total) * 100) : 0;

    const col = document.createElement("div");
    col.className = "col-md-6 col-lg-4";
    col.innerHTML = `
      <div class="saas-card h-100">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div class="d-flex align-items-center gap-2">
            <div class="kpi-icon-pill" style="background-color: var(--primary-light); color: ${cat.color};">
              <i data-lucide="${cat.icon}" style="width: 18px;"></i>
            </div>
            <h5 class="fw-bold mb-0">${cat.name}</h5>
          </div>
          <span class="badge bg-secondary-subtle text-secondary">${total} Tasks</span>
        </div>

        <div class="mb-3">
          <div class="d-flex justify-content-between small text-muted mb-1">
            <span>Progress</span>
            <span class="fw-bold">${rate}%</span>
          </div>
          <div class="progress" style="height: 6px;">
            <div class="progress-bar bg-primary" role="progressbar" style="width: ${rate}%;"></div>
          </div>
        </div>

        <div class="small text-muted mb-3">
          ${completed} completed • ${total - completed} pending
        </div>

        <button class="btn btn-outline-primary btn-sm w-100" onclick="filterByProject('${cat.name}')">
          View Tasks
        </button>
      </div>
    `;
    container.appendChild(col);
  });

  refreshIcons();
}

function filterByProject(catName) {
  document.getElementById("filterCategory").value = catName;
  state.filterCategory = catName;
  switchView("view-tasks");
  applyFilters();
}

// ==============================================================================
// NOTES VIEW
// ==============================================================================
function renderNotesView() {
  const container = document.getElementById("notesGridContainer");
  if (!container) return;
  container.innerHTML = "";

  if (state.notes.length === 0) {
    container.innerHTML = `
      <div class="empty-state-box w-100">
        <div class="empty-state-icon">
          <i data-lucide="file-text" style="width: 28px;"></i>
        </div>
        <h5 class="empty-state-title">No notes yet</h5>
        <p class="empty-state-desc">Capture thoughts, quick memos, and lecture highlights here.</p>
        <button class="btn btn-primary btn-sm" onclick="openNoteModal()">
          <i data-lucide="plus" style="width: 14px;"></i> Create Note
        </button>
      </div>
    `;
    return;
  }

  state.notes.forEach(note => {
    const card = document.createElement("div");
    card.className = "note-card";
    card.style.borderTopColor = note.color || "#6366F1";

    card.innerHTML = `
      <div>
        <div class="d-flex justify-content-between align-items-start">
          <div class="note-title">${escapeHtml(note.title)}</div>
          <div class="dropdown">
            <button class="btn btn-link btn-sm text-muted p-0" data-bs-toggle="dropdown">
              <i data-lucide="more-vertical" style="width: 15px;"></i>
            </button>
            <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0">
              <li><a class="dropdown-item small" href="#" onclick="openNoteModal(${note.id}); return false;">Edit</a></li>
              <li><a class="dropdown-item small text-danger" href="#" onclick="deleteNote(${note.id}); return false;">Delete</a></li>
            </ul>
          </div>
        </div>
        <div class="note-content">${escapeHtml(note.content || "")}</div>
      </div>
      <div class="note-footer">
        <span class="badge bg-secondary-subtle text-secondary">${escapeHtml(note.category || 'General')}</span>
        <span>${formatTimeAgo(note.updated_at)}</span>
      </div>
    `;
    container.appendChild(card);
  });

  refreshIcons();
}

function openNoteModal(noteId = null) {
  const form = document.getElementById("noteForm");
  form.reset();
  document.getElementById("noteFormId").value = "";

  if (noteId) {
    const note = state.notes.find(n => n.id === noteId);
    if (note) {
      document.getElementById("noteFormId").value = note.id;
      document.getElementById("noteTitleInput").value = note.title;
      document.getElementById("noteContentInput").value = note.content || "";
      document.getElementById("noteCategoryInput").value = note.category || "General";
      document.getElementById("noteColorInput").value = note.color || "#6366F1";
      document.getElementById("noteModalTitle").textContent = "Edit Note";
    }
  } else {
    document.getElementById("noteModalTitle").textContent = "New Note";
  }

  const modal = new bootstrap.Modal(document.getElementById("noteModal"));
  modal.show();
}

async function saveNoteForm(event) {
  event.preventDefault();
  const id = document.getElementById("noteFormId").value;
  const payload = {
    title: document.getElementById("noteTitleInput").value.trim(),
    content: document.getElementById("noteContentInput").value.trim(),
    category: document.getElementById("noteCategoryInput").value,
    color: document.getElementById("noteColorInput").value
  };

  try {
    let res;
    if (id) {
      res = await fetch(`/api/notes/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }

    const data = await res.json();
    if (data.success) {
      bootstrap.Modal.getInstance(document.getElementById("noteModal")).hide();
      showToast(data.message, "success");
      fetchNotes();
      fetchActivity();
    }
  } catch (err) {
    console.error("Save note error:", err);
  }
}

async function deleteNote(noteId) {
  try {
    const res = await fetch(`/api/notes/${noteId}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      showToast("Note deleted.", "warning");
      fetchNotes();
      fetchActivity();
    }
  } catch (err) {
    console.error("Delete note error:", err);
  }
}

// ==============================================================================
// CHARTS & ANALYTICS
// ==============================================================================
function updateDoughnutProgress(completionRate) {
  const canvas = document.getElementById("progressDoughnutChart");
  if (!canvas) return;

  document.getElementById("doughnutCenterPct").textContent = `${completionRate}%`;

  if (state.charts.doughnut) {
    state.charts.doughnut.destroy();
  }

  const isDark = state.theme === "dark";
  const emptyColor = isDark ? "#232938" : "#EEF0F6";
  const fillColor = "#4F46E5";

  state.charts.doughnut = new Chart(canvas, {
    type: "doughnut",
    data: {
      datasets: [{
        data: [completionRate, 100 - completionRate],
        backgroundColor: [fillColor, emptyColor],
        borderWidth: 0,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "78%",
      plugins: {
        tooltip: { enabled: false }
      }
    }
  });
}

function updateAnalyticsCharts(stats) {
  const isDark = state.theme === "dark";
  const textColor = isDark ? "#8E95A5" : "#64748B";
  const gridColor = isDark ? "#232938" : "#E9EAF0";

  // 1. Weekly Activity Trend
  const ctxWeekly = document.getElementById("chartWeeklyTrend");
  if (ctxWeekly && stats.weekly_data) {
    if (state.charts.weekly) state.charts.weekly.destroy();
    state.charts.weekly = new Chart(ctxWeekly, {
      type: "bar",
      data: {
        labels: stats.weekly_data.labels,
        datasets: [
          {
            label: "Due Tasks",
            data: stats.weekly_data.created,
            backgroundColor: "rgba(99, 102, 241, 0.4)",
            borderRadius: 6
          },
          {
            label: "Completed",
            data: stats.weekly_data.completed,
            backgroundColor: "#10B981",
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "top", labels: { color: textColor } } },
        scales: {
          x: { grid: { display: false }, ticks: { color: textColor } },
          y: { grid: { color: gridColor }, ticks: { color: textColor, stepSize: 1 } }
        }
      }
    });
  }

  // 2. Status Breakdown
  const ctxStatus = document.getElementById("chartStatusBreakdown");
  if (ctxStatus && stats.status_counts) {
    if (state.charts.status) state.charts.status.destroy();
    state.charts.status = new Chart(ctxStatus, {
      type: "doughnut",
      data: {
        labels: Object.keys(stats.status_counts),
        datasets: [{
          data: Object.values(stats.status_counts),
          backgroundColor: ["#6366F1", "#3B82F6", "#10B981", "#EF4444", "#F59E0B"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "right", labels: { color: textColor } } }
      }
    });
  }

  // 3. Priority Breakdown
  const ctxPriority = document.getElementById("chartPriorityBreakdown");
  if (ctxPriority && stats.priority_counts) {
    if (state.charts.priority) state.charts.priority.destroy();
    state.charts.priority = new Chart(ctxPriority, {
      type: "bar",
      data: {
        labels: ["High", "Medium", "Low"],
        datasets: [{
          label: "Tasks",
          data: [stats.priority_counts.High || 0, stats.priority_counts.Medium || 0, stats.priority_counts.Low || 0],
          backgroundColor: ["#EF4444", "#F59E0B", "#10B981"],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: textColor } },
          y: { grid: { color: gridColor }, ticks: { color: textColor, stepSize: 1 } }
        }
      }
    });
  }

  // 4. Category Breakdown
  const ctxCategory = document.getElementById("chartCategoryBreakdown");
  if (ctxCategory && stats.category_counts) {
    if (state.charts.category) state.charts.category.destroy();
    state.charts.category = new Chart(ctxCategory, {
      type: "pie",
      data: {
        labels: Object.keys(stats.category_counts),
        datasets: [{
          data: Object.values(stats.category_counts),
          backgroundColor: ["#6366F1", "#0EA5E9", "#8B5CF6", "#EC4899", "#64748B"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "right", labels: { color: textColor } } }
      }
    });
  }
}

// ==============================================================================
// UTILITIES: TOASTS, DATE FORMATTING, EXPORT
// ==============================================================================
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `saas-toast border-${type}`;

  let icon = "check-circle";
  if (type === "danger") icon = "alert-circle";
  if (type === "warning") icon = "alert-triangle";
  if (type === "info") icon = "info";

  toast.innerHTML = `
    <i data-lucide="${icon}" class="text-${type}" style="width: 18px;"></i>
    <span>${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);
  refreshIcons();

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

function formatRelativeDate(dateStr) {
  if (!dateStr) return { text: "", isOverdue: false };
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const parts = dateStr.split("-");
  const due = new Date(parts[0], parts[1] - 1, parts[2]);

  const diffTime = due.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return { text: "Overdue", isOverdue: true };
  } else if (diffDays === 0) {
    return { text: "Today", isOverdue: false };
  } else if (diffDays === 1) {
    return { text: "Tomorrow", isOverdue: false };
  } else {
    const month = due.toLocaleString('default', { month: 'short' });
    return { text: `${month} ${due.getDate()}`, isOverdue: false };
  }
}

function formatTimeAgo(isoString) {
  if (!isoString) return "";
  const date = new Date(isoString);
  const now = new Date();
  const diffSec = Math.floor((now - date) / 1000);

  if (diffSec < 60) return "Just now";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  return `${Math.floor(diffSec / 86400)}d ago`;
}

function exportTasksJson() {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state.tasks, null, 2));
  const downloadAnchor = document.createElement("a");
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", "minto_tasks_export.json");
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
  showToast("Tasks exported to JSON file.", "success");
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
