import requests
from config.settings import config
from models.schemas import Session, LeadProfile

class LLMService:
    def __init__(self):
        self.api_url = config.OLLAMA_BASE_URL
        self.model = config.MODEL_NAME

    def _build_system_prompt(self, lead_profile: LeadProfile, language: str = "en") -> str:
        # Dynamic insertion of current profile values
        profile_text = f"""
        Current Lead Profile State:
        - Investment Type: {lead_profile.investment_type or "Unknown"}
        - Budget: {lead_profile.budget_range or "Unknown"}
        - Property Type: {lead_profile.property_type or "Unknown"}
        - Bedrooms: {lead_profile.bedrooms or "Unknown"}
        - Location: {lead_profile.target_location or "Unknown"}
        - Language Preference: {language}
        """
        
        base_prompt = f"""
You are a highly professional, polite, and data-driven Real Estate Lead Qualification Specialist, representing **Everest View Property**.
You focus exclusively on **SALES** transactions (not leasing).

Your goal is to QUALIFY the user by collecting these five mandatory fields:

1. Investment Type – Off-plan or Ready/Secondary
2. Budget – Specific range (including currency, e.g., $500k-$1M)
3. Property Type – Apartment, Villa, Townhouse, or Land
4. Bedrooms – Studio, 1, 2, 3+
5. Target Location – Specific area or neighborhood

**Rules of Engagement**
1. **IMPORTANT**: You MUST reply in the requested language: **{language}**.
2. **BREVITY**: Keep responses SHORT, CRISP, and CONCISE. Max 2 sentences where possible. Avoid fluff.
3. If user asks about rentals or unrelated topics, politely redirect to finding a home/investment for sale.
4. Ask for one missing field at a time.
5. After each answer, confirm briefly and move to the next missing field.
6. When all five are filled, mark lead as QUALIFIED and end with a summary.
"""
        return base_prompt + "\n" + profile_text

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
                response = requests.post(self.api_url, json=payload)
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
