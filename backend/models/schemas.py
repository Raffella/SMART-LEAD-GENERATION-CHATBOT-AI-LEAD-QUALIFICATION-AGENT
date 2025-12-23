from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid

class ProcessStatus(str, Enum):
    INITIAL = "INITIAL"
    DISCOVERY = "DISCOVERY"
    QUALIFIED = "QUALIFIED"
    NEEDS_REVIEW = "NEEDS_REVIEW"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class LeadProfile(BaseModel):
    investment_type: Optional[str] = None # Off-plan or Ready
    budget_range: Optional[str] = None
    property_type: Optional[str] = None # Apartment, Villa, Townhouse
    bedrooms: Optional[str] = None
    target_location: Optional[str] = None
    language_preference: str = "en"
    urgency: Optional[str] = None
    lead_score: int = 0

class Session(BaseModel):
    session_id: str
    user_id: str
    messages: List[Message] = []
    qualification_status: ProcessStatus = ProcessStatus.INITIAL
    lead_profile: LeadProfile = Field(default_factory=LeadProfile)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    userId: str
    sessionId: str
    userMessage: str
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    reply: str
    leadProfile: LeadProfile
    qualificationStatus: ProcessStatus
    leadScore: int
    audioBase64: Optional[str] = None
