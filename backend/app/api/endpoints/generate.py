from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import rag_service
from app.core.prompts import TEACHER_SYSTEM_PROMPT

# Pre-load services at module level to avoid blocking the first request
from app.services.llm_service import llm_service
from app.services.orchestrator_service import orchestrator_service
from app.services.slide_service import slide_service
from app.services.tts_service import tts_service
from app.services.avatar_service import avatar_service

router = APIRouter()

class GenerateRequest(BaseModel):
    topic: str = "General Overview"

@router.post("/generate-lecture-plan")
async def generate_lecture_plan(request: GenerateRequest):
    print("Received generation request for topic:", request.topic)
    # Retrieve context relevant to the topic
    # If topic is general, we might want to sample widely or use a summary
    context_chunks = rag_service.search(request.topic, k=5)
    retrieved_context = "\n\n".join(context_chunks)

    if not retrieved_context:
        return {"error": "No context found. Please upload a PDF first."}
    
    # 1. Generate Text
    
    # 1. Generate Text
    lecture_content = llm_service.generate_lecture_content(TEACHER_SYSTEM_PROMPT, retrieved_context)
    
    # [MANDATORY REQUIREMENT] Store Debug Data (Context, Prompt, Output)
    import os
    import time
    debug_dir = os.path.join(os.getcwd(), "data", "outputs", "scripts")
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = int(time.time())
    
    debug_file = os.path.join(debug_dir, f"generation_{timestamp}.txt")
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write("=== RETRIEVED CONTEXT ===\n")
        f.write(retrieved_context + "\n\n")
        f.write("=== SYSTEM PROMPT ===\n")
        f.write(TEACHER_SYSTEM_PROMPT + "\n\n")
        f.write("=== LLM OUTPUT (Script) ===\n")
        f.write(lecture_content)
    
    # 2. Trigger Pipeline (Generate Assets)
    pipeline_results = await orchestrator_service.execute_pipeline(
        lecture_content, 
        slide_service, 
        tts_service, 
        avatar_service
    )

    return {
        "status": "Completed",
        "lecture_content": lecture_content, # Debug info
        "pipeline_results": pipeline_results, # The actual URLs for frontend
        "message": "Lecture generated successfully with Slides and Audio."
    }
