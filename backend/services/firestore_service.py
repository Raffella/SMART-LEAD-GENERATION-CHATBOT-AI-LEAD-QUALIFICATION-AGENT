try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    firebase_admin = None
    firestore = None
from models.schemas import Session, Message, LeadProfile
from config.settings import config
from datetime import datetime
import json
import os
try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None


import certifi

class FirestoreService:
    def __init__(self):
        # Fallback priority: Firestore (Real) > MongoDB (Real) > File (Mock)
        self.mode = "MOCK" 
        
        # 1. Try Firestore
        try:
            if config.FIREBASE_CREDENTIALS_PATH and os.path.exists(config.FIREBASE_CREDENTIALS_PATH):
                if not firebase_admin._apps:
                    cred = credentials.Certificate(config.FIREBASE_CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred, {'projectId': config.FIREBASE_PROJECT_ID})
                self.db = firestore.client()
                self.collection_ref = self.db.collection('realestate_sessions')
                self.mode = "FIRESTORE"
                print("Using: Firestore (Real)")
                return
        except Exception:
            pass

        # 2. Try MongoDB (Disabled for stability during dev/test)
        # try:
        #     self.mongo_client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=2000, tlsCAFile=certifi.where())
        #     self.mongo_client.server_info() # Trigger check
        #     self.mongo_db = self.mongo_client[config.MONGO_DB_NAME]
        #     self.mongo_coll = self.mongo_db.sessions
        #     self.mode = "MONGODB"
        #     print("Using: MongoDB (Sessions)")
        #     return
        # except Exception as e:
        #     print(f"MongoDB connection failed: {e}")

        # 3. Fallback to File
        print("Using: File-based Mock DB")
        self.mode = "FILE"
        self.mock_store = self._load_from_file()
        self.db_file = "local_db.json"

    def _load_from_file(self):
        if os.path.exists("local_db.json"):
            try:
                with open("local_db.json", 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_to_file(self):
        with open("local_db.json", 'w') as f:
            json.dump(self.mock_store, f, indent=2, default=str)

    def get_or_create_session(self, user_id: str, session_id: str) -> Session:
        # A. Firestore
        if self.mode == "FIRESTORE":
            doc_ref = self.collection_ref.document(session_id)
            doc = doc_ref.get()
            if doc.exists:
                return Session(**doc.to_dict())
            else:
                new_session = Session(session_id=session_id, user_id=user_id)
                doc_ref.set(json.loads(new_session.json()))
                return new_session

        # B. MongoDB
        elif self.mode == "MONGODB":
            doc = self.mongo_coll.find_one({"session_id": session_id})
            if doc:
                # MongoDB stores _id, remove it or ignore it
                if "_id" in doc: del doc["_id"]
                return Session(**doc)
            else:
                new_session = Session(session_id=session_id, user_id=user_id)
                self.mongo_coll.insert_one(json.loads(new_session.json()))
                return new_session
        
        # C. File Mock
        else:
            if session_id in self.mock_store:
                return Session(**self.mock_store[session_id])
            new_session = Session(session_id=session_id, user_id=user_id)
            self.mock_store[session_id] = json.loads(new_session.json())
            self._save_to_file()
            return new_session

    def save_session(self, session: Session):
        session.updated_at = datetime.utcnow()
        data = json.loads(session.json())

        if self.mode == "FIRESTORE":
            doc_ref = self.collection_ref.document(session.session_id)
            doc_ref.set(data)
        elif self.mode == "MONGODB":
            # Upsert
            self.mongo_coll.replace_one({"session_id": session.session_id}, data, upsert=True)
        else:
            self.mock_store[session.session_id] = data
            self._save_to_file()

    def get_all_sessions(self):
        if self.mode == "FIRESTORE":
            return [] # Security precaution, or implement listing
        elif self.mode == "MONGODB":
            cursor = self.mongo_coll.find({})
            sessions = []
            for doc in cursor:
                if "_id" in doc: del doc["_id"]
                sessions.append(doc)
            return sessions
        else:
            return list(self.mock_store.values())

firestore_service = FirestoreService()
