import re

COMPLEX_KEYWORDS = [
    "roi", "return on investment", "yield", "capital appreciation", 
    "market analysis", "trends", "forecast", "legal", "mortgage", "financing"
]

def should_escalate(user_message: str, extraction_attempts: int = 0) -> bool:
    """
    Decides whether to route to a smarter model (Claude) or stay with local (Llama).
    Returns True if we should escalate to Claude.
    """
    msg_lower = user_message.lower()
    
    # 1. Check for complex financial/legal queries
    if any(keyword in msg_lower for keyword in COMPLEX_KEYWORDS):
        return True
    
    # 2. Check for repeated extraction failures
    if extraction_attempts >= 2:
        return True
        
    # 3. Default to Local
    return False

def select_model(escalate: bool) -> str:
    return "Cloud-Claude" if escalate else "Local-Llama"
