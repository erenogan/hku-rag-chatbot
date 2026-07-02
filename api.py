from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import cevap_uret

app = FastAPI(title="HKÜ Asistanı API")

# Tarayıcıdan gelen isteklere izin ver (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SoruModeli(BaseModel):
    soru: str


@app.get("/")
def ana_sayfa():
    return {"mesaj": "HKÜ Asistanı API çalışıyor!"}


@app.post("/sor")
def soru_sor(istek: SoruModeli):
    sonuc = cevap_uret(istek.soru)
    return {
        "soru": istek.soru,
        "cevap": sonuc["cevap"],
        "kaynaklar": sonuc["kaynaklar"]
    }