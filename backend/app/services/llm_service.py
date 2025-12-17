import os
import requests

# Optional Import for Gemini
try:
    import google.generativeai as genai
    HAS_GEMINI_LIB = True
except ImportError:
    HAS_GEMINI_LIB = False
    print("⚠️ google.generativeai library not found. Gemini provider disabled.")

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        # Determine provider based on API Key presence AND Library presence
        if HAS_GEMINI_LIB and self.api_key and self.api_key.startswith("AIza"):
            self.provider = "gemini"
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            print("✅ LLM Service initialized with provider: GEMINI")
        else:
            self.provider = "ollama"
            self.ollama_base_url = "http://localhost:11434/api/generate"
            self.ollama_model = "mistral"  # You can change this to 'llama3' or 'gemma'
            print("⚠️ GEMINI_API_KEY not found/invalid. Switching to provider: OLLAMA")
            print(f"👉 Ensure Ollama is running (http://localhost:11434) and '{self.ollama_model}' model is pulled.")

    def generate_lecture_content(self, system_prompt: str, user_context: str) -> str:
        """
        Generates lecture content using the selected LLM provider.
        """
        full_prompt = f"{system_prompt}\n\nCONTEXT:\n{user_context}"

        if self.provider == "gemini":
            return self._generate_gemini(full_prompt)
        else:
            return self._generate_ollama(full_prompt)

    def _generate_gemini(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    def _generate_ollama(self, prompt: str) -> str:
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3, # Teaching needs to be structured
                "num_ctx": 4096     # Ensure context fits
            }
        }
        try:
            response = requests.post(self.ollama_base_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama. Is it running on port 11434?"
        except Exception as e:
            return f"Ollama Error: {str(e)}"

llm_service = LLMService()
