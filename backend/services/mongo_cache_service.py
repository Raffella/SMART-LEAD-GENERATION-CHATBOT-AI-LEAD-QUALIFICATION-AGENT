from pymongo import MongoClient, IndexModel, ASCENDING
from config.settings import config
from datetime import datetime, timedelta
import hashlib
import certifi

class MongoCacheService:
    def __init__(self):
        try:
            self.client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=2000, tlsCAFile=certifi.where())
            self.db = self.client[config.MONGO_DB_NAME]
            self.collection = self.db.cache
            # Create TTL index (7 days)
            self.collection.create_index("created_at", expireAfterSeconds=7 * 24 * 3600)
            self.client.server_info() # Trigger connection check
            print("MongoDB initialized successfully.")
        except Exception as e:
            print(f"Warning: MongoDB initialization failed ({e}). Caching disabled.")
            self.collection = None

    def _generate_hash(self, session_context: str, user_message: str) -> str:
        raw_string = f"{session_context}|{user_message}"
        return hashlib.sha256(raw_string.encode()).hexdigest()

    def get_cached_response(self, session_id: str, user_message: str):
        if self.collection is None:
            return None
        
        # We use a simple hash of last few messages + current message
        # For simplicity in this demo, just hashing the user message might be risky if we need context.
        # But the prompt says "hash of session + userMessage". 
        cache_key = self._generate_hash(session_id, user_message)
        
        doc = self.collection.find_one({"_id": cache_key})
        if doc:
            return doc.get("response")
        return None

    def cache_response(self, session_id: str, user_message: str, response_data: dict):
        if self.collection is None:
            return

        cache_key = self._generate_hash(session_id, user_message)
        document = {
            "_id": cache_key,
            "session_id": session_id,
            "user_message": user_message,
            "response": response_data,
            "created_at": datetime.utcnow()
        }
        try:
            self.collection.replace_one({"_id": cache_key}, document, upsert=True)
        except Exception as e:
            print(f"Failed to cache response: {e}")

mongo_cache_service = MongoCacheService()
