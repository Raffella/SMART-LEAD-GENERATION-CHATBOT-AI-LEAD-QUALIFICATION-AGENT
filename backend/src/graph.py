from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from models.schemas import LeadProfile, ProcessStatus
from services.llm_service import llm_service
from services.lead_extraction import lead_extractor
from src.hybrid_router import should_escalate, select_model
from src.notify import notification_manager
from src.db_manager import db_manager

# Define State
class LeadAgentState(TypedDict):
    session_id: str
    messages: List[Dict[str, str]] # [{'role': 'user', 'content': '...'}, ...]
    lead_profile: LeadProfile
    qualification_status: ProcessStatus
    extraction_attempts: int
    model_used: str
    latest_reply: str
    audio_base64: Optional[str]
    language: str

# Node: Qualifier (The detailed worker)
def qualifier_node(state: LeadAgentState):
    user_msg = state['messages'][-1]['content']
    profile = state['lead_profile']
    
    # 1. Router Logic
    escalate = should_escalate(user_msg, state.get('extraction_attempts', 0))
    model = select_model(escalate)
    
    # Temporary: Update llm_service model on the fly (not thread safe in prod but ok for this demo)
    # Ideally pass model param to generate_response
    original_model = llm_service.model
    if model == "Cloud-Claude":
        # Placeholder for Claude integration
        # In real scenario: llm_service.generate_response(..., model="claude-3-5-sonnet")
        print(">>> SWITCHING TO CLAUDE (Simulated) <<<")
        # For now, we simulate Claude by just flagging it, 
        # as we might not have the API key set up in llm_service yet.
        pass

    # 2. Generate Reply
    # Create a dummy Session object because llm_service expects it
    # We must bridge the gap between new State and old Session object
    from models.schemas import Session as SchemaSession, Message as SchemaMessage
    
    schema_msgs = [SchemaMessage(role=m['role'], content=m['content']) for m in state['messages']]
    dummy_session = SchemaSession(
        session_id=state['session_id'],
        user_id="user",
        messages=schema_msgs,
        lead_profile=profile,
        qualification_status=state['qualification_status']
    )
    
    reply = llm_service.generate_response(dummy_session, user_msg, state['language'])
    
    # 3. Extract entities
    updated_profile = lead_extractor.extract_data(user_msg, profile)
    score = lead_extractor.calculate_lead_score(updated_profile)
    updated_profile.lead_score = score
    new_status = lead_extractor.check_qualification_status(updated_profile)
    
    # Check if extraction made progress?
    # For simplicity, we just increment attempts if score didn't increase significantly?
    # Or just reset attempts if we got new data.
    # Let's simple increment attempts if status is same.
    new_attempts = state['extraction_attempts'] + 1
    if new_status != state['qualification_status']:
         new_attempts = 0

    return {
        "lead_profile": updated_profile,
        "qualification_status": new_status,
        "lead_score": score,
        "model_used": model,
        "latest_reply": reply,
        "extraction_attempts": new_attempts
    }

# Node: Notifier
def notifier_node(state: LeadAgentState):
    profile = state['lead_profile']
    
    if profile.lead_score > 80 or state['qualification_status'] == ProcessStatus.QUALIFIED:
        # Trigger notifications
        notification_manager.send_sms(profile)
        notification_manager.send_email(profile, state['session_id'])
        if profile.lead_score > 90:
             notification_manager.trigger_call()
    
    # Persist to DB
    db_manager.upsert_lead(
        state['session_id'], 
        profile, 
        profile.lead_score
    )
    db_manager.log_conversation(state['session_id'], state['messages'])
    
    return {} # No state update needed, just side effects

# Build Graph
builder = StateGraph(LeadAgentState)

builder.add_node("qualifier", qualifier_node)
builder.add_node("notifier", notifier_node)

builder.set_entry_point("qualifier")

# Edge Logic
def should_notify(state: LeadAgentState):
    # If qualified or high score, go to notifier
    if state['qualification_status'] == ProcessStatus.QUALIFIED or state['lead_profile'].lead_score > 80:
        return "notifier"
    return END

builder.add_conditional_edges("qualifier", should_notify)
builder.add_edge("notifier", END)

graph = builder.compile()
