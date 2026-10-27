"""
test_backend.py - Test suite for PropertyLead AI core backend modules
Validates database CRUD, seed generation, scoring accuracy, validation, and messaging.
"""

import os
import sys

# Ensure current dir is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import validate_lead_input, mask_phone, mask_email, format_currency
from database import (
    init_db, add_lead, update_lead, delete_lead, get_lead_by_id,
    get_all_leads, get_dashboard_metrics, reset_to_sample_leads
)
from scoring import calculate_lead_score
from messaging import generate_followup_message


def run_tests():
    print("=== 1. Testing Input Validation & Privacy Masking ===")
    valid, msg = validate_lead_input("John Doe", "+1 555-123-4567", "john@example.com", 500000, "2026-11-01")
    assert valid, f"Validation failed: {msg}"

    # Test invalid phone
    inv_valid, inv_msg = validate_lead_input("John Doe", "12", "john@example.com", 500000, "2026-11-01")
    assert not inv_valid, "Expected invalid phone to fail"

    # Test invalid email
    inv_valid, inv_msg = validate_lead_input("John Doe", "+1 555-123-4567", "bad-email", 500000, "2026-11-01")
    assert not inv_valid, "Expected invalid email to fail"

    # Test masking
    masked_p = mask_phone("+1 555-123-4567")
    masked_e = mask_email("john.smith@domain.com")
    assert "4567" in masked_p, f"Masked phone issue: {masked_p}"
    assert "@domain.com" in masked_e and "•" in masked_e, f"Masked email issue: {masked_e}"
    print("PASS: Validation and Privacy masking OK.")

    print("\n=== 2. Testing Database Operations & Sample Seeding ===")
    init_db()
    reset_to_sample_leads()
    
    leads = get_all_leads()
    print(f"Loaded {len(leads)} sample leads.")
    assert len(leads) >= 8, f"Expected at least 8 leads, got {len(leads)}"

    # Test metrics
    metrics = get_dashboard_metrics()
    print("Metrics:", metrics)
    assert metrics["total_leads"] >= 8
    assert metrics["converted_leads"] >= 1
    assert metrics["conversion_rate"] > 0
    print("PASS: Database init, seed, and metrics OK.")

    # Test Add Lead
    new_id = add_lead(
        name="Test Lead Agent",
        phone="+1 555-999-0000",
        email="test.agent@domain.com",
        property_preference="3 BHK Penthouse",
        location_preference="Downtown",
        budget=750000.0,
        purchase_timeline="Immediate (< 1 month)",
        lead_status="New",
        next_followup_date="2026-10-30",
        notes="Automated test note"
    )
    assert new_id > 0, "Failed to insert test lead"
    lead = get_lead_by_id(new_id)
    assert lead["name"] == "Test Lead Agent"
    print("PASS: Add and Get lead OK.")

    # Test Update Lead
    update_success = update_lead(
        lead_id=new_id,
        name="Test Lead Agent Updated",
        phone="+1 555-999-0000",
        email="test.agent@domain.com",
        property_preference="3 BHK Penthouse",
        location_preference="Downtown",
        budget=800000.0,
        purchase_timeline="Immediate (< 1 month)",
        lead_status="Interested",
        next_followup_date="2026-10-30",
        notes="Updated note"
    )
    assert update_success, "Failed to update lead"
    updated_lead = get_lead_by_id(new_id)
    assert updated_lead["name"] == "Test Lead Agent Updated"
    assert updated_lead["budget"] == 800000.0
    print("PASS: Update lead OK.")

    # Test Delete Lead
    delete_success = delete_lead(new_id)
    assert delete_success, "Failed to delete test lead"
    assert get_lead_by_id(new_id) is None, "Lead still found after deletion"
    print("PASS: Delete lead OK.")

    print("\n=== 3. Testing Lead Scoring Engine ===")
    sample_lead = leads[0]
    score_res = calculate_lead_score(sample_lead)
    print(f"Score for {sample_lead['name']}: {score_res['total_score']} ({score_res['category']})")
    assert 0 <= score_res["total_score"] <= 100
    assert len(score_res["breakdown"]) > 0
    assert "action_recommendation" in score_res
    print("PASS: Scoring engine OK.")

    print("\n=== 4. Testing Follow-up Message Generation ===")
    msg_wa = generate_followup_message(sample_lead, channel="WhatsApp")
    msg_email = generate_followup_message(sample_lead, channel="Email")
    assert len(msg_wa["body"]) > 10
    assert len(msg_email["subject"]) > 5
    assert "https://wa.me/" in msg_wa["whatsapp_link"]
    print("PASS: Message generation OK.")

    print("\nALL BACKEND TESTS PASSED SUCCESSFULLY! Ready for Streamlit UI.")


if __name__ == "__main__":
    run_tests()
