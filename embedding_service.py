from sentence_transformers import SentenceTransformer
from typing import List
from config import config

class EmbeddingService:
    def __init__(self):
        print(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Dimension: {self.dimension}")

    def embed_text(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        return self.dimension
