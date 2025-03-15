# Get Results

## Description

```bash
get_results_python [Scrap]
├── .venv
├── data
│   └── database
├── src
│   ├── database
│   │   └── db_connector.py
│   ├── navigation
│   │   ├── cookies.py
│   │   └── navigation.py
│   ├── saving
│   │   ├── db_writer.py
│   │   └── save_data_csv.py
│   ├── scraping
│   │   ├── get_all.py
│   │   ├── get_compet_data.py
│   │   ├── get_match_results.py
│   │   └── get_rank.py
│   └── utils
│       ├── purge
│       │   ├── db_drop.py
│       │   └── tables_drop.py
│       └── db_drop_option.py
├── docker-compose.yml
├── run_daily_scraping.py
├── notes.txt
├── README.md
└── requirements.txt
```

```bash
python -m venv venv
source venv/bin/activate   
pip install -r requirements.txt
```

```bash
chmod +x scraping_scheduler.py
```

```bash
./scraping_scheduler.py
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

http://localhost:5000/scrape
sudo apt update
sudo apt install -y xvfb
sudo apt install -y chromium-browser chromium-chromedriver
