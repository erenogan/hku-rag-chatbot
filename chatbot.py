import chromadb
from chromadb.utils import embedding_functions
import ollama

DB_KLASORU = "chroma_db"
KOLEKSIYON_ADI = "hku_ceng"
ANA_ADRES = "https://compe.hku.edu.tr/"

# --- Veritabanına bağlan ---
embed_fonksiyonu = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="intfloat/multilingual-e5-large"
)
client = chromadb.PersistentClient(path=DB_KLASORU)
koleksiyon = client.get_collection(
    name=KOLEKSIYON_ADI,
    embedding_function=embed_fonksiyonu
)


def cevap_uret(soru):
    # --- İlgili parçaları bul ---
    sonuc = koleksiyon.query(
        query_texts=["query: " + soru],
        n_results=5
    )
    parcalar = sonuc["documents"][0]
    mesafeler = sonuc["distances"][0]

    metadatalar = sonuc["metadatas"][0]

    # --- Mesafe eşiği: en yakın parça bile uzaksa cevap verme ---
    if not parcalar or mesafeler[0] > 0.45:
        return {
            "cevap": "Bu konuda elimde bilgi yok. Sadece Bilgisayar Mühendisliği bölümüyle ilgili soruları yanıtlayabilirim.",
            "kaynaklar": []
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
    yanit = ollama.chat(
        model="qwen2.5:7b",
        messages=[{"role": "user", "content": prompt}]
    )

    # --- Kullanılan kaynakları URL'ye çevir (tekrarsız) ---
    kaynaklar = []
    for m in metadatalar:
        dosya = m["kaynak"].replace(".txt", "")
        url = ANA_ADRES + dosya + "/"
        kaynak = {"ad": dosya, "url": url}
        if kaynak not in kaynaklar:
            kaynaklar.append(kaynak)

    return {
        "cevap": yanit["message"]["content"],
        "kaynaklar": kaynaklar
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