import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7"}

def conversion(text):
    return (text or "").replace("zł do negocjacji","").replace("zł","").replace("\xa0","").replace(" ","").replace(",",".").replace("$","").strip()

def parsowanie(lista, platforma):

    products = []
    
    for html in lista:
        
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        
        if platforma == 0:
            for card in soup.select('div[data-cy="ad-card-title"]'):
                a = card.select_one("a.css-1tqlkj0")
                c = card.select_one('p[data-testid="ad-price"]')
                if a and c:
                    products.append([conversion(c.get_text(" ", strip=True)), "https://www.olx.pl" + a.get("href","")])
        
        elif platforma == 1:
            for card in soup.select("div.new-item-box__container"):
                a = card.select_one("a.new-item-box__overlay")
                c = card.select_one('p[data-testid$="--price-text"]')
                if a and c:
                    products.append([conversion(c.get_text(" ", strip=True)), a.get("href","")])
        
        else:
            for card in soup.select("div.su-card-container"):
                a = card.select_one("a.s-card__link")
                c = card.select_one("span.s-card__price")
                if a and c:
                    products.append([conversion(c.get_text(" ", strip=True)), a.get("href","")])
    
    return products

async def fetch(session, url, sem):
    async with sem:
        try:
            async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=20)) as r:
                return await r.text()
        except Exception:
            return ""

async def main():
    fraza = input("Nazwa produktu [np. spodnie]: ").strip()
    if not fraza:
        raise ValueError("Błąd: nie podano nazwy produktu.")

    cena_min = input("Minimalna cena w PLN [np. 10]: ").strip()
    if not cena_min:
        raise ValueError("Błąd: nie podano minimalnej ceny.")
    try:
        cena_min = int(cena_min)
        if cena_min < 1:
            raise ValueError
    except ValueError:
        raise ValueError("Błąd: minimalna cena musi być liczbą całkowitą >= 1.")

    liczba_stron = input("Liczba stron do skrapowania [np. 3]: ").strip()
    if not liczba_stron:
        raise ValueError("Błąd: nie podano liczby stron.")
    try:
        liczba_stron = int(liczba_stron)
        if liczba_stron < 1:
            raise ValueError
    except ValueError:
        raise ValueError("Błąd: liczba stron musi być liczbą całkowitą >= 1.")

    limit_pobran = input("Limit jednoczesnych pobrań (concurrency) [np. 4]: ").strip()
    if not limit_pobran:
        raise ValueError("Błąd: nie podano limitu jednoczesnych pobrań.")
    try:
        limit_pobran = int(limit_pobran)
        if limit_pobran < 1:
            raise ValueError
    except ValueError:
        raise ValueError("Błąd: limit jednoczesnych pobrań musi być liczbą całkowitą >= 1.")

    platformy = input("Platformy (olx,vinted,ebay) [np. olx,vinted]: ").strip().lower()
    if not platformy:
        raise ValueError("Błąd: nie podano platform.")

    dozwolone = ["olx", "vinted", "ebay"]
    wybrane_platformy = [p.strip() for p in platformy.split(",") if p.strip() in dozwolone]
    if not wybrane_platformy:
        raise ValueError("Błąd: nie wybrano poprawnych platform (olx, vinted, ebay).")

    fraza_olx = fraza.replace(" ", "-")
    fraza_vinted = fraza.replace(" ", "%20")
    fraza_ebay = fraza.replace(" ", "+")

    url_olx = f"https://www.olx.pl/oferty/q-{fraza_olx}/?page={{page}}&search%5Bfilter_float_price%3Afrom%5D={cena_min}"
    url_vinted = f"https://www.vinted.pl/catalog?search_text={fraza_vinted}&price_from={cena_min}&currency=PLN&page={{page}}"
    url_ebay = f"https://www.ebay.pl/sch/i.html?_nkw={fraza_ebay}&_sacat=9355&_from=R40&rt=nc&_udlo={cena_min}&_pgn={{page}}"

    szablony = {"olx": url_olx, "vinted": url_vinted, "ebay": url_ebay}

    adresy = []
    for strona in range(1, liczba_stron + 1):
        for plat in wybrane_platformy:
            adresy.append(szablony[plat].format(page=strona))

    semafor = asyncio.Semaphore(limit_pobran)
    async with aiohttp.ClientSession() as session:
        strony_html = await asyncio.gather(*(fetch(session, u, semafor) for u in adresy))

    liczba_platform = len(wybrane_platformy)
    wiersze = []
    mapa_platform = {"olx": 0, "vinted": 1, "ebay": 2}

    for i, nazwa in enumerate(wybrane_platformy):
        oferty = parsowanie(strony_html[i::liczba_platform], mapa_platform[nazwa])
        for cena, link in oferty:
            wiersze.append({"platforma": nazwa, "price": cena, "url": link})

    df = pd.DataFrame(wiersze)
    if not df.empty:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df.dropna(subset=["price", "url"])

    for nazwa in wybrane_platformy:
        print(f"{nazwa.upper()}: {(df['platforma'] == nazwa).sum() if not df.empty else 0}")

    if not df.empty:
        najtansze = df.loc[df.groupby("platforma")["price"].idxmin()].sort_values("price")
        print("\nNajtańsze oferty (platforma, cena, url):")
        for p, c, u in najtansze[["platforma", "price", "url"]].values:
            print(f"{p}, {c}, {u}")
        df.to_csv("wynik_csv.csv", sep=";", index=False)
        print("\nZapisano: wynik_csv.csv")
    else:
        print("\nBrak wyników (możliwa blokada lub zmiana HTML).")

asyncio.run(main())
