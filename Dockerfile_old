# 1. Image légère Python, multi-arch compatible ARM64
FROM python:3.10-slim

# 2. Set le répertoire de travail
WORKDIR /app

# 3. Installer les dépendances système, Y COMPRIS les locales
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    chromium \
    chromium-driver \
    xvfb \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 4. Générer et configurer la locale française
RUN echo "fr_FR.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen fr_FR.UTF-8 && \
    update-locale LANG=fr_FR.UTF-8

# 5. Variables d'environnement (incluant la langue)
ENV LANG fr_FR.UTF-8
ENV LANGUAGE fr_FR:fr
ENV LC_ALL fr_FR.UTF-8
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    PATH="/usr/bin:${PATH}"

# 6. Copier les fichiers du projet
COPY . /app

# 7. Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 8. Donner des droits
RUN chmod +x scraping_scheduler.py

# 9. Exposer le port
EXPOSE 5000

# 10. Commande par défaut
CMD ["python", "scraping_scheduler.py"]