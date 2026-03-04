# Roadmap d'Amélioration - FFHandball Scraper

## Vue d'ensemble

Ce document présente la roadmap d'amélioration du projet, organisée en phases incrémentales (crescendo).

---

## Phase 1: Qualité de Code (Semaine 1)

### 1.1 Ajout de Ruff (Linting + Formatage)
- [ ] Installer ruff dans requirements.txt (dev)
- [ ] Créer fichier `ruff.toml` avec règles de base
- [ ] Configurer pre-commit hook pour ruff
- [ ] Corriger les violations existantes

### 1.2 Ajout de MyPy (Type Checking)
- [ ] Installer mypy dans requirements.txt (dev)
- [ ] Créer fichier `mypy.ini` avec configuration de base
- [ ] Ajouter annotation de types manquantes
- [ ] Intégrer mypy au pipeline CI

### 1.3 Correction des LSP Errors
- [ ] Corriger les paramètres `_env_file` invalides dans `tests/test_api_client.py`

---

## Phase 2: Couverture de Tests (Semaine 2)

### 2.1 Tests pour get_all.py
- [ ] Ajouter fixture pour mock IngestClient
- [ ] Tester `_extract_poule_id()` 
- [ ] Tester `_map_to_ingest_model()` - cas normaux
- [ ] Tester `_map_to_ingest_model()` - cas d'erreur
- [ ] Tester `_map_to_ranking_model()` 
- [ ] Tester `_build_pagination_urls()`
- [ ] Tester intégration avec scraping

### 2.2 Tests pour get_match_results.py
- [ ] Ajouter fixture pour mock HTTP responses
- [ ] Tester `fetch_html()` - succès et erreur
- [ ] Tester `_extract_journee_from_url()`
- [ ] Tester `_process_single_match()` 
- [ ] Tester `_extract_pagination_meta()`

### 2.3 Couverture Globale
- [ ] Atteindre 70% de coverage
- [ ] Ajouter tests d'intégration simples

---

## Phase 3: Résilience & Monitoring (Semaine 3)

### 3.1 Error Handling Amélioré
- [ ] Créer exceptions personnalisées (ScrapingError, IngestionError)
- [ ] Remplacer Exception génériques par des spécifiques
- [ ] Ajouter contexte aux messages d'erreur

### 3.2 Métriques
- [ ] Ajouter logging de timing par compétition
- [ ] Logger taux de succès/failure par source
- [ ] Créer summary log à la fin du job

### 3.3 Healthcheck Amélioré
- [ ] Vérifier connectivité MySQL au startup
- [ ] Vérifier connectivité API source
- [ ] Ajouter endpoint `/health/detailed`

---

## Phase 4: Configuration & CI/CD (Semaine 4)

### 4.1 Environnements Multiples
- [ ] Créer `.env.dev`, `.env.staging`, `.env.prod`
- [ ] Documenter les différences d'environnement
- [ ] Ajouter validation au startup

### 4.2 Pipeline CI
- [ ] Créer `.github/workflows/ci.yml`
- [ ] Étape 1: Installation dépendances
- [ ] Étape 2: Ruff lint
- [ ] Étape 3: MyPy typecheck
- [ ] Étape 4: Tests avec coverage

### 4.3 Pre-commit Hooks
- [ ] Créer `.pre-commit-config.yaml`
- [ ] Hooks: ruff, trailing-whitespace, end-of-file-fixer

---

## Phase 5: Optimisations (Optionnel)

### 5.1 Performance
- [ ] Ajouter cache pour responses API FFHandball
- [ ] Optimiser requêtes DB avec connection pooling

### 5.2 Robustesse
- [ ] Ajouter circuit breaker pour API backend
- [ ] Améliorer retry logic avec max duration

---

## Priorisation Recommandée

```
P1 (Must Have):
├── 1.1 Ruff + MyPy
├── 2.1 Tests get_all.py
└── 4.2 Pipeline CI

P2 (Should Have):
├── 2.2 Tests get_match_results.py
├── 3.1 Error Handling
└── 4.1 Environnements

P3 (Nice to Have):
├── 3.2 Métriques
├── 3.3 Healthcheck
└── 5. Optimisations
```

---

## Commandes Utiles

```bash
# Lancement linting
ruff check src/ tests/

# Formatage automatique
ruff format src/ tests/

# Type checking
mypy src/

# Tests avec coverage
pytest --cov=src --cov-report=term-missing

# Pré-commit
pre-commit run --all-files
```
