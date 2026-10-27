"""
app.py - PropertyLead AI: Real Estate Lead Management & Scoring Dashboard
Built with Streamlit, SQLite, and Python.
No paid APIs required.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta

# Import local backend modules
from database import (
    init_db, add_lead, update_lead, delete_lead, get_lead_by_id,
    get_all_leads, get_dashboard_metrics, seed_sample_leads, reset_to_sample_leads
)
from scoring import calculate_lead_score
from messaging import generate_followup_message, get_available_templates
from utils import (
    validate_lead_input, mask_phone, mask_email, format_currency
)

# -------------------------------------------------------------
# 1. Page Configuration & Custom CSS Styling
# -------------------------------------------------------------
st.set_page_config(
    page_title="PropertyLead AI | Real Estate CRM",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom modern CSS for a clean, professional real-estate dashboard look
st.markdown(
    """
    <style>
    /* Metric Card Styling */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
    }
    .metric-title {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #0f172a;
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .metric-sub {
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 4px;
    }
    
    /* Badges */
    .badge-hot {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-warm {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-cold {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-converted {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }

    /* Explanation Breakdown Box */
    .breakdown-card {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------------
# 2. Database Initialization & Auto-Seed
# -------------------------------------------------------------
init_db()
seed_sample_leads()

# -------------------------------------------------------------
# 3. Sidebar Navigation & Global Controls
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏢 **PropertyLead AI**")
    st.caption("Intelligent Real Estate Lead & Follow-up Assistant")
    st.divider()

    navigation = st.radio(
        "Navigate To",
        [
            "📊 Dashboard Overview",
            "👥 Leads Directory & Edit",
            "➕ Add New Lead",
            "📅 Follow-up Task List",
            "🧠 AI Lead Scoring Engine",
            "💬 Draft Message Studio",
            "⚙️ Settings & Sample Data"
        ],
        index=0
    )

    st.divider()
    st.markdown("### 🛡️ **Privacy & Display**")
    privacy_mode = st.toggle(
        "Privacy Protection Mode",
        value=False,
        help="Masks client phone numbers and email addresses on screen to safeguard personal data during presentations or shared screen sessions."
    )
    if privacy_mode:
        st.info("🔒 Contact masking active")

    currency_pref = st.selectbox("Display Currency", ["$ (USD)", "₹ (INR)", "€ (EUR)", "£ (GBP)"], index=0)
    curr_symbol = currency_pref.split()[0]

    st.divider()
    st.caption("v1.0.0 • SQLite Powered • Fully Offline & Free")


# -------------------------------------------------------------
# 4. Helper Function: Prepare Lead DataFrame for Table View
# -------------------------------------------------------------
def format_leads_dataframe(leads_list: list[dict], mask_privacy: bool, curr_sym: str) -> pd.DataFrame:
    """Transforms raw lead records into a formatted presentation DataFrame."""
    if not leads_list:
        return pd.DataFrame()

    records = []
    for l in leads_list:
        score_info = calculate_lead_score(l)
        phone_display = mask_phone(l["phone"]) if mask_privacy else l["phone"]
        email_display = mask_email(l["email"]) if mask_privacy else (l["email"] or "N/A")
        
        records.append({
            "ID": l["id"],
            "Customer Name": l["name"],
            "Phone": phone_display,
            "Email": email_display,
            "Property Preference": l["property_preference"],
            "Location": l["location_preference"] or "Unspecified",
            "Budget": format_currency(l["budget"], curr_sym),
            "Timeline": l["purchase_timeline"],
            "Status": l["lead_status"],
            "Priority Score": f"{score_info['total_score']} / 100",
            "Priority Tier": score_info["badge"],
            "Next Follow-up": l["next_followup_date"] or "None set"
        })
    return pd.DataFrame(records)


# -------------------------------------------------------------
# PAGE 1: DASHBOARD OVERVIEW
# -------------------------------------------------------------
if navigation == "📊 Dashboard Overview":
    st.markdown("## 📊 Real Estate Sales Dashboard")
    st.write("Track sales pipeline performance, customer readiness, and daily conversion targets.")

    metrics = get_dashboard_metrics()
    today_str = date.today().strftime("%Y-%m-%d")

    # Alert banners for high urgency items
    if metrics["followups_overdue"] > 0:
        st.error(f"🚨 **Attention Required:** You have **{metrics['followups_overdue']} overdue follow-up task(s)** that need immediate outreach!")
    elif metrics["followups_due_today"] > 0:
        st.warning(f"📌 **Daily Reminder:** You have **{metrics['followups_due_today']} lead follow-up(s) scheduled for today**.")

    # Top KPI Metrics Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    with kpi_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Total Leads</div>
                <div class="metric-value">{metrics['total_leads']}</div>
                <div class="metric-sub">Active in database</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi_col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">New Inquiries</div>
                <div class="metric-value" style="color: #0284c7;">{metrics['new_leads']}</div>
                <div class="metric-sub">Awaiting qualification</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi_col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Interested Pipeline</div>
                <div class="metric-value" style="color: #d97706;">{metrics['interested_leads']}</div>
                <div class="metric-sub">Tours & active negotiations</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi_col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Deals Converted</div>
                <div class="metric-value" style="color: #16a34a;">{metrics['converted_leads']}</div>
                <div class="metric-sub">Closed-Won properties</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi_col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Conversion Rate</div>
                <div class="metric-value" style="color: #4f46e5;">{metrics['conversion_rate']}%</div>
                <div class="metric-sub">Win ratio across pipeline</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Secondary metric row
    sub_col1, sub_col2, sub_col3 = st.columns(3)
    with sub_col1:
        st.info(f"💰 **Average Client Budget:** {format_currency(metrics['average_budget'], curr_symbol)}")
    with sub_col2:
        st.info(f"📅 **Follow-ups Due Today:** {metrics['followups_due_today']} lead(s)")
    with sub_col3:
        st.info(f"⏳ **Follow-ups Overdue:** {metrics['followups_overdue']} lead(s)")

    st.divider()

    # Visual Pipeline Charts
    all_leads = get_all_leads()
    if all_leads:
        chart_col1, chart_col2 = st.columns(2)
        
        # Prepare charts data
        df_leads = pd.DataFrame(all_leads)

        with chart_col1:
            st.markdown("#### 🎯 Leads by Pipeline Status")
            status_counts = df_leads["lead_status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Lead Count"]
            st.bar_chart(status_counts.set_index("Status"), color="#3b82f6")

        with chart_col2:
            st.markdown("#### ⏱️ Leads by Purchase Timeline")
            timeline_counts = df_leads["purchase_timeline"].value_counts().reset_index()
            timeline_counts.columns = ["Timeline", "Lead Count"]
            st.bar_chart(timeline_counts.set_index("Timeline"), color="#f59e0b")

        st.markdown("#### 🔥 Lead Priority Distribution (AI Score)")
        priority_tiers = []
        for l in all_leads:
            score = calculate_lead_score(l)
            priority_tiers.append(score["category"])
        
        priority_df = pd.Series(priority_tiers).value_counts().reset_index()
        priority_df.columns = ["Priority Level", "Count"]
        
        p_cols = st.columns(len(priority_df))
        for idx, row in priority_df.iterrows():
            with p_cols[idx]:
                tier_name = row["Priority Level"]
                tier_count = row["Count"]
                color_badge = "🔥 Hot" if tier_name == "Hot" else ("⚡ Warm" if tier_name == "Warm" else ("❄️ Cold" if tier_name == "Cold" else tier_name))
                st.metric(label=f"{color_badge} Leads", value=tier_count)
    else:
        st.info("No leads available to plot charts. Seed sample data from the Settings page!")


# -------------------------------------------------------------
# PAGE 2: LEADS DIRECTORY, SEARCH, FILTER & EDIT
# -------------------------------------------------------------
elif navigation == "👥 Leads Directory & Edit":
    st.markdown("## 👥 Real Estate Leads Directory")
    st.write("Browse, search, filter, and edit full lead profiles.")

    # Search & Filter Controls
    with st.expander("🔍 **Search & Filter Controls**", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)

        with f_col1:
            search_query = st.text_input("Search Leads", placeholder="Name, phone, email, location...", key="dir_search")

        with f_col2:
            status_options = ["All", "New", "Contacted", "Interested", "Site Visit Scheduled", "Negotiation", "Converted", "Lost"]
            status_filter = st.selectbox("Filter by Status", status_options, index=0)

        with f_col3:
            timeline_options = ["All", "Immediate (< 1 month)", "1 - 3 months", "3 - 6 months", "More than 6 months", "Just Browsing / Exploring"]
            timeline_filter = st.selectbox("Filter by Purchase Timeline", timeline_options, index=0)

        with f_col4:
            sort_options = [
                "Created (Newest First)",
                "Created (Oldest First)",
                "Budget (High to Low)",
                "Budget (Low to High)",
                "Next Follow-up (Earliest First)",
                "Customer Name (A-Z)"
            ]
            sort_by = st.selectbox("Sort By", sort_options, index=0)

    # Fetch filtered leads
    leads = get_all_leads(
        search_query=search_query,
        status_filter=status_filter,
        timeline_filter=timeline_filter,
        sort_by=sort_by
    )

    st.markdown(f"**Found {len(leads)} lead(s)**")

    if leads:
        formatted_df = format_leads_dataframe(leads, privacy_mode, curr_symbol)
        st.dataframe(formatted_df, use_container_width=True, hide_index=True)

        st.divider()

        # Detailed Lead Card & Quick Edit section
        st.markdown("### ✏️ Inspect & Edit Lead Profile")
        lead_options = {f"#{l['id']} - {l['name']} ({l['property_preference']})": l["id"] for l in leads}
        selected_label = st.selectbox("Select a Lead to Inspect or Edit", list(lead_options.keys()))
        selected_lead_id = lead_options[selected_label]
        lead_data = get_lead_by_id(selected_lead_id)

        if lead_data:
            # Score breakdown preview
            score_data = calculate_lead_score(lead_data)
            
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.markdown(f"#### {lead_data['name']}")
                contact_phone = mask_phone(lead_data['phone']) if privacy_mode else lead_data['phone']
                contact_email = mask_email(lead_data['email']) if privacy_mode else (lead_data['email'] or "No email provided")
                st.caption(f"📞 {contact_phone} • ✉️ {contact_email} • 📍 {lead_data['location_preference'] or 'Location flexible'}")
            with c2:
                st.metric("Priority Score", f"{score_data['total_score']} / 100", delta=score_data["category"])
            with c3:
                st.metric("Target Budget", format_currency(lead_data["budget"], curr_symbol))

            # Edit Form
            with st.form(f"edit_lead_form_{lead_data['id']}"):
                st.markdown("**Update Lead Details:**")
                e_col1, e_col2, e_col3 = st.columns(3)
                
                with e_col1:
                    edit_name = st.text_input("Customer Name *", value=lead_data["name"])
                    edit_phone = st.text_input("Phone Number *", value=lead_data["phone"])
                    edit_email = st.text_input("Email Address", value=lead_data["email"])

                with e_col2:
                    edit_prop = st.text_input("Property Preference *", value=lead_data["property_preference"])
                    edit_loc = st.text_input("Preferred Location / Neighborhood", value=lead_data["location_preference"] or "")
                    edit_budget = st.number_input(
                        f"Budget ({curr_symbol}) *",
                        min_value=0.0,
                        value=float(lead_data["budget"]),
                        step=10000.0
                    )

                with e_col3:
                    timeline_idx = timeline_options[1:].index(lead_data["purchase_timeline"]) if lead_data["purchase_timeline"] in timeline_options[1:] else 0
                    edit_timeline = st.selectbox("Purchase Timeline *", timeline_options[1:], index=timeline_idx)
                    
                    status_idx = status_options[1:].index(lead_data["lead_status"]) if lead_data["lead_status"] in status_options[1:] else 0
                    edit_status = st.selectbox("Lead Pipeline Status *", status_options[1:], index=status_idx)

                    # Date parsing
                    default_date = date.today()
                    if lead_data["next_followup_date"]:
                        try:
                            default_date = datetime.strptime(lead_data["next_followup_date"], "%Y-%m-%d").date()
                        except ValueError:
                            default_date = date.today()
                    edit_followup = st.date_input("Next Follow-up Date", value=default_date)

                edit_notes = st.text_area("Agent Notes & Meeting Summary", value=lead_data["notes"] or "", rows=3)

                btn_col1, btn_col2 = st.columns([1, 4])
                with btn_col1:
                    save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)

                if save_btn:
                    is_valid, err_msg = validate_lead_input(
                        name=edit_name,
                        phone=edit_phone,
                        email=edit_email,
                        budget=edit_budget,
                        followup_date=str(edit_followup)
                    )
                    if not is_valid:
                        st.error(f"❌ Validation Error: {err_msg}")
                    else:
                        success = update_lead(
                            lead_id=lead_data["id"],
                            name=edit_name,
                            phone=edit_phone,
                            email=edit_email,
                            property_preference=edit_prop,
                            location_preference=edit_loc,
                            budget=edit_budget,
                            purchase_timeline=edit_timeline,
                            lead_status=edit_status,
                            next_followup_date=str(edit_followup),
                            notes=edit_notes
                        )
                        if success:
                            st.success(f"✅ Lead profile for **{edit_name}** updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update lead record. Please try again.")

            # Danger Zone: Delete Lead
            with st.expander("🗑️ **Danger Zone: Delete this lead**"):
                st.warning("Deleting a lead is irreversible and permanently removes their records.")
                if st.button(f"Permanently Delete #{lead_data['id']} - {lead_data['name']}", type="primary"):
                    if delete_lead(lead_data["id"]):
                        st.success(f"Lead #{lead_data['id']} deleted.")
                        st.rerun()
                    else:
                        st.error("Could not delete lead.")
    else:
        st.info("No leads match your current search/filter criteria.")


# -------------------------------------------------------------
# PAGE 3: ADD NEW LEAD
# -------------------------------------------------------------
elif navigation == "➕ Add New Lead":
    st.markdown("## ➕ Register New Real Estate Lead")
    st.write("Capture incoming prospect details with automated input validation and instant AI priority scoring.")

    with st.form("add_lead_form", clear_on_submit=False):
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### 👤 Customer Contact Profile")
            name = st.text_input("Full Name *", placeholder="e.g. Alexander Vance")
            phone = st.text_input("Phone Number *", placeholder="e.g. +1 555-482-9011")
            email = st.text_input("Email Address (Optional)", placeholder="e.g. alexander@example.com")
            
            st.markdown("#### 📍 Property Requirements")
            property_types = [
                "1 BHK Apartment / Studio",
                "2 BHK Modern Apartment",
                "3 BHK Luxury Apartment",
                "4+ BHK Executive Villa / Townhouse",
                "Penthouse Suite",
                "Commercial Office / Retail Space",
                "Residential Land / Plot",
                "Other / Custom"
            ]
            prop_choice = st.selectbox("Property Preference *", property_types, index=1)
            if prop_choice == "Other / Custom":
                prop_choice = st.text_input("Specify Custom Property Type *", placeholder="e.g. Historic Brownstone")
            
            location = st.text_input("Preferred Location / Neighborhood", placeholder="e.g. Downtown Waterfront, Suburbs")

        with c2:
            st.markdown("#### 💰 Financials & Pipeline Qualification")
            budget = st.number_input(f"Target Budget ({curr_symbol}) *", min_value=0.0, value=350000.0, step=25000.0)
            
            timelines = [
                "Immediate (< 1 month)",
                "1 - 3 months",
                "3 - 6 months",
                "More than 6 months",
                "Just Browsing / Exploring"
            ]
            timeline = st.selectbox("Purchase Timeline *", timelines, index=0)

            statuses = [
                "New",
                "Contacted",
                "Interested",
                "Site Visit Scheduled",
                "Negotiation",
                "Converted",
                "Lost"
            ]
            status = st.selectbox("Current Lead Status *", statuses, index=0)

            followup_date = st.date_input(
                "Next Follow-up Date *",
                value=date.today() + timedelta(days=2),
                help="Recommended: schedule follow-ups within 48 hours for maximum conversion."
            )

            notes = st.text_area(
                "Requirements & Discussion Notes",
                placeholder="Mention specific client needs (e.g., south-facing balcony, parking space, pre-approved mortgage)...",
                rows=3
            )

        submit_btn = st.form_submit_button("🚀 Create Lead & Calculate AI Score", use_container_width=True)

        if submit_btn:
            is_valid, err_msg = validate_lead_input(
                name=name,
                phone=phone,
                email=email,
                budget=budget,
                followup_date=str(followup_date)
            )

            if not is_valid:
                st.error(f"❌ Validation Error: {err_msg}")
            else:
                new_id = add_lead(
                    name=name,
                    phone=phone,
                    email=email,
                    property_preference=prop_choice,
                    location_preference=location,
                    budget=budget,
                    purchase_timeline=timeline,
                    lead_status=status,
                    next_followup_date=str(followup_date),
                    notes=notes
                )
                
                # Retrieve newly created lead and compute instant AI score
                new_lead = get_lead_by_id(new_id)
                score_info = calculate_lead_score(new_lead)

                st.success(f"🎉 Lead **{name}** added successfully! (ID #{new_id})")
                
                st.markdown("### 🎯 Instant AI Priority Assessment")
                sc_col1, sc_col2 = st.columns([1, 2])
                with sc_col1:
                    st.metric("Priority Score", f"{score_info['total_score']} / 100", delta=score_info["badge"])
                with sc_col2:
                    st.info(f"💡 **Recommended Action:** {score_info['action_recommendation']}")


# -------------------------------------------------------------
# PAGE 4: FOLLOW-UP TASK LIST
# -------------------------------------------------------------
elif navigation == "📅 Follow-up Task List":
    st.markdown("## 📅 Follow-up Task Manager")
    st.write("Never lose a deal to delayed follow-ups. Prioritized by urgency and deadline.")

    all_active_leads = get_all_leads()
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    overdue_tasks = []
    today_tasks = []
    upcoming_tasks = []

    for l in all_active_leads:
        if l["lead_status"] in ("Converted", "Lost"):
            continue  # Terminal leads don't require active scheduled tasks
        
        f_date_str = l.get("next_followup_date", "")
        if not f_date_str:
            continue
        
        try:
            f_date = datetime.strptime(f_date_str, "%Y-%m-%d").date()
            if f_date < today:
                overdue_tasks.append((l, f_date))
            elif f_date == today:
                today_tasks.append((l, f_date))
            elif 0 < (f_date - today).days <= 7:
                upcoming_tasks.append((l, f_date))
        except ValueError:
            pass

    # Quick summary badges
    s1, s2, s3 = st.columns(3)
    s1.metric("🚨 Overdue Follow-ups", len(overdue_tasks))
    s2.metric("📌 Due Today", len(today_tasks))
    s3.metric("🗓️ Upcoming (Next 7 Days)", len(upcoming_tasks))

    st.divider()

    # Section 1: Overdue
    st.markdown("### 🚨 Overdue Follow-ups (Requires Urgent Action)")
    if overdue_tasks:
        for lead, f_date in overdue_tasks:
            days_late = (today - f_date).days
            score_res = calculate_lead_score(lead)
            contact_ph = mask_phone(lead["phone"]) if privacy_mode else lead["phone"]

            with st.container():
                st.markdown(
                    f"""
                    <div style="border-left: 5px solid #ef4444; background: #fff5f5; padding: 12px 18px; border-radius: 8px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: 700; font-size: 1.1rem; color: #1e293b;">{lead['name']}</span>
                                <span style="margin-left: 8px;">{score_res['badge']}</span>
                            </div>
                            <span style="color: #b91c1c; font-weight: 700; font-size: 0.85rem;">⚠️ {days_late} DAY(S) OVERDUE</span>
                        </div>
                        <div style="color: #475569; font-size: 0.9rem; margin-top: 4px;">
                            <strong>Property:</strong> {lead['property_preference']} ({format_currency(lead['budget'], curr_symbol)}) • 
                            <strong>Phone:</strong> {contact_ph} • 
                            <strong>Stage:</strong> {lead['lead_status']}
                        </div>
                        <div style="color: #64748b; font-size: 0.85rem; margin-top: 4px; font-style: italic;">
                            "{lead['notes'] or 'No notes provided'}"
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.success("🎉 Excellent! You have zero overdue tasks.")

    # Section 2: Due Today
    st.markdown("### 📌 Due Today's Action Plan")
    if today_tasks:
        for lead, _ in today_tasks:
            score_res = calculate_lead_score(lead)
            contact_ph = mask_phone(lead["phone"]) if privacy_mode else lead["phone"]

            with st.container():
                st.markdown(
                    f"""
                    <div style="border-left: 5px solid #3b82f6; background: #eff6ff; padding: 12px 18px; border-radius: 8px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: 700; font-size: 1.1rem; color: #1e293b;">{lead['name']}</span>
                                <span style="margin-left: 8px;">{score_res['badge']}</span>
                            </div>
                            <span style="color: #1d4ed8; font-weight: 700; font-size: 0.85rem;">📅 SCHEDULED FOR TODAY</span>
                        </div>
                        <div style="color: #475569; font-size: 0.9rem; margin-top: 4px;">
                            <strong>Property:</strong> {lead['property_preference']} ({format_currency(lead['budget'], curr_symbol)}) • 
                            <strong>Phone:</strong> {contact_ph} • 
                            <strong>Stage:</strong> {lead['lead_status']}
                        </div>
                        <div style="color: #64748b; font-size: 0.85rem; margin-top: 4px; font-style: italic;">
                            "{lead['notes'] or 'No notes provided'}"
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No follow-ups scheduled for today.")

    # Section 3: Upcoming 7 Days
    st.markdown("### 🗓️ Upcoming Follow-ups (Next 7 Days)")
    if upcoming_tasks:
        for lead, f_date in upcoming_tasks:
            days_away = (f_date - today).days
            score_res = calculate_lead_score(lead)
            contact_ph = mask_phone(lead["phone"]) if privacy_mode else lead["phone"]

            st.markdown(
                f"""
                <div style="border-left: 4px solid #10b981; background: #f0fdf4; padding: 10px 16px; border-radius: 6px; margin-bottom: 8px;">
                    <strong>{lead['name']}</strong> — {lead['property_preference']} 
                    <span style="color: #047857; font-weight: 600; font-size: 0.85rem; float: right;">Due in {days_away} day(s) ({f_date})</span>
                    <br><small style="color: #4b5563;">Status: {lead['lead_status']} • Contact: {contact_ph}</small>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.caption("No upcoming tasks for the next 7 days.")


# -------------------------------------------------------------
# PAGE 5: EXPLAINABLE AI LEAD SCORING ENGINE
# -------------------------------------------------------------
elif navigation == "🧠 AI Lead Scoring Engine":
    st.markdown("## 🧠 Transparent & Explainable AI Lead Scorer")
    st.write(
        "Unlike black-box models, PropertyLead AI uses **explainable feature weights** and clear heuristics. "
        "Every single point awarded is mathematically transparent and actionable."
    )

    all_leads = get_all_leads()
    if not all_leads:
        st.warning("No leads found. Please add a lead or load sample data.")
    else:
        lead_dict = {f"#{l['id']} - {l['name']} ({l['property_preference']})": l for l in all_leads}
        chosen_lead_label = st.selectbox("Select Lead to Audit & Explain", list(lead_dict.keys()))
        target_lead = lead_dict[chosen_lead_label]

        # Calculate explainable score
        score_data = calculate_lead_score(target_lead)

        col_score, col_rec = st.columns([1, 2])
        with col_score:
            st.metric(
                label="Overall Priority Score",
                value=f"{score_data['total_score']} / 100",
                delta=score_data["badge"]
            )
            st.progress(score_data["total_score"] / 100)

        with col_rec:
            st.markdown("#### 💡 AI Action Recommendation")
            st.info(score_data["action_recommendation"])
            st.caption(f"Evaluation Model: {score_data['confidence_level']}")

        st.divider()
        st.markdown("### 📋 Mathematical Factor Breakdown")
        st.write("Inspect how each individual feature contributed to the total score:")

        for item in score_data["breakdown"]:
            pts = item["points"]
            max_pts = item["max_points"]
            feature = item["feature"]
            reason = item["reason"]

            pct = (pts / max_pts) if max_pts > 0 else 1.0

            st.markdown(
                f"""
                <div class="breakdown-card">
                    <div style="display: flex; justify-content: space-between; font-weight: 600; color: #1e293b;">
                        <span>{feature}</span>
                        <span style="color: #2563eb;">{pts} / {max_pts} pts</span>
                    </div>
                    <div style="color: #475569; font-size: 0.85rem; margin-top: 4px;">
                        {reason}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with st.expander("ℹ️ **How PropertyLead AI Calculates Scores (Scoring Methodology)**"):
            st.markdown(
                """
                The priority scoring algorithm evaluates 4 key dimensions:
                1. **Timeline Urgency (35% weight):** Prospects needing to buy in `< 1 month` score maximum points (35 pts), while browsing leads score 0 pts.
                2. **Sales Pipeline Depth (30% weight):** Negotiation stage awards 30 pts, Site Visits award 25 pts, Interested awards 20 pts, and New awards 10 pts.
                3. **Financial & Requirement Viability (20% weight):** Explicit budgets award 10 pts, luxury/high-tier budgets award +5 pts, and specific locations award +5 pts.
                4. **Cadence & Contact Quality (15% weight):** Having dual phone + email awards +5 pts; scheduled follow-ups due today or overdue award up to +10 pts for urgency.
                """
            )


# -------------------------------------------------------------
# PAGE 6: DRAFT MESSAGE STUDIO
# -------------------------------------------------------------
elif navigation == "💬 Draft Message Studio":
    st.markdown("## 💬 Follow-up Message Drafter")
    st.write("Generate personalized, high-converting outreach drafts across WhatsApp, SMS, and Email in seconds.")

    all_leads = get_all_leads()
    if not all_leads:
        st.warning("No leads available. Please add a lead or load sample data.")
    else:
        lead_dict = {f"#{l['id']} - {l['name']} ({l['property_preference']})": l for l in all_leads}
        
        c_lead, c_channel = st.columns([2, 1])
        with c_lead:
            selected_label = st.selectbox("Select Target Lead", list(lead_dict.keys()), key="msg_lead_sel")
            active_lead = lead_dict[selected_label]
        
        with c_channel:
            channel = st.radio("Communication Channel", ["WhatsApp", "SMS", "Email"], horizontal=True)

        # Template Selection
        templates = get_available_templates()
        template_labels = [t["label"] for t in templates]
        template_ids = [t["id"] for t in templates]

        chosen_template_label = st.selectbox("Outreach Intent / Template Type", template_labels, index=0)
        chosen_template_id = template_ids[template_labels.index(chosen_template_label)]

        # Customization options
        with st.expander("⚙️ **Agent Signature & Branding Details**", expanded=False):
            ag_col1, ag_col2 = st.columns(2)
            agent_name = ag_col1.text_input("Your Name / Title", value="Sarah Jenkins (Senior Realtor)")
            agency_name = ag_col2.text_input("Brokerage / Agency Name", value="Horizon Premier Realty")

        # Generate Message
        draft = generate_followup_message(
            lead=active_lead,
            channel=channel,
            template_type=chosen_template_id,
            agent_name=agent_name,
            agent_company=agency_name
        )

        st.markdown("### 📝 Generated Draft Preview")

        if channel == "Email":
            st.text_input("Email Subject Line", value=draft["subject"], key="email_subj_preview")
        
        st.text_area("Message Body", value=draft["body"], height=200, key="msg_body_preview")

        # Action Buttons
        b_col1, b_col2 = st.columns([1, 3])

        with b_col1:
            if channel == "WhatsApp" and draft["whatsapp_link"]:
                st.markdown(
                    f"""
                    <a href="{draft['whatsapp_link']}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #25D366; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: 700; cursor: pointer; width: 100%;">
                            📲 Open in WhatsApp
                        </button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.button("📋 Copy to Clipboard (Preview above)")

        with b_col2:
            phone_num = mask_phone(active_lead['phone']) if privacy_mode else active_lead['phone']
            email_addr = mask_email(active_lead['email']) if privacy_mode else (active_lead['email'] or "None")
            st.caption(f"Sending to: **{active_lead['name']}** • Phone: `{phone_num}` • Email: `{email_addr}`")


# -------------------------------------------------------------
# PAGE 7: SETTINGS & SAMPLE DATA
# -------------------------------------------------------------
elif navigation == "⚙️ Settings & Sample Data":
    st.markdown("## ⚙️ Settings & Database Management")
    st.write("Manage application sample data, export records, and inspect system storage.")

    set_col1, set_col2 = st.columns(2)

    with set_col1:
        st.markdown("### 🧪 Instant Demo & Sample Data")
        st.write("Reset database with 8 realistic real-estate leads (covering various stages, timelines, budgets, and follow-up deadlines).")
        if st.button("🔄 Reload / Reset Sample Leads", type="secondary"):
            reset_to_sample_leads()
            st.success("✅ Database re-seeded with fresh sample data!")
            st.rerun()

    with set_col2:
        st.markdown("### 📥 Data Export")
        st.write("Export all lead records to a clean CSV file for Excel, backup, or reporting.")
        all_export_leads = get_all_leads()
        if all_export_leads:
            df_export = pd.DataFrame(all_export_leads)
            csv_data = df_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Leads as CSV",
                data=csv_data,
                file_name=f"propertylead_ai_export_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.caption("No leads to export.")

    st.divider()

    st.markdown("### 📖 About PropertyLead AI")
    st.markdown(
        """
        - **Target Domain:** Real Estate Lead Management & Client Nurturing.
        - **Architecture:** Modular Python codebase with Streamlit UI, SQLite parameterized storage, rule-based AI scoring, and template communication engines.
        - **Privacy Safeguards:** In-memory masking for phone numbers and email addresses, parameterized SQL queries preventing SQL injection, and strict input format validation.
        - **No Paid APIs:** Designed to run 100% locally and cost-free.
        """
    )
