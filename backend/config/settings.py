import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Server
    PORT = int(os.getenv("PORT", 8000))
    BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

    # Firestore
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase_credentials.json")
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "everest-view-property")

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "realestate_db")

    # LLM
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/chat")
    MODEL_NAME = os.getenv("MODEL_NAME", "phi3:mini")
    MODEL_SOURCE = os.getenv("MODEL_SOURCE", "ollama") # or 'openai'

    # Notifications
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
    SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
    SALES_TEAM_EMAIL = os.getenv("SALES_TEAM_EMAIL", "")
    SALES_TEAM_PHONE = os.getenv("SALES_TEAM_PHONE", "")

config = Config()
