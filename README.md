# FFHandball Scraper (Python)

Ce projet est le module d'acquisition de données de la solution. Il est chargé de récupérer, traiter et stocker les résultats de matchs et les classements depuis le site officiel de la FFHandball.

Il implémente une stratégie **"Multi-Sources"** pour garantir la fiabilité et la précision des données (notamment les noms officiels des phases de championnat).

## 🏗 Architecture & Logique

Le scraper ne se contente pas de lire du HTML, il agit comme un client intelligent :

1.  **Orchestration :** Parcourt une liste d'URLs de compétitions (poules).
2.  **Smart Ranking (API Sécurisée) :**
    * Interroge l'API interne de la fédération (`wp-json`).
    * Déchiffre la réponse (XOR + Base64) pour contourner l'obfuscation.
    * **Pourquoi ?** C'est le seul moyen fiable d'obtenir le **"Nom Officiel de la Phase"** (ex: *Excellence* vs *Brassage*) pour distinguer les onglets sur l'application mobile.
3.  **Scraping Matchs (HTML) :**
    * Récupère les rencontres et scores via le rendu HTML classique.
    * Enrichit ces données avec le "Nom Officiel" récupéré à l'étape précédente.
4.  **Persistance (SQL) :**
    * Insère ou met à jour les données en base (MySQL) de manière idempotente (`ON DUPLICATE KEY UPDATE`).

## 🛠 Stack Technique

* **Langage :** Python 3.10+
* **Librairies Clés :**
    * `BeautifulSoup4` : Parsing HTML.
    * `Requests` : Appels HTTP & API.
    * `MySQL-Connector` : Gestion de la base de données.
* **Base de Données :** MySQL (Table `matches` et `ranking`).

## 🚀 Installation & Lancement

### 1. Pré-requis
* Python installé.
* Une base de données MySQL active (locale ou Docker).

### 2. Configuration
Créez un fichier `.env` à la racine avec les accès BDD :

```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=get_results
```

### 3. Installation des dépendances
Bash

```
pip install -r requirements.txt
```

### 4. Exécution
Pour lancer une récupération complète manuelle :

```
python run_daily_scraping.py
```

📂 Structure du Projet 

- src/scraping/ : Logique d'extraction.
- get_ranking_api.py : Cœur de la logique "Smart Ranking" (Appel API + Déchiffrement).
- get_match_results.py : Orchestrateur par poule (fusionne API + HTML).
- src/saving/ : Écriture en base (db_writer.py).
- src/utils/ : Outils transverses (Formatage dates, Logs).
- init.sql : Schéma de base de données de référence.