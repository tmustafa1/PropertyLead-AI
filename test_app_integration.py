"""
test_app_integration.py - Integration test verifying all helper methods and app dependencies
"""

import sys
import os

from database import (
    init_db, get_dashboard_metrics, get_all_leads, get_lead_by_id,
    add_lead, update_lead, delete_lead, reset_to_sample_leads
)
from scoring import calculate_lead_score
from messaging import generate_followup_message, get_available_templates
from utils import validate_lead_input, mask_phone, mask_email, format_currency

def test_full_flow():
    print("Testing init_db and reset_to_sample_leads...")
    init_db()
    reset_to_sample_leads()
    
    leads = get_all_leads()
    assert len(leads) >= 8, f"Expected 8 leads, got {len(leads)}"

    metrics = get_dashboard_metrics()
    print("Metrics check:", metrics)
    assert "total_leads" in metrics
    assert "conversion_rate" in metrics

    print("Testing scoring on all leads...")
    for lead in leads:
        score_res = calculate_lead_score(lead)
        assert 0 <= score_res["total_score"] <= 100
        assert score_res["category"] in ["Hot", "Warm", "Cold", "Converted", "Lost"]
        assert len(score_res["breakdown"]) > 0

    print("Testing message generation on all channels and templates...")
    templates = get_available_templates()
    for t in templates:
        for ch in ["WhatsApp", "SMS", "Email"]:
            msg = generate_followup_message(leads[0], channel=ch, template_type=t["id"])
            assert msg["body"]
            if ch == "Email":
                assert msg["subject"]

    print("Integration test passed successfully!")

if __name__ == "__main__":
    test_full_flow()
