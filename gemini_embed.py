import os
from dotenv import load_dotenv
from google import genai
from chromadb import Documents, EmbeddingFunction, Embeddings

load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiEmbedding(EmbeddingFunction):
    """ChromaDB için Gemini tabanlı embedding fonksiyonu."""

    def __call__(self, input: Documents) -> Embeddings:
        sonuc = _client.models.embed_content(
            model="gemini-embedding-001",
            contents=list(input)
        )
        return [e.values for e in sonuc.embeddings]