import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

from src.retriever import CandidateChunk
from src.prompt_builder import PromptBuilder


class GeminiLLMGenerator:
    """
    Server-Side Google Gemini LLM Generator.
    Uses GEMINI_API_KEY exclusively from environment variables on the server.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model_name or os.getenv("GEMINI_MODEL", os.getenv("GEMINI_MODEL_NAME", "gemini-3.6-flash"))

    def generate_answer(self, query: str, chunks: List[CandidateChunk]) -> str:
        """
        Generates an answer grounded strictly in retrieved context using Google Gemini API.
        Returns a clear user-facing error if API key is missing, quota is exceeded, or generation fails.
        """
        if not chunks:
            return "No relevant information found in the vault."

        if not self.api_key or self.api_key == "AIzaSy_your_gemini_api_key_here":
            return "⚠️ **Gemini API Error**: `GEMINI_API_KEY` is not configured on the server. Please set `GEMINI_API_KEY` in your environment variables or `.env` file."

        system_prompt = PromptBuilder.SYSTEM_PROMPT
        user_prompt = PromptBuilder.build_user_prompt(query, chunks)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        try:
            try:
                import google.genai as genai
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt
                )
            except (ImportError, AttributeError):
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(full_prompt)
            
            if response.text and response.text.strip():
                return response.text.strip()
            else:
                return "⚠️ **Gemini API Error**: Received empty response from model."

        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                return "⚠️ **Gemini Rate Limit Exceeded**: API quota limit reached. Please wait a moment before asking another question."
            elif "403" in err_msg or "API_KEY_INVALID" in err_msg:
                return "⚠️ **Gemini API Key Error**: Invalid API key configured on server."
            else:
                return f"⚠️ **Gemini API Error**: {err_msg}"


# Alias for backward compatibility
LLMGenerator = GeminiLLMGenerator
