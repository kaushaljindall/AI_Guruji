from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import rag_service
from app.core.prompts import TEACHER_SYSTEM_PROMPT
import uuid
import json
import os
import time

# Pre-load services
from app.services.llm_service import llm_service
from app.services.orchestrator_service import orchestrator_service
from app.services.slide_service import slide_service
from app.services.tts_service import tts_service
from app.services.avatar_service import avatar_service

router = APIRouter()

class GenerateRequest(BaseModel):
    document_id: str = "latest" # For now we just use the latest indexed index
    target_minutes: int = 10

@router.post("/generate-lecture")
async def generate_lecture(request: GenerateRequest):
    print(f"Received generation request. Duration: {request.target_minutes}min")
    
    # In this simple MVP, we ignore document_id and use the active FAISS index
    # We retrieve a general summary or context.
    # Since we don't have a specific query, we might fetch top chunks or just a generic "Overview"
    context_chunks = rag_service.search("Overview and key concepts", k=10)
    retrieved_context = "\n\n".join(context_chunks)

    if not retrieved_context:
        # If RAG is empty (no PDF uploaded), we might fallback or error
        # For now, let's allow it to proceed with empty context if that's the design, 
        # but the prompt implies RAG is mandatory.
        # Check if index is empty
        if rag_service.index.ntotal == 0:
             raise HTTPException(status_code=400, detail="No PDF uploaded/indexed. Please upload a PDF first.")

    # 1. Generate Content (Dict)
    try:
        lecture_data = llm_service.generate_lecture_content(TEACHER_SYSTEM_PROMPT, retrieved_context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Generation Failed: {str(e)}")
    
    # Debug Storage
    debug_dir = os.path.join(os.getcwd(), "data", "outputs", "scripts")
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = int(time.time())
    with open(os.path.join(debug_dir, f"generation_{timestamp}.txt"), "w", encoding="utf-8") as f:
        f.write(json.dumps(lecture_data, indent=2))
    
    # 2. Pipeline Execution (Audio, Slides)
    # This updates lecture_data with audio_urls etc.
    # Note: execute_pipeline currently returns {pptx_url, scene_count, segments}
    # It generates audio files but doesn't map them back to the lecture_data structure straightforwardly 
    # unless we update orchestrator or logic here.
    # The Frontend expects: "audio_url" inside each slide object.
    
    # Let's adjust logic:
    # We need to run TTS for each slide and inject the URL into lecture_data['slides']
    # The orchestrator currently composites video segments.
    # The PROMPT says: "Frontend show.jsx... plays audio_url... avatar lip-syncs".
    # And "NO video generation in backend." (Wait, "NO video generation in backend"?)
    # "NO avatar logic in backend."
    # BUT `orchestrator_service.py` was generating video segments!
    # The PROMPT says: "The frontend will handle: avatar rendering, lip synchronization".
    # So the backend should ONLY provide Audio + Slide + Data.
    # I should bypass the `orchestrator_service.execute_pipeline` video generation part 
    # and just do PPTX + TTS.
    
    # Refined Step 2:
    lecture_id = str(uuid.uuid4())
    slides = lecture_data.get("slides", [])
    
    try:
        # Generate PPTX
        slide_service.generate_presentation(lecture_data.get("lecture_title", "Lecture"), slides)
    except Exception as e:
        print(f"⚠️ PPTX Generation Failed: {e}. Skipping (Lecture will still work on web).")
    
    # Generate Audio for each slide
    for i, slide in enumerate(slides):
        script = slide.get("script", "")
        if script:
            audio_filename = f"{lecture_id}_slide_{i+1}.mp3"
            # tts_service returns (path, duration)
            try:
                path, duration = tts_service.generate_audio(script, audio_filename)
                # URL accessible via static mount
                slide["audio_url"] = f"/files/audio/{audio_filename}"
                slide["duration_seconds"] = duration
                slide["slide_id"] = i + 1
            except Exception as e:
                print(f"TTS failed for slide {i}: {e}. using fallback.")
                # Fallback to existing sample or silence
                slide["audio_url"] = "/sample.mp3" # Ensure this file exists in frontend/public or backend static
                slide["duration_seconds"] = 5
                slide["slide_id"] = i + 1
                slide["tts_error"] = str(e)

    # Save finalized lecture JSON
    lectures_dir = os.path.join(os.getcwd(), "data", "lectures")
    os.makedirs(lectures_dir, exist_ok=True)
    lecture_file = os.path.join(lectures_dir, f"{lecture_id}.json")
    
    with open(lecture_file, "w", encoding="utf-8") as f:
        json.dump(lecture_data, f, indent=2)
        
    return {"lecture_id": lecture_id}

@router.get("/lecture/{lecture_id}")
async def get_lecture(lecture_id: str):
    lecture_file = os.path.join(os.getcwd(), "data", "lectures", f"{lecture_id}.json")
    if not os.path.exists(lecture_file):
        raise HTTPException(status_code=404, detail="Lecture not found")
        
    with open(lecture_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return data
