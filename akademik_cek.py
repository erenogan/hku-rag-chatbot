import requests
from bs4 import BeautifulSoup

URL = "https://compe.hku.edu.tr/akademik-personel/"
CIKTI = "veri/akademik-personel.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

# Sayfayı indir
yanit = requests.get(URL, headers=HEADERS, timeout=10)
yanit.encoding = "utf-8"
soup = BeautifulSoup(yanit.text, "html.parser")

# Her hoca bir <h4> başlığı içinde (isim), altında görev + e-posta var
hocalar = []

# İsimleri <h4> etiketlerinden bul
for baslik in soup.find_all("h4"):
    isim = baslik.get_text(strip=True)
    if not isim:
        continue

    # İsimden sonraki metinde görev ve e-posta aranır
    # Bir sonraki tabloyu/metni bul
    sonraki = baslik.find_next("table")
    detay = ""
    if sonraki:
        detay = sonraki.get_text(separator=" ", strip=True)

    # Sadece gerçek hoca kayıtlarını al (@ işareti olanlar = e-posta var)
    if "@" in detay:
        hocalar.append(f"Akademik Personel: {isim}\nBilgiler: {detay}\n")

# Dosyaya yaz
with open(CIKTI, "w", encoding="utf-8") as f:
    f.write("HKÜ Bilgisayar Mühendisliği Akademik Personel Listesi\n")
    f.write("Bu sayfada bölümdeki tüm hocalar, öğretim üyeleri, profesörler, "
            "doktor öğretim üyeleri, araştırma görevlileri ve akademik kadro yer alır. "
            "Hangi hocalar var, kimler ders veriyor, öğretim üyesi listesi.\n\n")
    f.write("\n".join(hocalar))

print(f"{len(hocalar)} akademisyen kaydedildi -> {CIKTI}")
for h in hocalar:
    print(h)