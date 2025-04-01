# Gestion simplifiée des services via SSH

## 📂 Organisation des fichiers

```bash
~/scripts/
├── start_services.sh
└── stop_services.sh
```

## 🚀 Démarrer les services (`start_services.sh`)

```bash
#!/bin/bash

cd /home/monprojet || exit 1

docker compose up -d

nohup cloudflared tunnel run api > cloudflared.log 2>&1 &
echo $! > cloudflared.pid
```

## 🛑 Arrêter les services (`stop_services.sh`)

```bash
#!/bin/bash

cd /home/monprojet || exit 1

docker compose down

if [ -f cloudflared.pid ]; then
    kill $(cat cloudflared.pid) && rm cloudflared.pid
fi
```

## ⚙️ Installation rapide

Rendre les scripts exécutables :

```bash
chmod +x ~/scripts/*.sh
```

Ajouter des alias dans `~/.bashrc` :

```bash
alias startservices='~/scripts/start_services.sh'
alias stopservices='~/scripts/stop_services.sh'
```

Appliquer immédiatement :

```bash
source ~/.bashrc
```

## ✅ Commandes

Depuis SSH :

- **Démarrer :** `startservices`
- **Arrêter :** `stopservices`

