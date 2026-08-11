import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
from groq import Groq
from langfuse import observe, get_client

load_dotenv()  # .env dosyasını oku
langfuse = get_client()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_KLASORU = "chroma_db"
KOLEKSIYON_ADI = "hku_ceng"
ANA_ADRES = "https://compe.hku.edu.tr/"

# --- Veritabanına bağlan ---
from gemini_embed import GeminiEmbedding
embed_fonksiyonu = GeminiEmbedding()

client = chromadb.PersistentClient(path=DB_KLASORU)
koleksiyon = client.get_collection(
    name=KOLEKSIYON_ADI,
    embedding_function=embed_fonksiyonu
)


@observe(name="soru-cevap")
def cevap_uret(soru):
    # --- İlgili parçaları bul ---
    sonuc = koleksiyon.query(
        query_texts=[soru],
        n_results=5
    )
    parcalar = sonuc["documents"][0]
    mesafeler = sonuc["distances"][0]
    print(f"[DEBUG] En yakın mesafe: {mesafeler[0]:.3f}")

    metadatalar = sonuc["metadatas"][0]

    # --- Mesafe eşiği: en yakın parça bile uzaksa cevap verme ---
    if not parcalar or mesafeler[0] > 0.65:
        langfuse.update_current_span(
            input={"soru": soru},
            output={
                "cevap": "bilgi yok",
                "en_yakin_mesafe": float(mesafeler[0]) if mesafeler else None
            }
        )
        return {
            "cevap": "Bu konuda elimde bilgi yok. Sadece Bilgisayar Mühendisliği bölümüyle ilgili soruları yanıtlayabilirim.",
            "kaynaklar": [],
            "baglam": []
        }

    # --- "passage: " öneklerini temizle (model bunları görmesin) ---
    temiz_parcalar = [p.replace("passage: ", "") for p in parcalar]
    baglam = "\n\n".join(temiz_parcalar)

    # --- LLM talimatı ---
    prompt = f"""Sen Hasan Kalyoncu Üniversitesi Bilgisayar Mühendisliği bölümünün asistanısın.

    KURALLAR:
    - SADECE aşağıdaki BİLGİLER'e dayanarak cevap ver.
    - Cevap bilgilerde yoksa uydurma, sadece şunu yaz: "Bu konuda elimde bilgi yok."
    - Cevabı tam bir cümleyle ver. Sadece sayı veya tek kelime yazma, kısa bir açıklama ekle.
      Örnek: Soru "kaç kredi?" ise, "145" değil, "Mezun olmak için toplam 145 kredi tamamlamanız gerekiyor." yaz.
    - "Güzel soru", "gördüğüm kadarıyla" gibi gereksiz girişler yapma.
    - "passage", "Ders Kodu ve Adı" gibi teknik etiketleri kullanma.
    - Yalnızca düzgün Türkçe yaz, başka dil kullanma.
    - Açık ve anlaşılır ol ama gereksiz uzatma. 1-3 cümle ideal.

    BİLGİLER:
    {baglam}

    SORU: {soru}

    CEVAP:"""

    # --- LLM'den cevap al ---
    yanit = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    # --- Kullanılan kaynakları URL'ye çevir (tekrarsız) ---
    kaynaklar = []
    for m in metadatalar:
        dosya = m["kaynak"].replace(".txt", "")
        url = ANA_ADRES + dosya + "/"
        kaynak = {"ad": dosya, "url": url}
        if kaynak not in kaynaklar:
            kaynaklar.append(kaynak)

    langfuse.update_current_span(
        input={"soru": soru},
        output={
            "cevap": yanit.choices[0].message.content,
            "kaynak_sayisi": len(kaynaklar),
            "en_yakin_mesafe": float(mesafeler[0])
        }
    )

    return {
        "cevap": yanit.choices[0].message.content,
        "kaynaklar": kaynaklar,
        "baglam": temiz_parcalar
    }


if __name__ == "__main__":
    print("HKÜ Asistanı hazır! (Çıkmak için 'q' yaz)\n")
    while True:
        soru = input("Soru: ")
        if soru.lower() in ["q", "quit", "çık"]:
            break
        sonuc = cevap_uret(soru)
        print(f"\nCevap: {sonuc['cevap']}")
        print(f"Kaynaklar: {[k['ad'] for k in sonuc['kaynaklar']]}\n")
        print("-" * 50)