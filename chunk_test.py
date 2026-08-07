from langchain_text_splitters import RecursiveCharacterTextSplitter


with open("veri/ders-icerikleri.txt", "r", encoding="utf-8") as f:
    metin = f.read()
print(f"Orijinal metin: {len(metin)} karakter\n")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# 3. Metni parçala
parcalar = splitter.split_text(metin)

print(f"Toplam {len(parcalar)} parçaya bölündü\n")

for i, parca in enumerate(parcalar[:2], start=1):
    print(f"--- PARÇA {i} ({len(parca)} karakter) ---")
    print(parca)
    print()