import os
from typing import List
from sentence_transformers import SentenceTransformer


class LocalEmbedder:
    """
    Wrapper around SentenceTransformers for local CPU embedding generation.
    Zero API cost, zero external dependency.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy loads SentenceTransformer model instance."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generates vector embeddings for a list of text passages.
        """
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    def encode_query(self, query: str) -> List[float]:
        """
        Generates vector embedding for a single search query.
        """
        embedding = self.model.encode(query, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()
