import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

sonuc = client.models.embed_content(
    model="gemini-embedding-001",
    contents="yapay zeka dersi"
)

vektor = sonuc.embeddings[0].values
print("Vektör uzunluğu:", len(vektor))
print("İlk 5 sayı:", vektor[:5])