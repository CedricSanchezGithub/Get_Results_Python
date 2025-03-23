# 1. Image légère Python, multi-arch compatible ARM64
FROM python:3.10-slim

# 2. Set le répertoire de travail
WORKDIR /app

# 3. Installer Chromium et ses dépendances (meilleur contrôle des paquets)
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    xvfb \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 4. Variables d'environnement (corrigées avec les bons chemins)
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    PATH="/usr/bin:${PATH}"

# 5. Copier les fichiers du projet en une seule commande (plus rapide)
COPY . /app

# 6. Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. (Optionnel) Donner les droits si tu l'exécutes directement via chmod
RUN chmod +x scraping_scheduler.py

# 8. Exposer le port (ex: API Flask)
EXPOSE 5000

# 9. Commande par défaut
CMD ["python", "scraping_scheduler.py"]
