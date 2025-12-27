import requests
from config.settings import config
from models.schemas import Session, LeadProfile

class LLMService:
    def __init__(self):
        self.api_url = config.OLLAMA_BASE_URL
        self.model = config.MODEL_NAME

    def _build_system_prompt(self, lead_profile: LeadProfile, language: str = "en") -> str:
        # Dynamic insertion of current profile values
        profile_text = f"Investment: {lead_profile.investment_type}\\nBudget: {lead_profile.budget_range}\\nType: {lead_profile.property_type}\\nBeds: {lead_profile.bedrooms}\\nLocation: {lead_profile.target_location}"
        
        base_prompt = f"""
You are a fast, efficient Real Estate Assistant for **Everest View Property**.
**GOAL**: Get the user's **Name & Phone Number** ASAP, then confirm their Request (Property/Budget).

**Current Known Information**:
{profile_text}
(Name: {lead_profile.name or 'Unknown'}, Phone: {lead_profile.phone_number or 'Unknown'})

**Instructions**:
1. **PRIORITY 1**: If 'Name' or 'Phone' is Unknown, **ASK FOR IT NOW**. Do not ask about property details until you have contact info.
2. **PRIORITY 2**: If you have Name+Phone, ask for the main requirement (e.g., "What kind of property are you looking for?" or "What is your budget?").
3. **DO NOT** ask about amenities, pools, views, or specific neighborhood boundaries.
4. **DO NOT** loop. If state shows "Unknown" but user just said it, assume the system missed it and ask *once* more clearly, or move to the next item.
5. Keep it SHORT. "Thanks [Name], what is your phone number?" is a perfect response.
6. Language: **{language}**.
"""
        return base_prompt

    def generate_response(self, session: Session, user_message: str, language: str = "en") -> str:
        system_prompt = self._build_system_prompt(session.lead_profile, language)
        
        # Build message history for context
        messages = [{"role": "system", "content": system_prompt}]
        for msg in session.messages:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})

        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False
            }
            if config.MODEL_SOURCE == "ollama":
                response = requests.post(self.api_url, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                print(f"DEBUG: Ollama Response Data: {data}")
                # Ollama returns 'message': {'role': 'assistant', 'content': '...'} or just 'response' depending on endpoint
                # The chat endpoint uses 'message', generate uses 'response'.
                # Assuming /api/chat based on payload structure. If /api/generate, structure is diff.
                # Default config OLLAMA_BASE_URL is /api/generate, but structure above is for /api/chat.
                # Let's adjust for /api/chat since we are sending "messages".
                
                # If the URL ends with /generate, we might need a different payload.
                # But let's assume the user will set OLLAMA_BASE_URL to .../api/chat OR we handle it.
                # Let's try to be robust. if "messages" is in payload, it should be chat endpoint.
                
                if "message" in data:
                    return data["message"]["content"]
                elif "response" in data:
                    return data["response"]
                else:
                    return "Error: Unexpected response format from Ollama."
            else:
                return "Mock OpenAI Response: This feature is pending."
                
        except Exception as e:
            print(f"LLM Call Failed: {e}")
            return "I apologize, but I am having trouble connecting to my brain right now. Please try again in a moment."

llm_service = LLMService()
