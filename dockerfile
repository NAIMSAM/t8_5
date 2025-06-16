# (en partant du Dockerfile précédent)

# 1. Base Python légère
FROM python:3.10-slim

# 2. Configure locale (optionnel)
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# 3. Répertoire de travail
WORKDIR /app

# 4. Copier les fichiers de l’app et de licence
COPY requirements.txt            .
#COPY LICENSE.txt                 .
#COPY license.lic                 .
#COPY public_key.pem              .
COPY app.py                      .
# **Ajout de la pipeline ML**
COPY pipeline_t85_SVR_20250422_1445.joblib  .

# 5. Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 6. Exposer le port Streamlit
EXPOSE 8501

# 7. Démarrage automatique
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
