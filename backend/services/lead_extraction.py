import re
from models.schemas import LeadProfile, ProcessStatus

class LeadExtractionService:
    def __init__(self):
        # General Urban Real Estate Locations
        self.locations = [
            "Downtown", "Uptown", "Marina", "Business District", "Suburbs", 
            "City Center", "Beachfront", "Hills", "Valley", "Lakeside"
        ]
        self.property_types = ["Apartment", "Villa", "Townhouse", "Land", "Penthouse"]
        self.investment_types = ["Off-plan", "Ready", "Secondary"]

    def extract_data(self, user_message: str, current_profile: LeadProfile) -> LeadProfile:
        # Update fields if found in message
        # Naive keyword matching + Regex
        
        msg_lower = user_message.lower()

        # 1. Investment Type
        if "off-plan" in msg_lower or "off plan" in msg_lower:
            current_profile.investment_type = "Off-plan"
        elif "ready" in msg_lower or "secondary" in msg_lower or "move in" in msg_lower:
            current_profile.investment_type = "Ready/Secondary"

        # 2. Budget (Regex for quantities with currency context)
        # Matches: $1.5M, £2m, 500k, 2 million euros
        budget_match = re.search(r'(\d+(?:[.,]\d+)?[mk]?)', msg_lower)
        if budget_match:
            # Check for generic currency indicators or budget keywords
            currency_indicators = ["$", "£", "€", "dollars", "pounds", "euros", "budget", "price", "cost"]
             # Check if any indicator is in the message
            if any(ind in msg_lower for ind in currency_indicators):
                if re.search(r'\d+\s*(?:m|million|k|thousand)', msg_lower) or "$" in msg_lower or "€" in msg_lower or "£" in msg_lower:
                     current_profile.budget_range = user_message # Store raw string for now

        # 3. Property Type
        for p_type in self.property_types:
            if p_type.lower() in msg_lower:
                current_profile.property_type = p_type

        # 4. Bedrooms
        # "2 bedroom", "2 br", "studio", "3 beds"
        if "studio" in msg_lower:
            current_profile.bedrooms = "Studio"
        else:
            bd_match = re.search(r'(\d+)\s*(?:br|bed|room)', msg_lower)
            if bd_match:
                current_profile.bedrooms = f"{bd_match.group(1)} Bedroom(s)"

        # 5. Location
        for loc in self.locations:
            if loc.lower() in msg_lower:
                current_profile.target_location = loc

        # 6. Urgency (Heuristic)
        if "asap" in msg_lower or "urgent" in msg_lower or "now" in msg_lower or "this month" in msg_lower or "immediate" in msg_lower:
            current_profile.urgency = "High"
        
        # 7. Language
        if any("\u0600" <= c <= "\u06FF" for c in user_message):
             current_profile.language_preference = "ar"

        # 8. Email Extraction
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_message)
        if email_match:
            current_profile.email = email_match.group(0)

        # 9. Phone Extraction (Basic International Support)
        # Matches: +971 50 123 4567, 050-123-4567, 050 123 4567
        phone_match = re.search(r'(?:\+|00)?(?:\d[\s-]?){9,14}', user_message)
        if phone_match and len(re.sub(r'\D', '', phone_match.group(0))) >= 9:
             current_profile.phone_number = phone_match.group(0).strip()

        # 10. Name Extraction (Heuristics)
        # "My name is X", "I am X", "Call me X"
        name_patterns = [
            r"my name is ([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)",
            r"i am ([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)",
            r"call me ([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                # Basic check to avoid capturing "looking", "interested" as names if casing is ignored
                candidate = match.group(1)
                forbidden = ["looking", "interested", "searching", "buying", "selling"]
                if candidate.lower() not in forbidden:
                    current_profile.name = candidate.title()
                break

        return current_profile

    def calculate_lead_score(self, profile: LeadProfile) -> int:
        score = 0
        # Completeness
        fields = [
            profile.investment_type, profile.budget_range, profile.property_type, 
            profile.bedrooms, profile.target_location,
            profile.name, profile.phone_number, profile.email
        ]
        filled_count = sum(1 for f in fields if f)
        score += filled_count * 10 

        # Budget size (Naively scanning for 'm' or big digits)
        if profile.budget_range:
            if "m" in profile.budget_range.lower() or "million" in profile.budget_range.lower():
                score += 30
        
        if profile.urgency == "High":
            score += 20

        # Demo Priority: Contact Info is gold
        if profile.name: score += 20
        if profile.phone_number: score += 40
        
        return score

    def check_qualification_status(self, profile: LeadProfile) -> ProcessStatus:
        # Rapid Demo Mode: Qualified if Name+Phone AND (Property OR Budget) are known.
        has_contact = (profile.name and profile.phone_number)
        has_interest = (profile.property_type or profile.budget_range)
        
        if has_contact and has_interest:
             return ProcessStatus.QUALIFIED
        
        # Fallback to standard check if contact info is missing but other fields are there
        fields = [
             profile.investment_type, profile.budget_range, profile.property_type, 
             profile.bedrooms, profile.target_location
        ]
        if all(fields) and (profile.name or profile.phone_number or profile.email):
             return ProcessStatus.QUALIFIED
             
        elif any(fields) or has_contact:
            return ProcessStatus.DISCOVERY
        return ProcessStatus.INITIAL

lead_extractor = LeadExtractionService()
