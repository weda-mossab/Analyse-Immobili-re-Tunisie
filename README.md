# 🏠 Analyse Immobilière Tunisie (mubaweb.tn)

Un tableau de bord interactif pour analyser le marché immobilier tunisien à partir de données collectées sur Mubawab.

## 📋 Description du projet

Ce projet est une solution complète pour l'analyse des annonces immobilières en Tunisie, composée de trois parties principales:

1. **Scraper** - Un script Python utilisant Selenium pour extraire les données des annonces immobilières (vente et location) depuis le site Mubawab.
2. **API** - Une API Flask permettant d'accéder aux données collectées.
3. **Dashboard** - Un tableau de bord interactif construit avec Dash et Plotly pour visualiser et analyser les données du marché immobilier.

## 🚀 Fonctionnalités

- Extraction automatique des annonces immobilières
- Stockage des données au format Excel et dans une base de données SQLite
- API RESTful pour accéder aux données
- Tableau de bord interactif avec:
  - Filtres dynamiques (par type de bien, ville, gamme de prix, etc.)
  - Visualisations diverses (répartition des types de biens, prix moyens, etc.)
  - Analyses comparatives (prix au m², distribution des prix)
  - Top des annonces les plus chères

## 🔧 Installation

### Prérequis

- Python 3.8+
- Chrome (pour le web scraping avec Selenium)

### Étapes d'installation

1. Clonez ce dépôt:
```bash
git clone https://github.com/votre-username/analyse-immobiliere-tunisie.git
cd analyse-immobiliere-tunisie
```

2. Créez un environnement virtuel:
```bash
python -m venv venv
```

3. Activez l'environnement virtuel:
   - Windows:
   ```bash
   venv\Scripts\activate
   ```
   - macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. Installez les dépendances:
```bash
pip install -r requirements.txt
```

5. Téléchargez ChromeDriver (si vous souhaitez exécuter le scraper):
   - Le script utilise webdriver_manager qui devrait télécharger automatiquement la version appropriée de ChromeDriver.

## 💻 Utilisation

### Scraping des données

Pour collecter de nouvelles données depuis Mubawab:

```bash
python scrapping.py
```

Cela générera un fichier Excel `Mubawab_Annonces.xlsx` avec les données extraites.

### Lancement de l'API

Pour démarrer l'API Flask:

```bash
python app.py
```

L'API sera accessible à l'adresse `http://localhost:8000`.

Endpoints disponibles:
- `GET /` - Page d'accueil de l'API
- `GET /annonces` - Récupérer toutes les annonces depuis la base de données
- `GET /annonces_csv` - Récupérer toutes les annonces depuis le fichier Excel
- `POST /scrape` - Lancer une nouvelle session de scraping en arrière-plan

### Lancement du tableau de bord

Pour démarrer le tableau de bord Dash:

```bash
python dashboard.py
```

Le tableau de bord sera accessible à l'adresse `http://localhost:8050`.

## 📊 Structure des données

Les données collectées incluent:
- Nature (vente/location)
- Titre de l'annonce
- Prix
- Localisation
- Superficie
- Nombre de pièces
- Nombre de chambres
- Nombre de salles de bain
- Lien vers l'annonce

## 📁 Structure du projet

```
/
├── dashboard.py         # Application Dash pour le tableau de bord
├── scrapping.py         # Script de scraping Selenium
├── app.py               # API Flask
├── requirements.txt     # Dépendances Python
├── annonces.db          # Base de données SQLite
└── Mubawab_Annonces_Location_Vente.xlsx  # Données extraites
```

## 🛠️ Technologies utilisées

- **Web Scraping**: Selenium, BeautifulSoup
- **Backend**: Flask, SQLite
- **Visualisation**: Dash, Plotly
- **Analyse de données**: Pandas, NumPy

## 📝 À faire

- Ajouter une authentification à l'API
- Implémenter une fonctionnalité d'alerte pour les nouvelles annonces
- Améliorer les analyses prédictives pour les prix immobiliers
- Ajouter la géolocalisation des biens sur une carte

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d'informations.

## ⚠️ Avertissement

Ce projet est créé à des fins éducatives et d'analyse. Respectez les conditions d'utilisation des sites web que vous scrapez et les réglementations concernant les données personnelles.
