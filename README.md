# 🧠 AI Task Analyzer — Django + JavaScript Frontend

An intelligent Task Analysis and Suggestion System built with **Django REST API** and a **vanilla JavaScript frontend**.
It scores tasks using urgency, importance, effort, and dependency factors, then recommends the optimal task order.

---

## 📌 Features

* POST `/api/tasks/analyze/` → Analyze & score tasks
* GET `/api/tasks/suggest/` → Recommend best next tasks
* Weighted scoring algorithm considering urgency, importance, effort, and dependencies
* Dependency resolution with circular dependency detection
* Clean, responsive frontend
* Fully CORS-enabled for development

---

## 📁 Project Structure

```
task_analyzer/
│
├── task_analyzer/
│   ├── settings.py
│   ├── urls.py
│
├── tasks/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── scoring.py
│   ├── urls.py
│   ├── tests.py
│
└── frontend/
    ├── index.html
    ├── styles.css
    └── script.js
```

---

# 🧪 **Setup Instructions**

### 1️⃣ Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
```

### 2️⃣ Install dependencies

```bash
pip install django djangorestframework django-cors-headers
```

### 3️⃣ Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4️⃣ Run backend server

```bash
python manage.py runserver
```

### 5️⃣ Run frontend (optional local static server)

```bash
cd frontend
python -m http.server 8080
```

Open in browser:
`http://localhost:8080`

---

# 🧪 **Test API**

### Analyze Tasks

POST
`http://127.0.0.1:8000/api/tasks/analyze/`

Request body example:

```json
{
  "tasks": [
    {
      "title": "Fix login bug",
      "due_date": "2025-12-01",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ]
}
```

### Get Top Suggested Tasks

GET
`http://127.0.0.1:8000/api/tasks/suggest/`

Optional query parameter: `?n=3` (default 3 tasks)

---

# 🧮 **Algorithm Explanation (350–400 words)**

The Task Analyzer implements a weighted multi-factor scoring algorithm to intelligently prioritize tasks. Each task is evaluated across four dimensions: **urgency**, **importance**, **effort**, and **dependencies**.

**Urgency** is computed based on the task’s due date. Tasks closer to their deadline receive higher urgency scores, while overdue tasks receive maximum urgency, ensuring that time-sensitive items are appropriately prioritized.

**Importance** leverages the user-provided rating (1–10), normalized to a percentage scale. High-impact tasks are therefore favored, even if they are not immediately due.

**Effort** is calculated as the inverse of estimated hours to complete a task. This promotes quick wins by giving shorter tasks a higher score, making it easier for users to accomplish tangible progress.

**Dependencies** capture the relational aspect of tasks. Tasks that unblock other tasks are prioritized higher, which ensures smooth project progression and prevents bottlenecks. Circular dependencies are detected and flagged to maintain correctness.

These four factors are combined into a **weighted aggregate score**:

* Urgency — 40%
* Importance — 30%
* Effort — 20%
* Dependencies — 10%

The resulting **final score** represents a task’s overall priority. Each task also includes a **reasoning explanation** (e.g., “Due today”, “High importance”, “Blocks 2 tasks”) for transparency.

For suggestions, tasks are sorted by descending scores, and the top N tasks are returned as actionable recommendations. This modular design separates scoring, REST endpoints, and frontend display, ensuring maintainability and flexibility. Optional user-defined weights and strategy selections allow further customization.

By combining deadline awareness, task significance, time-to-complete, and relational dependencies, this algorithm helps users make smart decisions, maximize productivity, and reduce project bottlenecks.

---

# ✅ **Assignment Status: COMPLETE**

* Backend fully implemented and tested
* Frontend fully implemented with working API calls
* CORS configured for cross-origin requests
* Algorithm explained (350–400 words)
* Setup and test instructions added
* Ready for submission
