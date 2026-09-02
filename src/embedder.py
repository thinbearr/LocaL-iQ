import os
from typing import List


class LocalEmbedder:
    """
    Local CPU embedding generator using SentenceTransformers (all-MiniLM-L6-v2).
    Lazy-imports PyTorch and SentenceTransformer to avoid memory allocations at startup.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        self._model = None

    @property
    def model(self):
        """Lazy loads SentenceTransformer model instance and PyTorch on demand."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    def encode_query(self, query: str) -> List[float]:
        embedding = self.model.encode(query, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()


class GeminiEmbedder:
    """
    Lightweight cloud embedding generator using Google Gemini gemini-embedding-2 API.
    Zero PyTorch footprint, zero local RAM usage (~0MB local model memory).
    Used in cloud deployment environments (e.g. Render 512MB RAM tier).
    """

    def __init__(self, model_name: str = "gemini-embedding-2"):
        self.model_name = os.getenv("GEMINI_EMBED_MODEL", model_name)
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY")
            self._client = genai.Client(api_key=api_key)
        return self._client

    def encode_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = []
        # Batch requests
        for text in texts:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=text,
            )
            if hasattr(response, "embedding") and hasattr(response.embedding, "values"):
                embeddings.append(response.embedding.values)
            elif hasattr(response, "embeddings") and len(response.embeddings) > 0:
                embeddings.append(response.embeddings[0].values)
            else:
                # Fallback if structure varies
                embeddings.append(response.values if hasattr(response, "values") else [])
        return embeddings

    def encode_query(self, query: str) -> List[float]:
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=query,
        )
        if hasattr(response, "embedding") and hasattr(response.embedding, "values"):
            return response.embedding.values
        elif hasattr(response, "embeddings") and len(response.embeddings) > 0:
            return response.embeddings[0].values
        return response.values if hasattr(response, "values") else []


def get_embedder():
    """
    Factory function to select embedding provider:
    - EMBEDDING_PROVIDER=gemini or USE_GEMINI_EMBEDDINGS=true -> GeminiEmbedder (Cloud/Render low-RAM mode)
    - EMBEDDING_PROVIDER=local (default for local desktop execution) -> LocalEmbedder
    """
    provider = os.getenv("EMBEDDING_PROVIDER", "").lower()
    use_gemini = os.getenv("USE_GEMINI_EMBEDDINGS", "false").lower() in ("true", "1", "yes")
    
    # Auto-select Gemini Embedder in cloud/deployment if configured or explicit
    if provider == "gemini" or use_gemini:
        return GeminiEmbedder()
    return LocalEmbedder()
