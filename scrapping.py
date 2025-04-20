from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pandas as pd
from bs4 import BeautifulSoup

# Configuration de Selenium
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(10)

# Définir les types de biens à scraper
nature = {
    "location": "immobilier-a-louer",
    "vente": "immobilier-a-vendre"
}

annonces_list = []

for nature_label, url_part in nature.items():
    print(f"\n📥 SCRAPING pour : {nature_label.upper()}")

    base_url = f"https://www.mubawab.tn/fr/ct/tunis/{url_part}:p:{{}}"

    # Charger la première page
    driver.get(base_url.format(1))
    time.sleep(5)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Nombre total de pages
    try:
        total_pages = int(soup.select_one("#lastPageSpan").text.strip())
        print(f"➡️  Nombre total de pages : {total_pages}")
    except:
        total_pages = 1

    # Boucle sur toutes les pages
    for page in range(1, total_pages + 1):
        print(f"🔄 Page {page}/{total_pages}...")
        driver.get(base_url.format(page))
        time.sleep(5)

        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        annonces = soup.select("div.listingBox.feat, div.listingBox")

        for annonce in annonces:
            titre = annonce.select_one("h2.listingTit a")
            prix = annonce.select_one("span.priceTag")
            localisation = annonce.select_one("span.listingH3")
            details = annonce.select("div.adDetailFeature span")
            superficie = details[0] if len(details) > 0 else None
            nb_pieces = details[1] if len(details) > 1 else None
            nb_chambres = details[2] if len(details) > 2 else None
            nb_sdb = details[3] if len(details) > 3 else None
            lien = titre["href"] if titre else None

            if titre and prix:
                annonce_data = {
                    "nature": nature_label,
                    "Titre": titre.text.strip(),
                    "Prix": prix.text.strip(),
                    "Localisation": localisation.text.strip() if localisation else "N/A",
                    "Superficie": superficie.text.strip() if superficie else "N/A",
                    "Pièces": nb_pieces.text.strip() if nb_pieces else "N/A",
                    "Chambres": nb_chambres.text.strip() if nb_chambres else "N/A",
                    "Salles de bain": nb_sdb.text.strip() if nb_sdb else "N/A",
                    "Lien": f"https://www.mubawab.tn{lien}" if lien else "N/A",
                }
                annonces_list.append(annonce_data)

driver.quit()

# Export vers Excel
df = pd.DataFrame(annonces_list)
df.to_excel("Mubawab_Annonces_Location_Vente.xlsx", index=False)

print("Scraping terminé ✅ .")