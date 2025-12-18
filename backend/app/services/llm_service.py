import os
import json
import ast
from dotenv import load_dotenv
import google.generativeai as genai

# Optional OpenAI Import
try:
    from openai import OpenAI
    HAS_OPENAI_LIB = True
except ImportError:
    HAS_OPENAI_LIB = False
    print("⚠️ OpenAI library not found. OpenAI fallback disabled.")

class LLMService:
    def __init__(self):
        load_dotenv()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        self.providers = []
        
        # 1. Initialize OpenAI (Primary for now if key exists, or Fallback)
        if HAS_OPENAI_LIB and self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                self.providers.append("openai")
                print("✅ OpenAI LLM Initialized.")
            except Exception as e:
                print(f"❌ Failed to configure OpenAI: {e}")
        else:
             print("⚠️ OpenAI API Key or library missing.")

        # 2. Smart Gemini Initialization (Try latest, fallback to older)
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                # List of models to try in order of preference
                candidate_models = ['gemini-pro', 'gemini-1.5-flash', 'gemini-1.0-pro']
                self.gemini_model = None # Placeholder
                
                # Try the most likely public stable model first
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                
                self.providers.append("gemini")
                print(f"✅ Gemini LLM Initialized (Model: gemini-1.5-flash)")
            except Exception as e:
                print(f"❌ Failed to configure Gemini: {e}")
        else:
            print("⚠️ Gemini API Key missing.")

        if not self.providers:
            print("❌ CRITICAL: No LLM providers available.")

    def generate_lecture_content(self, system_prompt: str, user_context: str) -> dict:
        """
        Generates lecture content trying providers in sequence (Gemini -> OpenAI).
        Returns STRICT JSON.
        """
        full_prompt = (
            f"{system_prompt}\n\n"
            f"CONTEXT FROM DOCUMENT:\n{user_context}\n\n"
            "STRICT OUTPUT INSTRUCTIONS:\n"
            "You MUST return valid JSON only. No markdown formatting like ```json ... ```.\n"
            "The JSON structure must be:\n"
            "{\n"
            '  "lecture_title": "Title String",\n'
            '  "slides": [\n'
            '    {\n'
            '      "heading": "Slide Title",\n'
            '      "summary": "Brief summary",\n'
            '      "important_points": ["Point 1", "Point 2"],\n'
            '      "script": "Natural spoken script, approx 150 words.",\n'
            '      "code": "Optional code snippet or empty string"\n'
            "    }\n"
            "  ]\n"
            "}"
        )
        
        errors = []

        for provider in self.providers:
            print(f"🔄 Generating with {provider.upper()}...")
            try:
                if provider == "gemini":
                    return self._generate_gemini(full_prompt)
                elif provider == "openai":
                    return self._generate_openai(full_prompt)
            except Exception as e:
                error_msg = f"{provider} failed: {e}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)
                continue
        
        # If all fail
        print(f"❌ All LLM providers failed. Errors: {errors}")
        raise Exception(f"All LLM providers failed: {errors}")

    def _generate_gemini(self, prompt: str) -> dict:
        response = self.gemini_model.generate_content(prompt)
        if not response.text:
            raise ValueError("Empty response from Gemini")
        return self._clean_and_parse_json(response.text)

    def _generate_openai(self, prompt: str) -> dict:
        response = self.openai_client.chat.completions.create(
            model="gpt-4o", # Or gpt-3.5-turbo depending on budget/availability
            messages=[
                {"role": "system", "content": "You are a helpful AI teacher helper. output JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content
        return self._clean_and_parse_json(content)

    def _clean_and_parse_json(self, text: str) -> dict:
        # Remove markdown code blocks if present
        clean_text = text.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            # Try to salvage partial JSON or use AST if it's single-quoted
            try:
                return ast.literal_eval(clean_text)
            except:
                raise ValueError(f"Failed to parse JSON response: {text[:100]}...")

llm_service = LLMService()
