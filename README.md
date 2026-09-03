# IoT Pointage — Système intelligent de pointage par reconnaissance faciale

Développement et validation d'un système intelligent de pointage basé sur
IoT avec une stratégie de test automatisée (PFE — 6 mois).

**Stack** : Python / Flask (backend + API REST) · React + Vite (frontend)
· OpenCV + face_recognition (reconnaissance faciale) · MySQL / XAMPP
(base de données) · pytest (tests automatisés).

## Architecture

```
Caméra IoT (webcam / RTSP)
        │  OpenCV
        ▼
Service de reconnaissance faciale (face_recognition)
        │
        ▼
API Flask (blueprints : auth, dashboard, employes, pointages,
           cameras, reconnaissance, tests)
        │  SQLAlchemy
        ▼
MySQL (pointage_iot) — via XAMPP
        ▲
        │  Axios / REST
Interface React (Dashboard, Flux en direct, Pointages, Employés,
                  Caméras IoT, Alertes, Rapports, Tests auto.)
```

## 1. Base de données (XAMPP)

1. Démarrer **Apache** et **MySQL** depuis le panneau de contrôle XAMPP.
2. Ouvrir phpMyAdmin (`http://localhost/phpmyadmin`).
3. Importer, dans l'ordre :
   - `backend/database/schema.sql` (création des tables, vue, procédure stockée)
   - `backend/database/seed.sql` (données de démonstration : employés, caméras, pointages)

## 2. Backend (Flask)

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
copy .env.example .env       # ou `cp` sous Linux/macOS — ajuster DATABASE_URL si besoin

python run.py
```

L'API démarre sur `http://localhost:5000`. Vérifier avec `GET /api/health`.

> **Note sur `face_recognition`** : cette bibliothèque dépend de `dlib`, qui
> nécessite CMake + un compilateur C++ installés sur la machine. Si son
> installation échoue, l'API démarre quand même (mode dégradé) mais les
> fonctions d'encodage/reconnaissance faciale sont désactivées jusqu'à ce
> que `dlib` soit correctement compilé.

### Créer le compte administrateur

```bash
curl -X POST http://localhost:5000/api/auth/inscription \
  -H "Content-Type: application/json" \
  -d "{\"nom_utilisateur\":\"admin\",\"email\":\"admin@societe.tn\",\"mot_de_passe\":\"admin123\",\"role\":\"admin\"}"
```

### Lancer les tests automatisés

```bash
cd backend
pytest --html=tests/rapports/rapport.html --self-contained-html
```

(ou directement depuis l'interface web, page **Tests auto.**)

## 3. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

L'application démarre sur `http://localhost:5173` et communique avec le
backend via un proxy Vite (`/api` → `http://localhost:5000`).

## Pages de l'application

| Page              | Description                                                       |
|-------------------|---------------------------------------------------------------------|
| Dashboard         | Statistiques, activité en direct, présence 7 jours, par département |
| Flux en direct    | Flux MJPEG en direct avec overlay de reconnaissance faciale          |
| Pointages         | Historique complet, filtrable par date / employé / type              |
| Employés          | CRUD + inscription faciale (upload photo → encodage 128D)            |
| Caméras IoT       | Gestion des dispositifs, statut en ligne/hors ligne                  |
| Alertes           | Retards, caméras hors ligne, visages inconnus                        |
| Rapports          | Tendances hebdomadaires, assiduité par département                   |
| Tests auto.       | Déclenchement et historique des suites pytest                        |

## Schéma de la base de données

`departements`, `utilisateurs`, `employes`, `cameras`, `pointages`,
`alertes`, `logs_systeme`, `resultats_tests` — voir `backend/database/schema.sql`
pour le détail des colonnes, clés étrangères, index, la vue
`vue_presence_departements` et la procédure stockée `sp_enregistrer_pointage`
(détection automatique des retards).

## Charte graphique

Thème sombre navy respectant la maquette de référence : fond `#0a0f1c`,
cartes `#111a2e`, accent bleu `#5b9dff`, succès `#22c55e`, danger `#ef4444`,
police `Inter` (texte) / `JetBrains Mono` (valeurs numériques et horodatages).
Variables centralisées dans `frontend/src/styles/theme.css`.
