from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import ChatRequest, ChatResponse, Message, MessageRole, ProcessStatus
from services.firestore_service import firestore_service
from services.mongo_cache_service import mongo_cache_service
from src.graph import graph # LangGraph Integation
from services.llm_service import llm_service
from services.lead_extraction import lead_extractor
from services.notifications import notification_service
from config.settings import config
import uuid
import io
import base64
from gtts import gTTS

app = FastAPI(title="Real Estate AI Chatbot")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = request.sessionId
    user_id = request.userId
    user_message = request.userMessage
    language = request.language or "en"

    # 1. Fetch Session
    session = firestore_service.get_or_create_session(user_id, session_id)
    if language != session.lead_profile.language_preference:
        session.lead_profile.language_preference = language

    # 2. Check Cache
    last_assistant_msg = ""
    if session.messages and session.messages[-1].role == MessageRole.ASSISTANT:
        last_assistant_msg = session.messages[-1].content
    
    session_context_hash = f"{session_id}:{last_assistant_msg}:{language}"
    
    cached_reply_data = mongo_cache_service.get_cached_response(session_context_hash, user_message)
    if cached_reply_data:
        print(f"Cache Hit for session {session_id}")
        return ChatResponse(
            reply=cached_reply_data["reply"],
            leadProfile=session.lead_profile,
            qualificationStatus=session.qualification_status,
            leadScore=session.lead_profile.lead_score,
            audioBase64=cached_reply_data.get("audioBase64")
        )

    # 3. LangGraph Execution
    # Prepare State
    msgs = [{"role": m.role, "content": m.content} for m in session.messages]
    msgs.append({"role": "user", "content": user_message})

    initial_state = {
        "session_id": session_id,
        "messages": msgs,
        "lead_profile": session.lead_profile,
        "qualification_status": session.qualification_status,
        "extraction_attempts": 0, # In a real app, persist this
        "model_used": "Local-Llama",
        "latest_reply": "",
        "audio_base64": None,
        "language": language
    }

    print(">>> INVOKING LANGGRAPH <<<")
    final_state = graph.invoke(initial_state)
    
    llm_reply = final_state["latest_reply"]
    updated_profile = final_state["lead_profile"]
    new_status = final_state["qualification_status"]

    # 4. Audio Generation (Text-to-Speech)
    audio_base64 = None
    try:
        tts = gTTS(text=llm_reply, lang=language, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
    except Exception as e:
        print(f"TTS Generation failed: {e}")

    # 5. Save everything
    session.lead_profile = updated_profile
    session.qualification_status = new_status
    session.messages.append(Message(role=MessageRole.USER, content=user_message))
    session.messages.append(Message(role=MessageRole.ASSISTANT, content=llm_reply))
    
    firestore_service.save_session(session)

    # 6. Cache Response
    response_payload = {
        "reply": llm_reply,
        "audioBase64": audio_base64
    }
    mongo_cache_service.cache_response(session_context_hash, user_message, response_payload)

    return ChatResponse(
        reply=llm_reply,
        leadProfile=updated_profile,
        qualificationStatus=new_status,
        leadScore=updated_profile.lead_score,
        audioBase64=audio_base64
    )

@app.get("/admin/sessions")
async def get_all_sessions():
    return firestore_service.get_all_sessions()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
