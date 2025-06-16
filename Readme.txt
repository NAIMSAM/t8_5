# t₈/₅ Predictor

**Version 1.0**

---

## Introduction

Le **t₈/₅ Predictor** est une application permettant de prédire le temps de refroidissement t₈/₅ (800→500 °C) des aciers soudés via trois approches :

1. **Modèle multiplicatif** (physique)
2. **Formule experte arc-tangente** (bornée, sans singularité)
3. **Modèle SVR‑RBF** (Machine Learning)

L’application vérifie également la validité d’un fichier de licence signé avant tout démarrage.

---

## Contenu de la distribution

```
t85_release/
├── t85-predictor_1.0.tar        # Image Docker compressée
├── LICENSE.txt                  # Contrat de licence propriétaire
├── license.lic                  # Fichier JSON signé (licence client)
├── public_key.pem               # Clé publique RSA pour vérification
├── start_app.bat                # Script Windows de démarrage (double-clic)
├── stop_app.bat                 # Script Windows d’arrêt (double-clic)
└── README.md                    # Ce fichier
```

---

## Prérequis

- **Docker** (Engine ou Desktop) installé et démarré sur la machine client.
- **Windows** (pour l’utilisation des scripts `.bat`).

---

## Installation de l’image Docker

1. Copier `t85-predictor_1.0.tar` dans un dossier local (par exemple `t85_release`).
2. Charger l’image :
   ```bash
   docker load -i t85-predictor_1.0.tar
   ```

---

## Fichiers de licence

- **LICENSE.txt** : conditions générales d’utilisation.
- **license.lic** : fichier de licence unique au client, valide jusqu’à la date indiquée.
- **public_key.pem** : clé utilisée pour vérifier la signature du fichier `license.lic`.

Veillez à **ne pas modifier** ces trois fichiers, ils doivent être montés en lecture seule dans le conteneur.

---

## Lancement de l’application

Double-cliquez sur le script **`start_app.bat`**. Il :

1. Démarre le conteneur Docker :
   ```bat
   docker run -d --name t85predictor \
     -p 8501:8501 \
     -v "%~dp0LICENSE.txt":/app/LICENSE.txt:ro \
     -v "%~dp0license.lic":/app/license.lic:ro \
     -v "%~dp0public_key.pem":/app/public_key.pem:ro \
     -v "%~dp0pipeline_t85_SVR_20250422_1445.joblib":/app/pipeline_t85_SVR_20250422_1445.joblib:ro \
     t85-predictor:1.0
   ```
2. Attend quelques secondes et ouvre automatiquement votre navigateur sur :
   ```
   http://localhost:8501
   ```

---

## Arrêt de l’application

Double-cliquez sur **`stop_app.bat`**, il exécutera :

```bat
docker stop t85predictor
docker rm t85predictor
```

---

## Support & Mise à jour

Pour toute question ou demande de mise à jour de licence :
- Email : support@storkmind.fr
- Tél. : +33 7 66 99 47 48

---

© 2025 storkMind — Tous droits réservés.

