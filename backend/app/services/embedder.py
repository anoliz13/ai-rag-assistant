from typing import Optional
from sentence_transformers import SentenceTransformer
from app.core.config import settings
import openai
import numpy as np


class EmbedderService:
    def __init__(self):
        self._local_model: Optional[SentenceTransformer] = None
        self._dimension: int = 384

    def _get_local_model(self) -> SentenceTransformer:
        if self._local_model is None:
            self._local_model = SentenceTransformer(settings.embedding_model)
            self._dimension = self._local_model.get_sentence_embedding_dimension()
        return self._local_model

    async def embed(self, text: str) -> list[float]:
        if settings.embedding_provider == "local":
            model = self._get_local_model()
            embedding = model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        else:
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.embeddings.create(model=settings.embedding_model, input=text)
            return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if settings.embedding_provider == "local":
            model = self._get_local_model()
            embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return embeddings.tolist()
        else:
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.embeddings.create(model=settings.embedding_model, input=texts)
            return [item.embedding for item in response.data]

    @property
    def dimension(self) -> int:
        if settings.embedding_provider == "local":
            return self._get_local_model().get_sentence_embedding_dimension()
        return 1536
