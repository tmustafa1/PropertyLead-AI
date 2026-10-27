"""
messaging.py - Heuristic & Template-Driven Follow-up Message Generator
Generates personalized, high-converting follow-up communications across WhatsApp,
SMS, and Email without requiring any external or paid AI APIs.
"""

import urllib.parse
from utils import format_currency


def get_available_templates() -> list[dict]:
    """Returns the list of follow-up intent types."""
    return [
        {"id": "auto", "label": "🪄 Smart Auto-Select (Based on Lead Status)"},
        {"id": "welcome_new", "label": "👋 Initial Introduction & Requirement Qualification (New Lead)"},
        {"id": "site_visit_invite", "label": "🏡 Site Visit & Private Tour Invitation"},
        {"id": "post_visit_followup", "label": "✨ Post-Site-Visit Feedback & Next Steps"},
        {"id": "price_negotiation", "label": "💼 Price, Offer & Negotiation Discussion"},
        {"id": "check_in_nurture", "label": "☕ Casual Check-in / Market Update (Warm/Cold Lead)"},
        {"id": "urgent_deadline", "label": "⏰ Urgent Follow-up / Expiring Opportunity"}
    ]


def generate_followup_message(
    lead: dict,
    channel: str = "WhatsApp",
    template_type: str = "auto",
    agent_name: str = "Your Real Estate Advisor",
    agent_company: str = "Prime Realty Group"
) -> dict:
    """
    Generates a personalized communication draft for WhatsApp, SMS, or Email.
    
    Returns a dict with:
    - subject: (For Email)
    - body: The drafted message text
    - whatsapp_link: Direct WhatsApp link if phone is present
    - channel: Selected channel
    """
    # Extract lead details
    client_name = lead.get("name", "Valued Client").strip()
    first_name = client_name.split()[0] if client_name else "there"
    prop_type = lead.get("property_preference", "residential property").strip()
    location = lead.get("location_preference", "").strip()
    loc_text = f" in {location}" if location and location.lower() != "any" else ""
    budget_raw = float(lead.get("budget", 0) or 0)
    budget_str = format_currency(budget_raw) if budget_raw > 0 else "your preferred budget"
    status = lead.get("lead_status", "New")
    phone = lead.get("phone", "")

    # Auto-resolve template if "auto" was selected
    if template_type == "auto":
        if status == "New":
            template_type = "welcome_new"
        elif status == "Contacted":
            template_type = "site_visit_invite"
        elif status == "Site Visit Scheduled":
            template_type = "post_visit_followup"
        elif status == "Negotiation":
            template_type = "price_negotiation"
        elif status in ("Interested", "Follow-up"):
            template_type = "site_visit_invite"
        else:
            template_type = "check_in_nurture"

    subject = ""
    body = ""

    # -------------------------------------------------------------
    # 1. WHATSAPP DRAFTS (Conversational, emoji-friendly, clear CTA)
    # -------------------------------------------------------------
    if channel.lower() == "whatsapp":
        if template_type == "welcome_new":
            body = (
                f"Hi {first_name}! 👋 Thank you for inquiring about {prop_type}{loc_text}.\n\n"
                f"I'm {agent_name} with {agent_company}. I have curated a few exceptional options matching "
                f"a budget around {budget_str}. Would you be free for a quick 5-minute call today to discuss "
                f"your exact specifications?"
            )
        elif template_type == "site_visit_invite":
            body = (
                f"Hello {first_name}! 🏡 Hope you're having a productive week.\n\n"
                f"We just listed 2 premium {prop_type} options{loc_text} that align seamlessly with your {budget_str} range. "
                f"I'd love to organize a private on-site walkthrough for you this week. "
                f"Would Thursday afternoon or Saturday morning suit you best?"
            )
        elif template_type == "post_visit_followup":
            body = (
                f"Hi {first_name}! 🌟 It was great touring the property with you.\n\n"
                f"I wanted to hear your honest impressions of the layout and location. Did this property meet "
                f"your expectations, or would you like me to tweak our search parameters for other {prop_type} options?"
            )
        elif template_type == "price_negotiation":
            body = (
                f"Hello {first_name}! 🤝 I have an update regarding the {prop_type}{loc_text}.\n\n"
                f"I spoke with the sellers regarding the offer terms we discussed. They are open to discussing agreeable terms. "
                f"Could you take a quick call this afternoon so we can review the pricing details?"
            )
        elif template_type == "urgent_deadline":
            body = (
                f"Hi {first_name}, urgent update! ⏳\n\n"
                f"We just received multiple inquiries on the {prop_type}{loc_text} in your {budget_str} bracket. "
                f"If you're still interested, let's connect right away before the seller finalizes another offer."
            )
        else:  # check_in_nurture
            body = (
                f"Hi {first_name}! 👋 Just checking in from {agent_company}.\n\n"
                f"The market in{loc_text or ' the area'} has seen interesting new listings for {prop_type}. "
                f"Whenever you're ready to resume your property search, let me know and I'll send over the latest catalog!"
            )

    # -------------------------------------------------------------
    # 2. SMS DRAFTS (Crisp, under 160 chars where possible)
    # -------------------------------------------------------------
    elif channel.lower() == "sms":
        if template_type == "welcome_new":
            body = f"Hi {first_name}, thanks for inquiring on {prop_type}! I have curated units in your {budget_str} range. Free for a brief call? - {agent_name}, {agent_company}"
        elif template_type == "site_visit_invite":
            body = f"Hi {first_name}, 2 great {prop_type} listings just opened{loc_text}. Can I schedule a private tour for you this weekend? - {agent_name}"
        elif template_type == "post_visit_followup":
            body = f"Hi {first_name}, thank you for touring today! How did you like the {prop_type}? Happy to send over floor plans and payment schedules. - {agent_name}"
        elif template_type == "price_negotiation":
            body = f"Hi {first_name}, update on the {prop_type}: the seller is willing to discuss terms. Please call me back at your earliest convenience. - {agent_name}"
        elif template_type == "urgent_deadline":
            body = f"Alert {first_name}: High interest on the {prop_type}{loc_text}. Let's finalize your offer today before it goes under contract. - {agent_name}"
        else:
            body = f"Hi {first_name}, checking in regarding your property search{loc_text}. New {prop_type} inventory just arrived. Let me know if you'd like a preview! - {agent_name}"

    # -------------------------------------------------------------
    # 3. EMAIL DRAFTS (Professional subject + detailed body)
    # -------------------------------------------------------------
    else:  # Email
        if template_type == "welcome_new":
            subject = f"Property Options for Your {prop_type} Search{loc_text}"
            body = (
                f"Dear {client_name},\n\n"
                f"Thank you for reaching out regarding your search for a {prop_type}{loc_text}. "
                f"My name is {agent_name}, and I specialize in matching clients with premier real estate opportunities.\n\n"
                f"Based on your target budget of approximately {budget_str}, I have curated several promising properties "
                f"that offer superb value, verified titles, and desirable amenities.\n\n"
                f"To best tailor our recommendations, could we schedule a brief 10-minute discovery call this week? "
                f"Please let me know a day and time that fits your calendar.\n\n"
                f"Warm regards,\n\n"
                f"{agent_name}\n"
                f"{agent_company}"
            )
        elif template_type == "site_visit_invite":
            subject = f"Invitation: Private Walkthrough of Selected {prop_type} Properties"
            body = (
                f"Dear {client_name},\n\n"
                f"I hope this note finds you well.\n\n"
                f"We have recently secured exclusive viewing access for select {prop_type} listings{loc_text} "
                f"that match your criteria and {budget_str} budget. In-person viewings are by far the most effective way "
                f"to evaluate natural lighting, layout quality, and neighborhood ambiance.\n\n"
                f"I would be delighted to host you for a private walkthrough. We have availability:\n"
                f"• Thursday afternoon between 2:00 PM and 5:00 PM\n"
                f"• Saturday morning between 10:00 AM and 1:00 PM\n\n"
                f"Please reply with your preferred slot, and I will reserve it and send the directions.\n\n"
                f"Best regards,\n\n"
                f"{agent_name}\n"
                f"{agent_company}"
            )
        elif template_type == "post_visit_followup":
            subject = f"Following up on our property walkthrough - {prop_type}"
            body = (
                f"Dear {client_name},\n\n"
                f"Thank you for taking the time to tour the {prop_type}{loc_text} with me today.\n\n"
                f"I wanted to gather your initial thoughts. Did the layout, finishing, and pricing align with your "
                f"expectations? If you'd like to review the official title documentation, HOA bylaws, or projected payment schedules, "
                f"I have them ready to share.\n\n"
                f"Looking forward to hearing your thoughts and guiding your next steps.\n\n"
                f"Sincerely,\n\n"
                f"{agent_name}\n"
                f"{agent_company}"
            )
        elif template_type == "price_negotiation":
            subject = f"Update: Offer & Negotiation Status for {prop_type}"
            body = (
                f"Dear {client_name},\n\n"
                f"I am writing to share a positive development regarding our negotiations for the {prop_type}{loc_text}.\n\n"
                f"Following our recent discussions, the sellers have expressed flexibility regarding closing timelines "
                f"and initial price adjustments closer to your target budget of {budget_str}.\n\n"
                f"To keep the momentum in your favor, I recommend we review the proposed contract addendum together today.\n\n"
                f"Please let me know when you are available for a call.\n\n"
                f"Best regards,\n\n"
                f"{agent_name}\n"
                f"{agent_company}"
            )
        else:
            subject = f"Market Insights & Exclusive Property Opportunities{loc_text}"
            body = (
                f"Dear {client_name},\n\n"
                f"I hope you are having a wonderful week.\n\n"
                f"I am reaching out with our latest market brief on {prop_type} inventory{loc_text}. "
                f"Whether you are planning to purchase in the coming months or exploring future options, staying ahead "
                f"of price trends and emerging listings is essential.\n\n"
                f"Whenever you would like to revisit your property requirements, feel free to drop me a note or call.\n\n"
                f"Warm regards,\n\n"
                f"{agent_name}\n"
                f"{agent_company}"
            )

    # Clean phone digits for WhatsApp URL
    clean_phone_digits = "".join(filter(str.isdigit, phone))
    encoded_message = urllib.parse.quote(body)
    whatsapp_link = f"https://wa.me/{clean_phone_digits}?text={encoded_message}" if clean_phone_digits else ""

    return {
        "channel": channel,
        "template_type": template_type,
        "subject": subject,
        "body": body,
        "whatsapp_link": whatsapp_link,
        "client_name": client_name,
        "phone": phone
    }
