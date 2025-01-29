# Get Results

## Description

```bash
/scraping_project
├── /scraping            # Logique de scraping
│   ├── fetcher.py      # Téléchargement des pages HTML
│   ├── parser.py       # Extraction des données à partir du HTML
│   └── scheduler.py    # Programmation des exécutions périodiques
├── /database           # Gestion de la base de données
│   ├── db_connector.py # Connexion à la base de données
│   └── db_writer.py    # Insertion des données dans la base
├── /utils              # Utilitaires généraux
│   └── logger.py       # Gestion des logs
├── /tests              # Tests unitaires pour vérifier les modules
│   └── test_scraper.py # Tests du fetcher, parser, etc.
└── main.py             # Point d'entrée principal
```

```bash
git clone https://github.com/username/scraping_project.git
cd scraping_project
```

```bash
python -m venv venv
source venv/bin/activate   
pip install -r requirements.txt
```

```bash
python main.py
```

```SQL
DROP TABLE pool;
CREATE TABLE pool (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date VARCHAR(255) NOT NULL,      
    team_1_name VARCHAR(255) NOT NULL,     
    team_1_score INT NOT NULL,             
    team_2_name VARCHAR(255) NOT NULL,    
    team_2_score INT NOT NULL,             
    match_link VARCHAR(255),         
    competition VARCHAR(255),        
    day VARCHAR(255)                 
);

CREATE TABLE ranking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    position INT NOT NULL,
    club_name VARCHAR(255) NOT NULL,
    points INT NOT NULL
);

```
