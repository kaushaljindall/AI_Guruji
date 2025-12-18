import os
import requests
import time
from app.core.errors import LLMGenerationError

# Optional Import for Gemini
try:
    import google.generativeai as genai
    HAS_GEMINI_LIB = True
except ImportError:
    HAS_GEMINI_LIB = False
    print("⚠️ google.generativeai library not found. Gemini provider disabled.")

class LLMService:
    def __init__(self):
        # Configuration
        from dotenv import load_dotenv
        load_dotenv()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.ollama_base_url = "http://localhost:11434/api/generate"
        self.ollama_model = "gemma:2b"
        
        # Provider Order: Primary -> Secondary -> Fallback
        self.providers = []
        
        # 1. Register Gemini
        if HAS_GEMINI_LIB:
            if not self.gemini_api_key:
                print("⚠️ Gemini API Key not found in environment. Skipping Gemini.")
            elif self.gemini_api_key.startswith("Replace_With") or self.gemini_api_key.startswith("AIzaSyAdc9z20iPq4QdseowUxAJIrmcr4HUyqo4"):
                 # Check for default/placeholder keys
                 print("⚠️ Gemini API Key is default/placeholder. Skipping Gemini.")
            else:
                try:
                    genai.configure(api_key=self.gemini_api_key)
                    self.providers.append("gemini")
                except Exception as e:
                     print(f"⚠️ Failed to configure Gemini: {e}")
        else:
             print("⚠️ google.generativeai library not installed. Skipping Gemini.")

        # 2. Register Ollama (Always attempt if local)
        self.providers.append("ollama")

        # 3. Last Resort Mock
        self.providers.append("mock")

        print(f"✅ LLM Service initialized. Provider Chain: {self.providers}")

    def generate_lecture_content(self, system_prompt: str, user_context: str) -> str:
        """
        Generates lecture content trying providers in sequence.
        """
        full_prompt = f"{system_prompt}\n\nCONTEXT:\n{user_context}"
        
        errors = []

        for provider in self.providers:
            print(f"🔄 Attempting generation with provider: {provider.upper()}...")
            try:
                if provider == "gemini":
                    return self._generate_gemini(full_prompt)
                elif provider == "ollama":
                    return self._generate_ollama(full_prompt)
                elif provider == "mock":
                    return self._generate_mock(full_prompt)
                    
            except Exception as e:
                error_msg = f"{provider} failed: {str(e)}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)
                continue # Try next provider

        # If we reach here, ALL providers failed
        raise LLMGenerationError(
            message=f"All LLM providers failed. Errors: {'; '.join(errors)}",
            service_name="LLM_Service"
        )

    def _generate_gemini(self, prompt: str) -> str:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        if not response.text:
            raise ValueError("Empty response from Gemini")
        return response.text

    def _generate_ollama(self, prompt: str) -> str:
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_ctx": 4096}
        }
        # Increased timeout to 300s (5 mins) for slower CPU inference
        response = requests.post(self.ollama_base_url, json=payload, timeout=300) 
        # Added timeout to prevent infinite hang
        
        if response.status_code != 200:
             raise Exception(f"Ollama status {response.status_code}: {response.text}")
             
        data = response.json()
        return data.get("response", "")

    def _generate_mock(self, prompt: str) -> str:
        print("⚠️ USING MOCK LLM (FALLBACK) - Production would fail here.")
        # Minimal valid output to prevent crash
        return """
LECTURE_TITLE:
System Failure Recovery

TARGET_DURATION_MINUTES:
10

----------------------------------------------------

SLIDE 1:
HEADING: System Recovery Mode
SUMMARY: This is a fallback test lecture.
IMPORTANT POINTS:
- The Primary AI Brain is offline.
- This is a pre-written emergency script.
- The pipeline is functioning correctly.
SCRIPT:
Hello! This is a test message from the AI Guruji Recovery System. 
I am speaking to you because the main AI brain could not be reached. 
Don't worry, my voice means the audio system is working perfectly! 
Please check your Gemini API Key or Ollama server to restore full intelligence.
----------------------------------------------------
"""

llm_service = LLMService()
