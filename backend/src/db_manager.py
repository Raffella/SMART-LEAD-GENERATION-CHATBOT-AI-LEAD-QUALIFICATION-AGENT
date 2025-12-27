import os
from datetime import datetime
from supabase import create_client, Client
from models.schemas import LeadProfile, Session
from config.settings import config
from typing import Dict, Any, List, Optional
import json

class DatabaseManager:
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.client: Optional[Client] = None
        
        if self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                print("✅ Supabase Client Initialized")
            except Exception as e:
                print(f"⚠️ Supabase Init Failed: {e}")
        else:
            print("⚠️ SUPABASE_URL or SUPABASE_KEY not found. Running in MOCK DB mode.")

    def upsert_lead(self, session_id: str, profile: LeadProfile, score: int):
        """
        Inserts or updates a lead record in the 'leads' table.
        """
        if not self.client:
            print(f"[MOCK DB] Upsert Lead {session_id}: {profile.dict()}")
            return
        
        try:
            data = {
                "session_id": session_id,
                "investment_type": profile.investment_type,
                "budget": profile.budget_range,
                "property_type": profile.property_type,
                "bedrooms": profile.bedrooms,
                "location": profile.target_location,
                "language": profile.language_preference,
                "urgency": profile.urgency,
                "score": score,
                "updated_at": datetime.now().isoformat()
            }
            # Upsert based on session_id (assuming it's a unique key or primary key)
            self.client.table("leads").upsert(data, on_conflict="session_id").execute()
        except Exception as e:
            print(f"❌ DB Error (upsert_lead): {e}")

    def log_conversation(self, session_id: str, messages: List[Any]):
        """
        Logs the full conversation history to 'conversations' table.
        """
        if not self.client:
            # print(f"[MOCK DB] Log Conversation {session_id}: {len(messages)} messages")
            return

        try:
            # Convert internal Message objects to dicts
            msgs_json = [m.dict() if hasattr(m, "dict") else m for m in messages]
            
            data = {
                "session_id": session_id,
                "messages": msgs_json,
                "updated_at": datetime.now().isoformat()
            }
            self.client.table("conversations").upsert(data, on_conflict="session_id").execute()
        except Exception as e:
            print(f"❌ DB Error (log_conversation): {e}")

db_manager = DatabaseManager()
