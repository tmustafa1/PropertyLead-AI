"""
database.py - SQLite Database operations for PropertyLead AI
Handles connection management, schema initialization, parameterized CRUD operations,
and sample data population.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leads.db")


def get_connection():
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the SQLite database schema if not present."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                property_preference TEXT NOT NULL,
                location_preference TEXT,
                budget REAL NOT NULL DEFAULT 0,
                purchase_timeline TEXT NOT NULL,
                lead_status TEXT NOT NULL,
                next_followup_date TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        # Indexes for fast searching and filtering
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(lead_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_followup ON leads(next_followup_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_timeline ON leads(purchase_timeline)")
        conn.commit()


def add_lead(
    name: str,
    phone: str,
    email: str,
    property_preference: str,
    location_preference: str,
    budget: float,
    purchase_timeline: str,
    lead_status: str,
    next_followup_date: str,
    notes: str = ""
) -> int:
    """Inserts a new lead into the database using safe parameterized queries."""
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO leads (
                name, phone, email, property_preference, location_preference,
                budget, purchase_timeline, lead_status, next_followup_date,
                notes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name.strip(),
                phone.strip(),
                email.strip() if email else "",
                property_preference.strip(),
                location_preference.strip() if location_preference else "",
                float(budget),
                purchase_timeline.strip(),
                lead_status.strip(),
                str(next_followup_date) if next_followup_date else "",
                notes.strip() if notes else "",
                now_iso,
                now_iso
            )
        )
        conn.commit()
        return cursor.lastrowid


def update_lead(
    lead_id: int,
    name: str,
    phone: str,
    email: str,
    property_preference: str,
    location_preference: str,
    budget: float,
    purchase_timeline: str,
    lead_status: str,
    next_followup_date: str,
    notes: str = ""
) -> bool:
    """Updates an existing lead record."""
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE leads
            SET name = ?,
                phone = ?,
                email = ?,
                property_preference = ?,
                location_preference = ?,
                budget = ?,
                purchase_timeline = ?,
                lead_status = ?,
                next_followup_date = ?,
                notes = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                name.strip(),
                phone.strip(),
                email.strip() if email else "",
                property_preference.strip(),
                location_preference.strip() if location_preference else "",
                float(budget),
                purchase_timeline.strip(),
                lead_status.strip(),
                str(next_followup_date) if next_followup_date else "",
                notes.strip() if notes else "",
                now_iso,
                lead_id
            )
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_lead(lead_id: int) -> bool:
    """Deletes a lead by its ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_lead_by_id(lead_id: int) -> dict | None:
    """Retrieves a single lead by ID as a dictionary."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_leads(
    search_query: str = "",
    status_filter: str = "All",
    timeline_filter: str = "All",
    min_budget: float = 0.0,
    max_budget: float = None,
    sort_by: str = "Created (Newest First)"
) -> list[dict]:
    """
    Retrieves filtered and sorted leads.
    Guards against SQL injection using parameterized filters.
    """
    query = "SELECT * FROM leads WHERE 1=1"
    params = []

    # Search term filter across multiple columns
    if search_query and search_query.strip():
        term = f"%{search_query.strip()}%"
        query += " AND (name LIKE ? OR phone LIKE ? OR email LIKE ? OR location_preference LIKE ? OR property_preference LIKE ? OR notes LIKE ?)"
        params.extend([term, term, term, term, term, term])

    # Status filter
    if status_filter and status_filter != "All":
        query += " AND lead_status = ?"
        params.append(status_filter)

    # Timeline filter
    if timeline_filter and timeline_filter != "All":
        query += " AND purchase_timeline = ?"
        params.append(timeline_filter)

    # Budget range filter
    if min_budget > 0:
        query += " AND budget >= ?"
        params.append(min_budget)

    if max_budget is not None and max_budget > 0:
        query += " AND budget <= ?"
        params.append(max_budget)

    # Sorting options
    if sort_by == "Created (Newest First)":
        query += " ORDER BY id DESC"
    elif sort_by == "Created (Oldest First)":
        query += " ORDER BY id ASC"
    elif sort_by == "Budget (High to Low)":
        query += " ORDER BY budget DESC"
    elif sort_by == "Budget (Low to High)":
        query += " ORDER BY budget ASC"
    elif sort_by == "Next Follow-up (Earliest First)":
        query += " ORDER BY CASE WHEN next_followup_date = '' OR next_followup_date IS NULL THEN 1 ELSE 0 END, next_followup_date ASC"
    elif sort_by == "Customer Name (A-Z)":
        query += " ORDER BY name ASC"
    else:
        query += " ORDER BY id DESC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_dashboard_metrics() -> dict:
    """
    Computes key real estate CRM metrics:
    - total_leads
    - new_leads
    - interested_leads (Interested, Site Visit Scheduled, Negotiation)
    - converted_leads (Converted / Closed-Won)
    - conversion_rate (%)
    - followups_due_today
    - followups_overdue
    - average_budget
    """
    today_str = date.today().strftime("%Y-%m-%d")

    with get_connection() as conn:
        cursor = conn.cursor()

        # Total leads
        cursor.execute("SELECT COUNT(*) FROM leads")
        total_leads = cursor.fetchone()[0]

        if total_leads == 0:
            return {
                "total_leads": 0,
                "new_leads": 0,
                "interested_leads": 0,
                "converted_leads": 0,
                "conversion_rate": 0.0,
                "followups_due_today": 0,
                "followups_overdue": 0,
                "average_budget": 0.0,
            }

        # New leads
        cursor.execute("SELECT COUNT(*) FROM leads WHERE lead_status = 'New'")
        new_leads = cursor.fetchone()[0]

        # Interested leads (high pipeline intent)
        cursor.execute(
            """
            SELECT COUNT(*) FROM leads 
            WHERE lead_status IN ('Interested', 'Site Visit Scheduled', 'Negotiation')
            """
        )
        interested_leads = cursor.fetchone()[0]

        # Converted leads
        cursor.execute("SELECT COUNT(*) FROM leads WHERE lead_status = 'Converted'")
        converted_leads = cursor.fetchone()[0]

        # Conversion Rate
        conversion_rate = round((converted_leads / total_leads) * 100, 1)

        # Average Budget
        cursor.execute("SELECT AVG(budget) FROM leads WHERE budget > 0")
        avg_budget_row = cursor.fetchone()[0]
        average_budget = round(avg_budget_row, 2) if avg_budget_row else 0.0

        # Followups due today
        cursor.execute(
            "SELECT COUNT(*) FROM leads WHERE next_followup_date = ? AND lead_status NOT IN ('Converted', 'Lost')",
            (today_str,)
        )
        followups_due_today = cursor.fetchone()[0]

        # Followups overdue
        cursor.execute(
            """
            SELECT COUNT(*) FROM leads 
            WHERE next_followup_date != '' 
              AND next_followup_date < ? 
              AND lead_status NOT IN ('Converted', 'Lost')
            """,
            (today_str,)
        )
        followups_overdue = cursor.fetchone()[0]

        return {
            "total_leads": total_leads,
            "new_leads": new_leads,
            "interested_leads": interested_leads,
            "converted_leads": converted_leads,
            "conversion_rate": conversion_rate,
            "followups_due_today": followups_due_today,
            "followups_overdue": followups_overdue,
            "average_budget": average_budget,
        }


def seed_sample_leads():
    """
    Seeds initial realistic real estate leads if the database is currently empty.
    Provides immediate testable data for the user.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leads")
        count = cursor.fetchone()[0]
        if count > 0:
            return  # Already has data

    today = date.today()
    sample_data = [
        (
            "Sophia Reynolds",
            "+1 555-234-8901",
            "sophia.reynolds@example.com",
            "3 BHK Luxury Apartment",
            "Downtown Waterfront",
            650000.0,
            "Immediate (< 1 month)",
            "Negotiation",
            (today).strftime("%Y-%m-%d"),
            "Pre-approved mortgage from Chase. Loved the 14th floor corner unit. Waiting on final price revision."
        ),
        (
            "David Chen",
            "+1 555-876-5432",
            "david.chen@techmail.io",
            "4 BHK Modern Villa",
            "Suburban Hills",
            1200000.0,
            "1 - 3 months",
            "Site Visit Scheduled",
            (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            "Wants large backyard with home office space. Family visit scheduled this Saturday at 11 AM."
        ),
        (
            "Emily & Marcus Taylor",
            "+1 555-432-1098",
            "emily.taylor@gmail.com",
            "2 BHK Penthouse",
            "Arts District",
            450000.0,
            "Immediate (< 1 month)",
            "Interested",
            (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "Follow-up was due 2 days ago. Sent brochures for Skyline Tower; need to call to schedule walkthrough."
        ),
        (
            "Vikram Malhotra",
            "+1 555-789-0123",
            "v.malhotra@corpconsult.com",
            "Commercial Retail Space",
            "Financial District",
            850000.0,
            "3 - 6 months",
            "Contacted",
            (today + timedelta(days=4)).strftime("%Y-%m-%d"),
            "Looking for high footfall commercial shop space for specialty coffee brand expansion."
        ),
        (
            "Rachel Green",
            "+1 555-654-9870",
            "rachel.green@fashionhaus.com",
            "1 BHK Studio Apartment",
            "Midtown Central",
            280000.0,
            "Immediate (< 1 month)",
            "New",
            today.strftime("%Y-%m-%d"),
            "New website inquiry. Relocating next month for work. Prefers furnished units near metro line."
        ),
        (
            "Anthony Rossi",
            "+1 555-321-6549",
            "a.rossi@constructiongroup.com",
            "Residential Plot / Land",
            "Greenfield Valley",
            320000.0,
            "More than 6 months",
            "Interested",
            (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "Looking for 5000 sq ft corner parcel to build custom retirement home next year."
        ),
        (
            "Elena Rostova",
            "+1 555-908-1122",
            "elena.r@luxuryliving.com",
            "3 BHK Luxury Apartment",
            "Downtown Waterfront",
            720000.0,
            "Immediate (< 1 month)",
            "Converted",
            "",
            "Deal closed! Signed agreement on Marina Heights Penthouse B. Keys handover next Monday."
        ),
        (
            "Brandon Miller",
            "+1 555-456-7812",
            "bmiller88@gmail.com",
            "2 BHK Apartment",
            "Westside Suburbs",
            210000.0,
            "Just Browsing / Exploring",
            "Lost",
            "",
            "Budget lower than current market inventory in requested zone. Advised to re-explore later."
        )
    ]

    for item in sample_data:
        add_lead(
            name=item[0],
            phone=item[1],
            email=item[2],
            property_preference=item[3],
            location_preference=item[4],
            budget=item[5],
            purchase_timeline=item[6],
            lead_status=item[7],
            next_followup_date=item[8],
            notes=item[9]
        )


def reset_to_sample_leads():
    """Resets the leads table and re-populates with fresh sample data."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM leads")
        conn.commit()
    seed_sample_leads()
