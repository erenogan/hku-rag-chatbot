import os
import requests
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/intfloat/multilingual-e5-large"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def embed_al(metinler):
    yanit = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": metinler, "options": {"wait_for_model": True}}
    )
    return yanit.json()

# Test
sonuc = embed_al(["query: yapay zeka dersi"])
print("Tip:", type(sonuc))
print("İlk 5 sayı:", sonuc[0][:5] if isinstance(sonuc, list) else sonuc)