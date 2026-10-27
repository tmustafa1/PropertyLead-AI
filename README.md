# 🏢 PropertyLead AI — Real Estate Lead Management & Scoring System

> **A beginner-friendly, privacy-focused web application designed for real estate agents to organize leads, calculate explainable AI priority scores, track follow-ups, and auto-generate client communication drafts.**

---

## 🌟 Key Features

1. **📊 Executive Dashboard:**
   - Real-time KPIs: **Total Leads**, **New Leads**, **Interested Leads**, **Converted Deals**, and **Pipeline Conversion Rate (%)**.
   - Average budget and urgent task alerts for overdue and today's follow-ups.
   - Interactive visual breakdown by pipeline status, purchase timeline, and AI priority score distribution.

2. **👥 Complete Lead Management (CRUD):**
   - Store full client profiles: Name, Phone, Email, Property Preference, Location, Budget, Purchase Timeline, Pipeline Status, Next Follow-up Date, and Notes.
   - Live Search across name, phone, email, property, and notes.
   - Multi-parameter filters: filter by Lead Status, Purchase Timeline, and sort by budget, date, or name.
   - Dedicated Edit & Delete modal to update prospect profiles with instant database synchronization.

3. **🧠 100% Explainable AI Lead Priority Scoring Engine:**
   - Evaluates leads deterministically from **0 to 100** points.
   - Classifies prospects into **🔥 Hot Priority (70–100)**, **⚡ Warm Lead (40–69)**, or **❄️ Cold Lead (0–39)**.
   - Provides a transparent, itemized factor breakdown explaining exactly why points were awarded:
     - **Timeline Urgency (max 35 pts):** Immediate buyers (< 1 month) receive peak priority.
     - **Sales Pipeline Depth (max 30 pts):** Active negotiations and site tours score highest.
     - **Financial & Requirement Viability (max 20 pts):** Concrete budget declarations & location criteria.
     - **Contact Quality & Cadence (max 15 pts):** Omnichannel availability and follow-up urgency.
   - Provides concrete tactical recommendations for the agent (e.g. *"Schedule walkthrough immediately"*).

4. **📅 Follow-up Task Manager:**
   - Segregates tasks into **🚨 Overdue Follow-ups**, **📌 Due Today**, and **🗓️ Upcoming (Next 7 Days)**.
   - Keeps agents accountable so no high-value real estate deal goes cold.

5. **💬 Draft Message Studio (No Paid APIs Required):**
   - Heuristic and template-driven communication generator across **WhatsApp**, **SMS**, and **Email**.
   - Context-aware: personalizes recipient name, property type, location, and budget.
   - **One-click "Open in WhatsApp" button** with URL-encoded messages ready to send directly in WhatsApp Web or Desktop.

6. **🛡️ Privacy Safeguards & Data Validation:**
   - **Privacy Protection Mode toggle:** Masks customer phone numbers and emails on screen for screen-sharing or public workspace security.
   - Regex-based phone and email validation.
   - SQLite parameterized queries to safeguard against SQL injection.
   - Zero external third-party API keys or recurring costs.

---

## 📂 Project Architecture & File Explanation

| File | Purpose |
| :--- | :--- |
| **[`app.py`](file:///c:/Users/Admin/OneDrive/Desktop/New%20folder/app.py)** | **Main Streamlit User Interface.** Orchestrates sidebar navigation, metric cards, lead directory, add/edit forms, task lists, and visual charts. |
| **[`database.py`](file:///c:/Users/Admin/OneDrive/Desktop/New%20folder/database.py)** | **Database Management (SQLite).** Handles table creation, indexes, safe parameterized SQL queries (CRUD), KPI calculations, and sample data seeding. |
| **[`scoring.py`](file:///c:/Users/Admin/OneDrive/Desktop/New%20folder/scoring.py)** | **Explainable AI Scoring Engine.** Implements transparent feature weighting rules, returns score breakdown points, priority tier classification, and agent recommendations. |
| **[`messaging.py`](file:///c:/Users/Admin/OneDrive/Desktop/New%20folder/messaging.py)** | **Follow-up Communication Drafter.** Generates formatted WhatsApp, SMS, and Email text based on lead state with instant `wa.me` link generation. |
| **[`utils.py`](file:///c:/Users/Admin/OneDrive/Desktop/New%20folder/utils.py)** | **Utilities & Security.** Contains input format validation (phone, email, dates), currency formatting, and privacy masking functions. |
| **[`test_backend.py`](file:///c:/Users/Admin/OneDrive/Desktop/New%20folder/test_backend.py)** | **Automated Test Suite.** Verifies database CRUD, scoring accuracy, validation constraints, and messaging without needing a browser. |
| **[`run_app.bat`](file:///c:/Users/Admin/OneDrive/Desktop/New%20folder/run_app.bat)** | **Windows One-Click Launcher.** A quick double-clickable batch script to launch the app instantly. |
| **[`requirements.txt`](file:///c:/Users/Admin/OneDrive/Desktop/New%20folder/requirements.txt)** | **Package Dependencies.** Lists required Python libraries (`streamlit`, `pandas`). |

---

## 🚀 How to Run the Application

You can run PropertyLead AI using either of the two methods below:

### Method 1: One-Click Windows Launcher (Easiest)
Simply double-click the **`run_app.bat`** file located in the project folder, or run in PowerShell:
```powershell
.\run_app.bat
```

### Method 2: Direct Terminal Command
Open PowerShell or Command Prompt in the project folder and run:
```powershell
& "C:\Users\Admin\anaconda3\python.exe" -m streamlit run app.py
```
*(If your Anaconda or Python environment is already activated in your terminal, you can simply type: `streamlit run app.py`)*

Once started, Streamlit will automatically open your default browser at:
👉 **`http://localhost:8501`**

---

## 🧪 Testing with Sample Data

The application comes pre-loaded with **8 realistic real estate leads** representing different purchase scenarios (luxury apartments, suburban villas, commercial retail spaces, and plots), with varying budgets ($210k to $1.2M), and different follow-up statuses (overdue, today, upcoming, converted, and lost).

To reset or reload sample data at any time:
1. Navigate to **⚙️ Settings & Sample Data** in the left sidebar.
2. Click **🔄 Reload / Reset Sample Leads**.
3. All default test leads will be restored immediately!
