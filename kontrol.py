import chromadb
from chromadb.utils import embedding_functions

embed_fonksiyonu = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="intfloat/multilingual-e5-large"
)
client = chromadb.PersistentClient(path="chroma_db")
koleksiyon = client.get_collection(name="hku_ceng", embedding_function=embed_fonksiyonu)

# Toplam parça sayısı
print(f"Toplam parça: {koleksiyon.count()}")

# Kaynağı akademik-personel olan parçaları ara
sonuc = koleksiyon.get(where={"kaynak": "akademik-personel.txt"})
print(f"Akademik personel parça sayısı: {len(sonuc['ids'])}")

if sonuc['ids']:
    print("\nİÇERİK:")
    print(sonuc['documents'][0][:500])
else:
    print("\n⚠️ Akademik personel dosyası veritabanında YOK!")