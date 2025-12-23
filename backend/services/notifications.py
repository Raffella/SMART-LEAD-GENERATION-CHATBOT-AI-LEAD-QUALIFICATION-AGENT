from config.settings import config
from models.schemas import LeadProfile

class NotificationService:
    def __init__(self):
        # In a real app, initialize SendGrid/Twilio clients here
        pass

    def send_qualified_lead_notification(self, lead: LeadProfile, session_id: str):
        subject = f"🔥 NEW QUALIFIED LEAD - {lead.budget_range}"
        body = f"""
        New Lead Qualified!
        Session ID: {session_id}
        
        Profile:
        - Investment: {lead.investment_type}
        - Budget: {lead.budget_range}
        - Type: {lead.property_type}
        - Bedrooms: {lead.bedrooms}
        - Location: {lead.target_location}
        - Urgency: {lead.urgency}
        - Score: {lead.lead_score}
        
        Contact immediately!
        """
        
        # Mock Email
        print(f"--- [MOCK SENDGRID] Sending Email to {config.SALES_TEAM_EMAIL} ---")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print("-----------------------------------------------------------------")

        # Mock SMS
        sms_body = f"HOT LEAD: {lead.budget_range} for {lead.property_type} in {lead.target_location}. Score: {lead.lead_score}"
        print(f"--- [MOCK TWILIO] Sending SMS to {config.SALES_TEAM_PHONE} ---")
        print(f"Message: {sms_body}")
        print("----------------------------------------------------------------")

notification_service = NotificationService()
