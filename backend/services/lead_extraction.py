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
        if "asap" in msg_lower or "urgent" in msg_lower or "now" in msg_lower or "this month" in msg_lower:
            current_profile.urgency = "High"
        
        # 7. Language
        if any("\u0600" <= c <= "\u06FF" for c in user_message):
             current_profile.language_preference = "ar"

        return current_profile

    def calculate_lead_score(self, profile: LeadProfile) -> int:
        score = 0
        # Completeness
        fields = [profile.investment_type, profile.budget_range, profile.property_type, profile.bedrooms, profile.target_location]
        filled_count = sum(1 for f in fields if f)
        score += filled_count * 10 

        # Budget size (Naively scanning for 'm' or big digits)
        if profile.budget_range:
            if "m" in profile.budget_range.lower() or "million" in profile.budget_range.lower():
                score += 30
        
        # Urgency
        if profile.urgency == "High":
            score += 20
        
        return score

    def check_qualification_status(self, profile: LeadProfile) -> ProcessStatus:
        fields = [profile.investment_type, profile.budget_range, profile.property_type, profile.bedrooms, profile.target_location]
        if all(fields):
            return ProcessStatus.QUALIFIED
        elif any(fields):
            return ProcessStatus.DISCOVERY
        return ProcessStatus.INITIAL

lead_extractor = LeadExtractionService()
