import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions

VERI_KLASORU = "veri"
DB_KLASORU = "chroma_db"          # veritabanı buraya kaydedilecek
KOLEKSIYON_ADI = "hku_ceng"

# --- 1. Parçalayıcıyı hazırla (chunk_test.py'deki ile aynı ayarlar) ---
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# --- 2. Sadece beyaz listedeki dosyaları oku ve parçala ---
parcalar = []
kaynaklar = []

# Sadece bu dosyalar embed'lenecek (gerçek, değerli içerik)
ALINACAK_DOSYALAR = [
    "ders-icerikleri.txt",
    "akademik-personel.txt",
    "bolum-baskaninin-mesaji.txt",
    "hakkimizda.txt",
    "idari-personel.txt",
    "lisans-egitim-programi.txt",
    "staj-co-op.txt",
    "tanitim.txt",
    "mudek.txt",
    "iletisim.txt",
    "yonetim.txt",
    "formlar-ve-dilekceler.txt",
]

for dosya_adi in ALINACAK_DOSYALAR:
    yol = os.path.join(VERI_KLASORU, dosya_adi)

    # Dosya gerçekten var mı kontrol et (isim yanlışsa çökmesin)
    if not os.path.exists(yol):
        print(f"UYARI: bulunamadı, atlanıyor -> {dosya_adi}")
        continue

    with open(yol, "r", encoding="utf-8") as f:
        metin = f.read()

    if len(metin.strip()) < 50:
        continue

    # Akademik personel listesini parçalama - bütün kalsın
    if dosya_adi == "akademik-personel.txt":
            dosya_parcalari = [metin]  # tek parça olarak al
    else:
            dosya_parcalari = splitter.split_text(metin)
    for parca in dosya_parcalari:
        if len(parca.strip()) < 100:   # çok kısa parçaları atla
            continue
        parcalar.append("passage: " + parca)
        kaynaklar.append(dosya_adi)
    print(f"İşlendi: {dosya_adi} ({len(dosya_parcalari)} parça)")

print(f"\nToplam {len(parcalar)} parça hazırlandı.\n")

# --- 3. Embedding modelini tanımla (güçlü, çok dilli E5 modeli) ---
embed_fonksiyonu = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="intfloat/multilingual-e5-large"
)
# --- 4. ChromaDB'yi başlat (diske kaydeden kalıcı tip) ---
client = chromadb.PersistentClient(path=DB_KLASORU)

# Eskiden kalma varsa sil, temiz başla
try:
    client.delete_collection(KOLEKSIYON_ADI)
except Exception:
    pass

koleksiyon = client.create_collection(
    name=KOLEKSIYON_ADI,
    embedding_function=embed_fonksiyonu
)

# --- 5. Parçaları ID'lerle birlikte veritabanına ekle ---
idler = [f"parca_{i}" for i in range(len(parcalar))]
metadatalar = [{"kaynak": k} for k in kaynaklar]

print("Embedding yapılıyor ve kaydediliyor...")
koleksiyon.add(
    documents=parcalar,
    ids=idler,
    metadatas=metadatalar
)
print(f"Bitti! {koleksiyon.count()} parça veritabanında.\n")

soru = "query: yapay zeka"
sonuc = koleksiyon.query(query_texts=[soru], n_results=5)

print(f"SORU: {soru}\n")
for i, belge in enumerate(sonuc["documents"][0], start=1):
    kaynak = sonuc["metadatas"][0][i-1]["kaynak"]
    mesafe = sonuc["distances"][0][i-1]
    print(f"--- PARÇA {i} (kaynak: {kaynak}, mesafe: {mesafe:.3f}) ---")
    print(belge[:200])
    print()