import os
from config.settings import config
from models.schemas import LeadProfile

# Try importing libraries, handle mock if missing
try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    TwilioClient = None

try:
    import resend
except ImportError:
    resend = None

class NotificationManager:
    def __init__(self):
        self.twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.twilio_auth = os.environ.get("TWILIO_AUTH_TOKEN")
        self.twilio_from = os.environ.get("TWILIO_PHONE_NUMBER")
        self.sales_phone = config.SALES_TEAM_PHONE
        
        self.resend_key = os.environ.get("RESEND_API_KEY")
        self.sales_email = config.SALES_TEAM_EMAIL

        self.twilio_client = None
        if TwilioClient and self.twilio_sid and self.twilio_auth:
            try:
                self.twilio_client = TwilioClient(self.twilio_sid, self.twilio_auth)
                print("✅ Twilio Client Initialized")
            except Exception as e:
                print(f"⚠️ Twilio Init Failed: {e}")

        if resend and self.resend_key:
            resend.api_key = self.resend_key
            print("✅ Resend Client Initialized")
        else:
            print("⚠️ RESEND_API_KEY not found or lib missing.")

    def send_sms(self, lead: LeadProfile):
        msg_body = f"🔥 HOT LEAD: {lead.name or 'Unknown'} ({lead.phone_number or 'No Phone'}). Budget: {lead.budget_range}. Location: {lead.target_location}. Score: {lead.lead_score}"
        
        if self.twilio_client and self.twilio_from:
            try:
                message = self.twilio_client.messages.create(
                    body=msg_body,
                    from_=self.twilio_from,
                    to=self.sales_phone
                )
                print(f"✅ SMS Sent: {message.sid}")
            except Exception as e:
                print(f"❌ SMS Failed: {e}")
        else:
            print(f"[MOCK SMS] To: {self.sales_phone} | Body: {msg_body}")

    def send_email(self, lead: LeadProfile, session_id: str):
        subject = f"New Qualified Lead - {lead.budget_range} ({lead.target_location})"
        html_content = f"""
        <h2>New High-Quality Lead</h2>
        <p><strong>Session ID:</strong> {session_id}</p>
        <ul>
            <li><strong>Name:</strong> {lead.name}</li>
            <li><strong>Phone:</strong> {lead.phone_number}</li>
            <li><strong>Email:</strong> {lead.email}</li>
            <li><strong>Investment:</strong> {lead.investment_type}</li>
            <li><strong>Budget:</strong> {lead.budget_range}</li>
            <li><strong>Type:</strong> {lead.property_type}</li>
            <li><strong>Bedrooms:</strong> {lead.bedrooms}</li>
            <li><strong>Location:</strong> {lead.target_location}</li>
            <li><strong>Score:</strong> {lead.lead_score}</li>
        </ul>
        <p>Please contact immediately.</p>
        """
        
        if resend and self.resend_key:
            try:
                r = resend.Emails.send({
                    "from": "AI Agent <onboarding@resend.dev>",
                    "to": self.sales_email,
                    "subject": subject,
                    "html": html_content
                })
                print(f"✅ Email Sent: {r}")
            except Exception as e:
                print(f"❌ Email Failed: {e}")
        else:
            print(f"[MOCK EMAIL] To: {self.sales_email} | Subject: {subject}")

    def trigger_call(self):
        # Simulated call logic or Twilio Voice
        if self.twilio_client and self.twilio_from:
             print(f"📞 Initiating Twilio Call to {self.sales_phone}...")
             try:
                call = self.twilio_client.calls.create(
                    twiml='<Response><Say voice="alice">You have a new qualified lead waiting for your review. Please check the dashboard immediately.</Say></Response>',
                    to=self.sales_phone,
                    from_=self.twilio_from
                )
                print(f"✅ Call Initiated: {call.sid}")
             except Exception as e:
                print(f"❌ Call Failed: {e}")
        else:
             print("[MOCK CALL] Ringing Sales Team...")

notification_manager = NotificationManager()
