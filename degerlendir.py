import os
import json
from dotenv import load_dotenv
from chatbot import cevap_uret
from groq import Groq

load_dotenv()
hakem = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Veride cevabı olan gerçek test soruları
test_sorulari = [
    "Yapay zeka dersi var mı?",
    "Bölüm başkanı kim?",
    "Mezun olmak için kaç kredi gerekiyor?",
    "Staj zorunlu mu?",
    "Hangi hocalar var?",
]

def hakem_puanla(soru, cevap, baglam):
    """Bir LLM'i hakem yapıp cevabı 1-5 arası puanlatır."""
    prompt = f"""Sen bir değerlendirme hakemisin. Aşağıdaki cevabı iki açıdan 1-5 arası puanla:
- sadakat: Cevap SADECE verilen BİLGİ'ye mi dayanıyor? (5=tamamen, 1=uydurma var)
- alaka: Cevap soruyla ne kadar alakalı? (5=tam, 1=alakasız)

BİLGİ:
{baglam}

SORU: {soru}
CEVAP: {cevap}

Sadece şu JSON formatında yanıt ver, başka hiçbir şey yazma:
{{"sadakat": <1-5>, "alaka": <1-5>, "aciklama": "<kısa>"}}"""

    yanit = hakem.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    ham = yanit.choices[0].message.content.strip()
    # JSON'u ayıkla
    ham = ham.replace("```json", "").replace("```", "").strip()
    return json.loads(ham)

# Değerlendirmeyi çalıştır
toplam_sadakat = 0
toplam_alaka = 0
print("=" * 60)
for soru in test_sorulari:
    sonuc = cevap_uret(soru)
    cevap = sonuc["cevap"]
    baglam = "\n".join(sonuc.get("baglam", [""]))
    puan = hakem_puanla(soru, cevap, baglam)

    toplam_sadakat += puan["sadakat"]
    toplam_alaka += puan["alaka"]

    print(f"SORU: {soru}")
    print(f"CEVAP: {cevap[:100]}...")
    print(f"  Sadakat: {puan['sadakat']}/5 | Alaka: {puan['alaka']}/5")
    print(f"  Not: {puan['aciklama']}")
    print("-" * 60)

n = len(test_sorulari)
print(f"\nORTALAMA SADAKAT: {toplam_sadakat/n:.2f}/5")
print(f"ORTALAMA ALAKA:   {toplam_alaka/n:.2f}/5")
print("=" * 60)