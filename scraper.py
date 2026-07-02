import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import warnings
from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

BASLANGIC_URL = "https://compe.hku.edu.tr/"
ALAN = "compe.hku.edu.tr"
KAYIT_KLASORU = "veri"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


def sayfayi_getir(url):
    """Bir URL'in HTML'ini indirip BeautifulSoup nesnesi döndürür."""
    yanit = requests.get(url, headers=HEADERS, timeout=10)
    yanit.encoding = "utf-8"
    return BeautifulSoup(yanit.text, "html.parser")


def metni_temizle(soup):
    """Çöp blokları siler, temiz metni döndürür."""
    for etiket in soup(["nav", "header", "footer", "script", "style", "form"]):
        etiket.decompose()

    metin = soup.get_text(separator="\n", strip=True)
    satirlar = [s for s in metin.split("\n") if s.strip()]

    # Her sayfada tekrar eden menü/araç satırlarını at
    cop_satirlar = {
        "ANASAYFA", "HKÜ KALİTE", "PORTAL", "EBYS", "BİLGİ PAKETİ",
        "ÖĞRENCİ E-MAİL", "PERSONEL E-MAİL", "OBS", "KÜTÜPHANE", "EN",
        "BİLGİSAYAR", "MÜHENDİSLİĞİ",
    }
    temiz = [s for s in satirlar if s.strip() not in cop_satirlar]

    # "Erişilebilirlik Aracı" bloğundan sonrasını tamamen kes
    sonuc = []
    for s in temiz:
        if "Erişilebilirlik Aracı" in s:
            break  # bu satıra gelince dur, gerisini alma
        sonuc.append(s)

    return "\n".join(sonuc)


def ic_linkleri_bul(soup, ana_url):
    """Sayfadaki aynı-alan linklerini toplar (tekrarsız)."""
    linkler = set()
    for a in soup.find_all("a", href=True):
        tam_url = urljoin(ana_url, a["href"])
        tam_url = tam_url.split("#")[0]
        if urlparse(tam_url).netloc == ALAN:
            linkler.add(tam_url)
    return linkler


def dosya_adi_yap(url):
    """URL'den güvenli bir dosya adı üretir."""
    yol = urlparse(url).path.strip("/")
    if not yol:
        yol = "anasayfa"
    return yol.replace("/", "_") + ".txt"


def main():
    os.makedirs(KAYIT_KLASORU, exist_ok=True)

    ana_soup = sayfayi_getir(BASLANGIC_URL)
    gezilecek = ic_linkleri_bul(ana_soup, BASLANGIC_URL)
    gezilecek.add(BASLANGIC_URL)

    print(f"{len(gezilecek)} sayfa bulundu, çekiliyor...\n")

    for i, url in enumerate(sorted(gezilecek), start=1):
        try:
            soup = sayfayi_getir(url)
            metin = metni_temizle(soup)
            dosya = os.path.join(KAYIT_KLASORU, dosya_adi_yap(url))
            with open(dosya, "w", encoding="utf-8") as f:
                f.write(metin)
            print(f"[{i}/{len(gezilecek)}] kaydedildi: {dosya_adi_yap(url)} ({len(metin)} karakter)")
        except Exception as e:
            print(f"[{i}] HATA: {url} -> {e}")


if __name__ == "__main__":
    main()