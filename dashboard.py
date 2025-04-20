import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback, callback_context
import re
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import numpy as np
from datetime import datetime

# Load Bootstrap template for plots
load_figure_template("bootstrap")

# Initialize the app with a modern Bootstrap theme
app = Dash(__name__, external_stylesheets=[
    dbc.themes.COSMO,  # More modern theme
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"  # Font Awesome icons
])

app.title = "Immobilier Tunisie Dashboard"

# Custom CSS for animations and more professional look
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Animations and modern styling */
            .fade-in {
                animation: fadeIn 0.8s ease-in;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .hover-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            
            .metric-card {
                transition: all 0.3s ease;
                border-radius: 10px;
                border: none;
                box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            }
            
            .navbar-brand {
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            
            .dash-graph {
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                padding: 15px;
                background-color: white;
                transition: all 0.3s ease;
            }
            
            .dash-graph:hover {
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            }
            
            .count-up {
                display: inline-block;
                animation: countUp 2s ease-out forwards;
            }
            
            @keyframes countUp {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .card-header {
                background: linear-gradient(120deg, #5B86E5, #36D1DC);
                color: white;
                border-radius: 10px 10px 0 0 !important;
                font-weight: 600;
            }
            
            .filter-card .card-header {
                background: linear-gradient(120deg, #FF8008, #FFC837);
            }
            
            .footer {
                background: linear-gradient(to right, #141E30, #243B55);
                color: white !important;
            }
            
            .footer p {
                color: rgba(255,255,255,0.8) !important;
            }
            
            /* Pulsing animation for key metrics */
            .pulse {
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            /* Tooltip styling */
            .tooltip-inner {
                background-color: #2C3E50;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                max-width: 300px;
            }
            
            /* Logo styling */
            .logo-img {
                height: 40px;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
            <script>
                // Add some basic animations
                document.addEventListener("DOMContentLoaded", function() {
                    // Animate metrics
                    const metrics = document.querySelectorAll('.metric-value');
                    metrics.forEach((metric, index) => {
                        setTimeout(() => {
                            metric.classList.add('count-up');
                        }, index * 200);
                    });
                    
                    // Initialize Bootstrap tooltips
                    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
                    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                        return new bootstrap.Tooltip(tooltipTriggerEl)
                    });
                });
            </script>
        </footer>
    </body>
</html>
'''

# Charger les données
def load_data():
    try:
        df = pd.read_excel("Mubawab_Annonces.xlsx")
        print("✅ Données chargées :")
        print(df.head())
        print("Shape initiale :", df.shape)

        # Nettoyage : enlever les valeurs manquantes
        df.dropna(subset=["Titre", "Prix", "Localisation"], inplace=True)
        print("Après suppression des NaN :", df.shape)

        # Nettoyage de la colonne 'Prix'
        def nettoyer_prix(prix_str):
            try:
                if isinstance(prix_str, str):
                    prix_str = prix_str.replace(" ", "").replace(".", "").replace(",", "")
                    match = re.search(r"\d+", prix_str)
                    if match:
                        return int(match.group())
                elif isinstance(prix_str, (int, float)):
                    return int(prix_str)
            except:
                return None
            return None

        df["Prix_nettoye"] = df["Prix"].apply(nettoyer_prix)
        df.dropna(subset=["Prix_nettoye"], inplace=True)
        print("Après nettoyage du prix :", df.shape)

        # Nettoyage de la colonne 'Localisation'
        df["Ville"] = df["Localisation"].apply(
            lambda x: str(x).split(",")[-1].strip() if isinstance(x, str) else "Inconnu"
        )

        # Création de la colonne 'type_bien' depuis le titre
        def extraire_type_bien(titre):
            titre = titre.lower()
            if "appart" in titre:
                return "Appartement"
            elif "villa" in titre:
                return "Villa"
            elif "terrain" in titre:
                return "Terrain"
            elif "maison" in titre:
                return "Maison"
            else:
                return "Autre"

        df["type_bien"] = df["Titre"].apply(extraire_type_bien)
        
        # NOUVELLE FONCTIONNALITÉ: Détection de la nature (vente/location)
        def determiner_nature(titre, prix):
            titre_lower = str(titre).lower()
            prix_str = str(prix).lower()
            if "louer" in titre_lower or "locat" in titre_lower or "/mois" in prix_str or "par mois" in prix_str:
                return "Location"
            else:
                return "Vente"
                
        df["nature"] = df.apply(lambda row: determiner_nature(row["Titre"], row["Prix"]), axis=1)
        
        # Nettoyage de la colonne 'Superficie'
        def nettoyer_superficie(sup_str):
            try:
                if isinstance(sup_str, str):
                    match = re.search(r"\d+", sup_str)
                    if match:
                        return int(match.group())
                elif isinstance(sup_str, (int, float)):
                    return int(sup_str)
            except:
                return None
            return None
            
        df["Superficie_nettoye"] = df["Superficie"].apply(nettoyer_superficie)
        
        # Calculer prix au m²
        df["prix_m2"] = df.apply(
            lambda row: row["Prix_nettoye"] / row["Superficie_nettoye"] 
            if pd.notnull(row["Superficie_nettoye"]) and row["Superficie_nettoye"] > 0 
            else None, 
            axis=1
        )
        
        # Créer des catégories de prix
        df["categorie_prix"] = pd.cut(
            df["Prix_nettoye"], 
            bins=[0, 100000, 250000, 500000, 1000000, float('inf')],
            labels=["< 100K", "100K-250K", "250K-500K", "500K-1M", "> 1M"]
        )
        
        return df
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

df = load_data()

# Fonction pour créer les figures
def create_figures(dataframe):
    if dataframe.empty:
        return tuple([go.Figure() for _ in range(8)])
    
    # Couleurs cohérentes
    colors = {
        'Appartement': '#1f77b4',
        'Villa': '#ff7f0e',
        'Terrain': '#2ca02c',
        'Maison': '#d62728',
        'Autre': '#9467bd',
        'Vente': '#2E86C1',
        'Location': '#F39C12'
    }
    
    # Figure 1: Répartition des types de biens
    fig_type_bien = px.pie(
        dataframe, 
        names="type_bien",
        title="<b>Répartition des types de biens</b>",
        color="type_bien",
        color_discrete_map=colors,
        hole=0.4
    )
    fig_type_bien.update_traces(textinfo='percent+label', pull=[0.05, 0.05, 0.05, 0.05, 0.05], textfont_size=12)
    fig_type_bien.update_layout(
        legend_title="<b>Type de bien</b>",
        font=dict(size=12),
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=20, color="#2C3E50")
    )
    
    # Figure 2: Top villes
    top_villes = dataframe["Ville"].value_counts().head(10).reset_index()
    top_villes.columns = ["Ville", "Nombre d'annonces"]
    
    fig_top_villes = px.bar(
        top_villes, 
        x="Ville", 
        y="Nombre d'annonces",
        text="Nombre d'annonces",
        title="<b>Top 10 villes par nombre d'annonces</b>",
        color_discrete_sequence=['#5B86E5']
    )
    fig_top_villes.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig_top_villes.update_layout(
        xaxis_title="<b>Ville</b>",
        yaxis_title="<b>Nombre d'annonces</b>",
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=20, color="#2C3E50")
    )
    
    # Figure 3: Distribution des prix
    fig_distribution_prix = px.histogram(
        dataframe, 
        x="Prix_nettoye",
        nbins=30,
        title="<b>Distribution des prix</b>",
        color_discrete_sequence=['#5B86E5'],
        opacity=0.8
    )
    fig_distribution_prix.update_layout(
        xaxis_title="<b>Prix (TND)</b>",
        yaxis_title="<b>Nombre d'annonces</b>",
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=20, color="#2C3E50")
    )
    
    # Figure 4: Prix moyen par type de bien
    prix_moyen_type = dataframe.groupby('type_bien')['Prix_nettoye'].mean().reset_index()
    fig_prix_moyen = px.bar(
        prix_moyen_type,
        x='type_bien',
        y='Prix_nettoye',
        color='type_bien',
        color_discrete_map=colors,
        title="<b>Prix moyen par type de bien</b>",
        text_auto='.0f'
    )
    fig_prix_moyen.update_layout(
        xaxis_title="<b>Type de bien</b>",
        yaxis_title="<b>Prix moyen (TND)</b>",
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=20, color="#2C3E50")
    )
    
    # Figure 5: Scatter plot prix vs superficie
    if 'Superficie_nettoye' in dataframe.columns and not dataframe['Superficie_nettoye'].isna().all():
        fig_scatter = px.scatter(
            dataframe.dropna(subset=['Superficie_nettoye']),
            x='Superficie_nettoye',
            y='Prix_nettoye',
            color='type_bien',
            color_discrete_map=colors,
            title="<b>Relation entre superficie et prix</b>",
            opacity=0.7,
            size_max=15,
            hover_data=['Titre', 'Prix', 'Ville']
        )
        fig_scatter.update_layout(
            xaxis_title="<b>Superficie (m²)</b>",
            yaxis_title="<b>Prix (TND)</b>",
            margin=dict(t=50, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font=dict(size=20, color="#2C3E50")
        )
    else:
        fig_scatter = go.Figure()
        fig_scatter.update_layout(title="<b>Données de superficie insuffisantes</b>")
    
    # NOUVEAU GRAPHIQUE 1: Répartition par nature (vente/location)
    fig_nature = px.pie(
        dataframe, 
        names="nature",
        title="<b>Répartition vente/location</b>",
        color="nature", 
        color_discrete_map={'Vente': colors['Vente'], 'Location': colors['Location']},
        hole=0.6
    )
    fig_nature.update_traces(textinfo='percent+label', pull=[0.05, 0.05], textfont_size=14)
    fig_nature.update_layout(
        font=dict(size=12),
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=20, color="#2C3E50")
    )
    
    # NOUVEAU GRAPHIQUE 2: Prix au m² par type
    if 'prix_m2' in dataframe.columns and not dataframe['prix_m2'].isna().all():
        prix_m2_type = dataframe.dropna(subset=['prix_m2']).groupby('type_bien')['prix_m2'].median().reset_index()
        fig_prix_m2 = px.bar(
            prix_m2_type,
            x='type_bien',
            y='prix_m2',
            color='type_bien',
            color_discrete_map=colors,
            title="<b>Prix médian au m² par type de bien</b>",
            text_auto='.0f'
        )
        fig_prix_m2.update_layout(
            xaxis_title="<b>Type de bien</b>",
            yaxis_title="<b>Prix/m² (TND)</b>",
            margin=dict(t=50, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font=dict(size=20, color="#2C3E50")
        )
    else:
        fig_prix_m2 = go.Figure()
        fig_prix_m2.update_layout(title="<b>Données de prix/m² insuffisantes</b>")
    
    # NOUVEAU GRAPHIQUE 3: Heatmap Ville x Type de bien
    ville_type_count = dataframe.groupby(['Ville', 'type_bien']).size().reset_index(name='count')
    top_villes_list = dataframe['Ville'].value_counts().head(8).index.tolist()
    filtered_ville_type = ville_type_count[ville_type_count['Ville'].isin(top_villes_list)]
    
    pivot_data = filtered_ville_type.pivot(index='Ville', columns='type_bien', values='count').fillna(0)
    
    fig_heatmap = px.imshow(
        pivot_data,
        labels=dict(x="Type de bien", y="Ville", color="Nombre d'annonces"),
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale='YlOrRd',
        title="<b>Répartition des types de biens par ville</b>"
    )
    fig_heatmap.update_layout(
        xaxis_title="<b>Type de bien</b>",
        yaxis_title="<b>Ville</b>",
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=20, color="#2C3E50")
    )
    
    return fig_type_bien, fig_top_villes, fig_distribution_prix, fig_prix_moyen, fig_scatter, fig_nature, fig_prix_m2, fig_heatmap

# Create the figures
if not df.empty:
    fig_type_bien, fig_top_villes, fig_distribution_prix, fig_prix_moyen, fig_scatter, fig_nature, fig_prix_m2, fig_heatmap = create_figures(df)
else:
    # Create empty figures
    fig_type_bien = go.Figure()
    fig_top_villes = go.Figure()
    fig_distribution_prix = go.Figure()
    fig_prix_moyen = go.Figure()
    fig_scatter = go.Figure()
    fig_nature = go.Figure()
    fig_prix_m2 = go.Figure()
    fig_heatmap = go.Figure()

# Calculate key metrics
if not df.empty:
    nb_annonces = len(df)
    prix_moyen = int(df['Prix_nettoye'].mean()) if 'Prix_nettoye' in df else 0
    prix_median = int(df['Prix_nettoye'].median()) if 'Prix_nettoye' in df else 0
    nb_villes = df['Ville'].nunique() if 'Ville' in df else 0
    nb_vente = df[df['nature'] == 'Vente'].shape[0] if 'nature' in df else 0
    nb_location = df[df['nature'] == 'Location'].shape[0] if 'nature' in df else 0
    prix_moyen_m2 = int(df['prix_m2'].dropna().median()) if 'prix_m2' in df else 0
else:
    nb_annonces = 0
    prix_moyen = 0
    prix_median = 0
    nb_villes = 0
    nb_vente = 0
    nb_location = 0
    prix_moyen_m2 = 0

# Layout components

# Header avec animation et logo
header = html.Div(
    [
        dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src="https://www.mubawab-media.com/assets/logos/mubawab.png", className="logo-img"), width="auto"),
                                dbc.Col(dbc.NavbarBrand("Analyse Immobilière Tunisie", className="ms-2 fade-in")),
                            ],
                            align="center",
                        ),
                        href="#",
                    ),
                    dbc.NavbarToggler(id="navbar-toggler"),
                    dbc.Collapse(
                        id="navbar-collapse",
                        navbar=True,
                    ),
                ],
                fluid=True,
            ),
            color="primary",
            dark=True,
            className="mb-4",
        ),
        html.Div(
            dbc.Container(
                [
                    html.H1("Tableau de Bord Immobilier Tunisie", className="display-4 fade-in"),
                    html.P(
                        f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y')}",
                        className="lead fade-in"
                    ),
                ]
            ),
            className="p-5 mb-4 bg-light rounded-3 fade-in",
        ),
    ]
)

# Metrics cards
metrics = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Nombre d'annonces"),
                    dbc.CardBody(
                        [
                            html.H2(f"{nb_annonces:,}", className="card-title metric-value pulse"),
                            html.P("annonces immobilières", className="card-text"),
                        ]
                    ),
                ],
                className="text-center h-100 metric-card hover-card",
                color="light"
            ),
            width={"size": 3, "offset": 0},
            className="mb-4",
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Prix moyen"),
                    dbc.CardBody(
                        [
                            html.H2(f"{prix_moyen:,}", className="card-title metric-value"),
                            html.P("TND", className="card-text"),
                        ]
                    ),
                ],
                className="text-center h-100 metric-card hover-card",
                color="light"
            ),
            width={"size": 2, "offset": 0},
            className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Prix médian"),
                    dbc.CardBody(
                        [
                            html.H2(f"{prix_median:,}", className="card-title metric-value"),
                            html.P("TND", className="card-text"),
                        ]
                    ),
                ],
                className="text-center h-100 metric-card hover-card",
                color="light"
            ),
            width={"size": 2, "offset": 0},
            className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Ventes"),
                    dbc.CardBody(
                        [
                            html.H2(f"{nb_vente:,}", className="card-title metric-value"),
                            html.P(f"({nb_vente/nb_annonces*100:.1f}% du total)" if nb_annonces > 0 else "", className="card-text"),
                        ]
                    ),
                ],
                className="text-center h-100 metric-card hover-card",
                color="light"
            ),
            width={"size": 2, "offset": 0},
            className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Locations"),
                    dbc.CardBody(
                        [
                            html.H2(f"{nb_location:,}", className="card-title metric-value"),
                            html.P(f"({nb_location/nb_annonces*100:.1f}% du total)" if nb_annonces > 0 else "", className="card-text"),
                        ]
                    ),
                ],
                className="text-center h-100 metric-card hover-card",
                color="light"
            ),
            width={"size": 2, "offset": 0},
            className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Prix/m² médian"),
                    dbc.CardBody(
                        [
                            html.H2(f"{prix_moyen_m2:,}", className="card-title metric-value"),
                            html.P("TND/m²", className="card-text"),
                        ]
                    ),
                ],
                className="text-center h-100 metric-card hover-card",
                color="light"
            ),
            width={"size": 3, "offset": 0},
            className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Villes"),
                    dbc.CardBody(
                        [
                            html.H2(f"{nb_villes:,}", className="card-title metric-value"),
                            html.P("zones différentes", className="card-text"),
                        ]
                    ),
                ],
                className="text-center h-100 metric-card hover-card",
                color="light"
            ),
            width={"size": 3, "offset": 0},
            className="mb-4"
        ),
    ],
    className="mb-4 fade-in",
)

# Filters panel
filters = dbc.Card(
    [
        dbc.CardHeader([
            html.I(className="fas fa-filter me-2"),
            "Filtres d'analyse"
        ]),
        dbc.CardBody(
            [
                html.P("Nature:", className="fw-bold"),
                dcc.Dropdown(
                    id='nature-dropdown',
                    options=[
                        {'label': 'Tous', 'value': 'Tous'},
                        {'label': 'Vente', 'value': 'Vente'},
                        {'label': 'Location', 'value': 'Location'}
                    ],
                    value='Tous',
                    multi=False,
                    className="mb-3"
                ),
                
                html.P("Type de bien:", className="fw-bold"),
                dcc.Dropdown(
                    id='type-dropdown',
                    options=[{'label': 'Tous', 'value': 'Tous'}] + [{'label': t, 'value': t} for t in df['type_bien'].unique()] if not df.empty else [],
                    value='Tous',
                    multi=False,
                    className="mb-3"
                ),

                html.Hr(),
                
                html.P("Gamme de prix (TND):", className="fw-bold"),
                dcc.RangeSlider(
                    id='prix-slider',
                    min=int(df['Prix_nettoye'].min()) if not df.empty and 'Prix_nettoye' in df else 0,
                    max=int(df['Prix_nettoye'].max()) if not df.empty and 'Prix_nettoye' in df else 1000000,
                    step=10000,
                    marks={
                        i: f'{i/1000:.0f}K' if i < 1000000 else f'{i/1000000:.0f}M' 
                        for i in range(
                            int(df['Prix_nettoye'].min()) if not df.empty and 'Prix_nettoye' in df else 0, 
                            int(df['Prix_nettoye'].max()) if not df.empty and 'Prix_nettoye' in df else 1000000, 
                            max(50000, int((df['Prix_nettoye'].max() - df['Prix_nettoye'].min())/10)) if not df.empty and 'Prix_nettoye' in df else 100000
                        )
                    },
                    value=[
                        int(df['Prix_nettoye'].min()) if not df.empty and 'Prix_nettoye' in df else 0, 
                        int(df['Prix_nettoye'].max()) if not df.empty and 'Prix_nettoye' in df else 1000000
                    ],
                    className="mt-2 mb-4",
                ),
                
                html.P("Top villes:", className="fw-bold"),
                dcc.Dropdown(
                    id='ville-dropdown',
                    options=[{'label': 'Toutes', 'value': 'Toutes'}] + 
                            [{'label': ville, 'value': ville} 
                             for ville in df['Ville'].value_counts().head(15).index.tolist()] if not df.empty else [],
                    value='Toutes',
                    multi=True,
                    className="mb-3"
                ),
                
                dbc.Button(
                    [html.I(className="fas fa-sync-alt me-2"), "Réinitialiser les filtres"],
                    id="reset-button",
                    color="secondary",
                    className="w-100 mt-3"
                )
            ]
        ),
    ],
    className="mb-4 fade-in filter-card",
)

# Charts layout
charts = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(id='nature-chart', figure=fig_nature, className="dash-graph"),# Cette partie continue la définition du layout des graphiques
                            width=6,
                            className="mb-4",
                        ),
                        dbc.Col(
                            dcc.Graph(id='type-chart', figure=fig_type_bien, className="dash-graph"),
                            width=6,
                            className="mb-4",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(id='ville-chart', figure=fig_top_villes, className="dash-graph"),
                            width=12,
                            className="mb-4",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(id='prix-distribution-chart', figure=fig_distribution_prix, className="dash-graph"),
                            width=6,
                            className="mb-4",
                        ),
                        dbc.Col(
                            dcc.Graph(id='prix-moyen-chart', figure=fig_prix_moyen, className="dash-graph"),
                            width=6,
                            className="mb-4",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(id='scatter-chart', figure=fig_scatter, className="dash-graph"),
                            width=6,
                            className="mb-4",
                        ),
                        dbc.Col(
                            dcc.Graph(id='prix-m2-chart', figure=fig_prix_m2, className="dash-graph"),
                            width=6,
                            className="mb-4",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(id='heatmap-chart', figure=fig_heatmap, className="dash-graph"),
                            width=12,
                            className="mb-4",
                        ),
                    ]
                ),
            ],
            width=9,
        ),
        dbc.Col(
            filters,
            width=3,
        ),
    ],
    className="fade-in",
)

# Top annonces table
if not df.empty:
    top_annonces = df.sort_values('Prix_nettoye', ascending=False).head(5)
    top_annonces_table = dbc.Card(
        [
            dbc.CardHeader([
                html.I(className="fas fa-chart-line me-2"),
                "Top 5 annonces les plus chères"
            ]),
            dbc.CardBody(
                DataTable(
                    id='top-annonces-table',
                    columns=[
                        {'name': 'Titre', 'id': 'Titre'},
                        {'name': 'Prix', 'id': 'Prix'},
                        {'name': 'Type', 'id': 'type_bien'},
                        {'name': 'Nature', 'id': 'nature'},  # Ajout de la colonne nature
                        {'name': 'Ville', 'id': 'Ville'},
                    ],
                    data=top_annonces.to_dict('records'),
                    style_header={
                        'backgroundColor': '#5B86E5',
                        'color': 'white',
                        'fontWeight': 'bold'
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'whiteSpace': 'normal',
                        'height': 'auto',
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    page_size=5,
                )
            )
        ],
        className="mb-4 fade-in",
    )
else:
    top_annonces_table = html.Div()

# Footer
footer = html.Footer(
    dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Analyse Immobilière Tunisie", className="text-white"),
                        html.P(
                            "Tableau de bord analytique pour le marché immobilier tunisien",
                            className="text-muted"
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
        className="py-4",
    ),
    className="mt-4 footer",
)

# App layout
app.layout = html.Div(
    [
        header,
        dbc.Container(
            [
                metrics,
                charts,
                top_annonces_table,
            ],
            fluid=True,
        ),
        footer
    ]
)

# Callbacks
@app.callback(
    [
        Output('nature-chart', 'figure'),
        Output('type-chart', 'figure'),
        Output('ville-chart', 'figure'),
        Output('prix-distribution-chart', 'figure'),
        Output('prix-moyen-chart', 'figure'),
        Output('scatter-chart', 'figure'),
        Output('prix-m2-chart', 'figure'),
        Output('heatmap-chart', 'figure'),
        Output('top-annonces-table', 'data'),  # Ajout de cet output
    ],
    [
        Input('nature-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('prix-slider', 'value'),
        Input('ville-dropdown', 'value'),
        Input('reset-button', 'n_clicks')
    ]
)
def update_charts(nature_value, type_value, prix_range, villes_value, n_clicks):
    ctx = callback_context
    
    # Reset filters if button was clicked
    if ctx.triggered_id == 'reset-button':
        # Don't actually filter the dataframe here, just return to original figures
        return (*create_figures(df), df.sort_values('Prix_nettoye', ascending=False).head(5).to_dict('records'))
    
    # Apply filters
    filtered_df = df.copy()
    
    # Filter by nature
    if nature_value != 'Tous':
        filtered_df = filtered_df[filtered_df['nature'] == nature_value]
    
    # Filter by type
    if type_value != 'Tous':
        filtered_df = filtered_df[filtered_df['type_bien'] == type_value]
    
    # Filter by price range
    filtered_df = filtered_df[(filtered_df['Prix_nettoye'] >= prix_range[0]) & 
                             (filtered_df['Prix_nettoye'] <= prix_range[1])]
    
    # Filter by ville
    if villes_value != 'Toutes' and isinstance(villes_value, list) and len(villes_value) > 0 and 'Toutes' not in villes_value:
        filtered_df = filtered_df[filtered_df['Ville'].isin(villes_value)]
    
    # Create updated figures with filtered dataframe
    figures = create_figures(filtered_df)
    
    # Update top annonces table
    top_annonces_data = filtered_df.sort_values('Prix_nettoye', ascending=False).head(5).to_dict('records')
    
    return (*figures, top_annonces_data)

# Reset callback for the filters
@app.callback(
    [
        Output('nature-dropdown', 'value'),
        Output('type-dropdown', 'value'),
        Output('prix-slider', 'value'),
        Output('ville-dropdown', 'value'),
    ],
    Input('reset-button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    return ('Tous', 
            'Tous', 
            [int(df['Prix_nettoye'].min()) if not df.empty and 'Prix_nettoye' in df else 0, 
             int(df['Prix_nettoye'].max()) if not df.empty and 'Prix_nettoye' in df else 1000000],
            'Toutes')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)