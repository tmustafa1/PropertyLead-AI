"""
scoring.py - Transparent & Explainable Lead-Priority Scoring Engine
Designed with AI/ML feature-weighting principles:
Uses deterministic, transparent scoring rules that provide an exact point breakdown
and recommended next actions for real estate agents.
"""

from datetime import datetime, date


def calculate_lead_score(lead: dict) -> dict:
    """
    Computes an explainable lead priority score from 0 to 100.
    
    Returns a comprehensive dictionary containing:
    - total_score: 0 to 100
    - category: 'Hot', 'Warm', 'Cold', 'Converted', or 'Lost'
    - badge: Visual emoji badge for UI rendering
    - color: Hex color for UI charts and tags
    - breakdown: List of each evaluated feature, points earned, and explanation
    - action_recommendation: Heuristic-based next step for the real estate agent
    """
    status = lead.get("lead_status", "New")
    
    # Terminal statuses
    if status == "Converted":
        return {
            "total_score": 100,
            "category": "Converted",
            "badge": "🏆 Converted (Won)",
            "color": "#28a745",
            "breakdown": [
                {
                    "feature": "Deal Status",
                    "points": 100,
                    "max_points": 100,
                    "reason": "Successfully closed deal! Lead has converted to a customer."
                }
            ],
            "action_recommendation": "Send post-closing congratulations package and request referrals or a review.",
            "confidence_level": "Deterministic (Closed Deal)"
        }

    if status == "Lost":
        return {
            "total_score": 0,
            "category": "Lost",
            "badge": "⚪ Closed-Lost",
            "color": "#6c757d",
            "breakdown": [
                {
                    "feature": "Deal Status",
                    "points": 0,
                    "max_points": 100,
                    "reason": "Deal marked as closed-lost or customer declined at this time."
                }
            ],
            "action_recommendation": "Archive lead in long-term drip campaign for re-engagement in 6 months.",
            "confidence_level": "Deterministic (Archived Lead)"
        }

    score = 0
    breakdown = []

    # -------------------------------------------------------------
    # Feature 1: Purchase Timeline Urgency (Weight: 35 points max)
    # Immediate buyers represent the highest conversion probability.
    # -------------------------------------------------------------
    timeline = lead.get("purchase_timeline", "")
    timeline_pts = 0
    timeline_reason = ""

    if "Immediate" in timeline or "< 1 month" in timeline:
        timeline_pts = 35
        timeline_reason = "Urgent buyer: Needs property within 30 days (+35 pts)"
    elif "1 - 3 months" in timeline:
        timeline_pts = 25
        timeline_reason = "High readiness: Looking to purchase in 1 to 3 months (+25 pts)"
    elif "3 - 6 months" in timeline:
        timeline_pts = 15
        timeline_reason = "Medium timeline: Purchase window is 3 to 6 months (+15 pts)"
    elif "More than 6 months" in timeline:
        timeline_pts = 5
        timeline_reason = "Long term pipeline: Timeline exceeds 6 months (+5 pts)"
    else:
        timeline_pts = 0
        timeline_reason = "Browsing / Unspecified purchase timeline (0 pts)"

    score += timeline_pts
    breakdown.append({
        "feature": "Purchase Timeline",
        "points": timeline_pts,
        "max_points": 35,
        "reason": timeline_reason
    })

    # -------------------------------------------------------------
    # Feature 2: Sales Pipeline Engagement Stage (Weight: 30 points max)
    # Further pipeline depth corresponds to higher purchase intent.
    # -------------------------------------------------------------
    stage_pts = 0
    stage_reason = ""

    if status == "Negotiation":
        stage_pts = 30
        stage_reason = "Active negotiations / price finalization in progress (+30 pts)"
    elif status == "Site Visit Scheduled":
        stage_pts = 25
        stage_reason = "High commitment: Client agreed to on-site property tour (+25 pts)"
    elif status == "Interested":
        stage_pts = 20
        stage_reason = "Client shortlisted specific properties and requested details (+20 pts)"
    elif status == "Contacted":
        stage_pts = 10
        stage_reason = "Initial conversation held; client profile being qualified (+10 pts)"
    elif status == "New":
        stage_pts = 10
        stage_reason = "Fresh inbound lead awaiting initial contact outreach (+10 pts)"
    else:
        stage_pts = 5
        stage_reason = f"Standard pipeline stage: {status} (+5 pts)"

    score += stage_pts
    breakdown.append({
        "feature": "Pipeline Engagement Stage",
        "points": stage_pts,
        "max_points": 30,
        "reason": stage_reason
    })

    # -------------------------------------------------------------
    # Feature 3: Budget & Requirement Viability (Weight: 20 points max)
    # Explicit budget and location clarify qualified demand.
    # -------------------------------------------------------------
    budget = float(lead.get("budget", 0) or 0)
    location = str(lead.get("location_preference", "")).strip()
    property_type = str(lead.get("property_preference", "")).strip()

    budget_pts = 0
    budget_notes = []

    if budget > 0:
        budget_pts += 10
        budget_notes.append("Explicit budget declared (+10 pts)")
        if budget >= 500000:
            budget_pts += 5
            budget_notes.append("High-tier investment / luxury segment (+5 pts)")
    else:
        budget_notes.append("No budget specified (0 pts)")

    if location and location.lower() != "any":
        budget_pts += 5
        budget_notes.append("Specific location preference identified (+5 pts)")

    score += budget_pts
    breakdown.append({
        "feature": "Requirement Viability & Budget",
        "points": budget_pts,
        "max_points": 20,
        "reason": "; ".join(budget_notes)
    })

    # -------------------------------------------------------------
    # Feature 4: Lead Responsiveness & Follow-up Recency (Weight: 15 points max)
    # Evaluates omnichannel contact presence and active follow-up cadence.
    # -------------------------------------------------------------
    cadence_pts = 0
    cadence_notes = []

    # Check contact completeness
    phone = str(lead.get("phone", "")).strip()
    email = str(lead.get("email", "")).strip()
    if phone and email:
        cadence_pts += 5
        cadence_notes.append("Dual contact channels available (Phone + Email) (+5 pts)")
    elif phone or email:
        cadence_pts += 2
        cadence_notes.append("Single contact channel available (+2 pts)")

    # Check follow-up date status
    followup_str = str(lead.get("next_followup_date", "")).strip()
    if followup_str:
        try:
            followup_date = datetime.strptime(followup_str, "%Y-%m-%d").date()
            today = date.today()
            delta_days = (followup_date - today).days

            if delta_days < 0:
                # Overdue
                cadence_pts += 10
                cadence_notes.append(f"Follow-up is overdue by {abs(delta_days)} days! High urgency (+10 pts)")
            elif delta_days == 0:
                cadence_pts += 10
                cadence_notes.append("Follow-up is scheduled for TODAY (+10 pts)")
            elif 1 <= delta_days <= 3:
                cadence_pts += 8
                cadence_notes.append(f"Follow-up scheduled in {delta_days} days (+8 pts)")
            else:
                cadence_pts += 5
                cadence_notes.append("Follow-up scheduled in future pipeline (+5 pts)")
        except ValueError:
            cadence_notes.append("Unparseable follow-up date format (0 pts)")
    else:
        cadence_notes.append("No next follow-up date currently scheduled (0 pts)")

    # Cap cadence points to 15 max
    cadence_pts = min(cadence_pts, 15)
    score += cadence_pts
    breakdown.append({
        "feature": "Contact Quality & Follow-up Urgency",
        "points": cadence_pts,
        "max_points": 15,
        "reason": "; ".join(cadence_notes)
    })

    # Ensure total score is bounded [0, 100]
    total_score = min(max(int(round(score)), 0), 100)

    # Classification & Action Recommendation
    if total_score >= 70:
        category = "Hot"
        badge = "🔥 Hot Priority"
        color = "#e63946"  # Vibrant Red/Coral
        action_recommendation = (
            "Top priority lead! Call or WhatsApp today. Lock in a property tour or present "
            "comparable closing options immediately to prevent buyer fatigue."
        )
    elif total_score >= 40:
        category = "Warm"
        badge = "⚡ Warm Lead"
        color = "#f4a261"  # Warm Orange/Amber
        action_recommendation = (
            "Solid prospective buyer. Share targeted property brochures, answer questions on amenities "
            "and financing, and set a firm site-visit date."
        )
    else:
        category = "Cold"
        badge = "❄️ Cold Lead"
        color = "#457b9d"  # Cool Slate/Blue
        action_recommendation = (
            "Early stage or low urgency. Send monthly market updates or property newsletter. "
            "Keep touchpoints light without aggressive sales pressure."
        )

    return {
        "total_score": total_score,
        "category": category,
        "badge": badge,
        "color": color,
        "breakdown": breakdown,
        "action_recommendation": action_recommendation,
        "confidence_level": "Explainable Rule-Engine (100% Transparent)"
    }
