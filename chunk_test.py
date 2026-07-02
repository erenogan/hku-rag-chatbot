from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Bir test dosyasını oku (kendi dosya adınla değiştir)
with open("veri/ders-icerikleri.txt", "r", encoding="utf-8") as f:
    metin = f.read()

print(f"Orijinal metin: {len(metin)} karakter\n")

# 2. Parçalayıcıyı ayarla
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # her parça ~1000 karakter
    chunk_overlap=150,    # parçalar 150 karakter üst üste binsin
    separators=["\n\n", "\n", ". ", " ", ""]  # önce paragraf, sonra satır, sonra cümle...
)

# 3. Metni parçala
parcalar = splitter.split_text(metin)

print(f"Toplam {len(parcalar)} parçaya bölündü\n")

# 4. İlk 2 parçayı göster (kontrol için)
for i, parca in enumerate(parcalar[:2], start=1):
    print(f"--- PARÇA {i} ({len(parca)} karakter) ---")
    print(parca)
    print()