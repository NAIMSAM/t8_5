

# # -----------------------------------------------------------------------------
# # Vérification de licence avant tout
# # -----------------------------------------------------------------------------
# import json, base64
# from datetime import datetime
# from cryptography.hazmat.primitives import serialization, hashes
# from cryptography.hazmat.primitives.asymmetric import padding

# def verify_license(license_path="license.lic", public_key_path="public_key.pem"):
#     # 1) Charger et parser le .lic
#     with open(license_path, "r", encoding="utf-8") as f:
#         lic = json.load(f)
#     lic_data = lic["license"]
#     signature = base64.b64decode(lic["signature"].encode("utf-8"))
#     # 2) Recomposer le JSON signé de manière canonique
#     signed_bytes = json.dumps(lic_data, sort_keys=True).encode("utf-8")
#     # 3) Charger la clé publique
#     with open(public_key_path, "rb") as f:
#         pub = serialization.load_pem_public_key(f.read())
#     # 4) Vérifier la signature
#     try:
#         pub.verify(
#             signature,
#             signed_bytes,
#             padding.PKCS1v15(),
#             hashes.SHA256()
#         )
#     except Exception as e:
#         raise RuntimeError("Licence invalide ou corrompue.") from e
#     # 5) Contrôler la date d'expiration
#     exp = datetime.fromisoformat(lic_data["expiry"])
#     if datetime.utcnow() > exp:
#         raise RuntimeError("Licence expirée le " + lic_data["expiry"])
#     # Vous pouvez aussi vérifier le max_users ici si besoin
#     return lic_data
#     # 5) Contrôler le ID de la machine pour éviter la duplication
#     import uuid
#     current_id = uuid.getnode()
#     if lic_data.get("machine_id") != current_id:
#         raise RuntimeError(
#             f"Licence non valide pour cette machine "
#             f"(expected {lic_data.get('machine_id')}, got {current_id})"
#         )


# # Essayer la vérification, arrêter si échec
# try:
#     license_info = verify_license()
# except RuntimeError as err:
#     # Affichage minimal avant sortie
#     print("❌ Erreur licence:", err)
#     import sys; sys.exit(1)












import streamlit as st
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# 1 | Config de la page
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="t₈/₅ Predictor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2 | Constantes des modèles
# -----------------------------------------------------------------------------
K = 0.386
alpha_m, beta_m, gamma_m = 5.225, 1.193, 0.898
B, C, D = 0.432, 0.260, 0.242
alpha_e, beta_e, gamma_e, F = 5.000, 1.194, 0.898, -6.173
svr_pipeline = joblib.load("pipeline_t85_SVR_20250422_1445.joblib")

# -----------------------------------------------------------------------------
# 3 | Fonctions de prédiction
# -----------------------------------------------------------------------------
def predict_multiplicative(CE, sigma, HD):
    return K * CE**alpha_m * sigma**beta_m * HD**gamma_m

def predict_expert(CE, sigma, HD):
    u = np.arctan((CE - B) / C) + np.pi/2
    return np.exp(np.log(D) + alpha_e*np.log(u)
                  + beta_e*np.log(sigma) + gamma_e*np.log(HD) + F)

def predict_svr(CE, sigma, HD):
    df = pd.DataFrame({"CE": [CE], "Contrainte": [sigma], "HD": [HD]})
    return svr_pipeline.predict(df)[0]

# -----------------------------------------------------------------------------
# 4 | Navigation
# -----------------------------------------------------------------------------
page = st.sidebar.selectbox("Menu", ["Accueil", "Prédiction"])

# -----------------------------------------------------------------------------
# 5 | Page d'accueil
# -----------------------------------------------------------------------------
if page == "Accueil":
    st.title("🛠️ Outil de prédiction du temps de refroidissement t₈/₅")
    st.markdown("### Un outil hybride mêlant modélisation physique et Machine Learning")
    st.divider()
    
    st.subheader("Contexte")
    st.markdown("""
    Le temps de refroidissement **t₈/₅** (800 → 500 °C) est critique pour la microstructure et la sensibilité à la fissuration des aciers soudés.
    Trois facteurs principaux influencent ce temps :
    - **CEV** (Carbone équivalent)
    - **σ** (Contrainte mécanique)
    - **HD** (Hydrogène diffusible)
    """)
    
    st.subheader("Approches comparées")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🔢 Modèle Multiplicatif")
        st.markdown("Forme : t₈/₅ = K·CEVᵅ·σᵝ·HDᵞ\n\nInterprétation simple et coefficientielle.")
    with col2:
        st.markdown("#### 🧠 Formule Experte")
        st.markdown("Forme : ln(t₈/₅) = ln D + α·ln[arctan(...)+π/2] + ...\n\nBornée et monotone, sans singularité.")
    with col3:
        st.markdown("#### 🤖 SVR-RBF")
        st.markdown("Modèle non-linéaire appris (Support Vector Regression).\n\nMeilleure performance et robustesse.")
    
    st.subheader("Accès au rapport")
    # Placeholder pour téléchargement
    st.download_button(
        label="📄 Télécharger le rapport complet",
        data=b"",  # remplacer par open("rapport.pdf", "rb").read()
        file_name="rapport_t85.pdf",
        mime="application/pdf"
    )

# -----------------------------------------------------------------------------
# 6 | Page de prédiction
# -----------------------------------------------------------------------------
else:
    st.header("Prédiction du temps de refroidissement t₈/₅")
    st.write("Entrez les paramètres puis cliquez sur **Prédire**.")

    with st.form(key="input_form"):
        CE = st.slider("Carbone équivalent (CEV)", 0.36, 0.50, 0.42, 0.001)
        sigma = st.slider("Contrainte σ (MPa)", 180, 420, 300, 5)
        HD = st.selectbox("Hydrogène diffusible (HD, ml H₂/100g)", [2.0, 2.75, 4.0, 5.5])
        submitted = st.form_submit_button("Prédire")

    if submitted:
        with st.spinner("Calcul en cours..."):
            t_mul = predict_multiplicative(CE, sigma, HD)
            t_exp = predict_expert(CE, sigma, HD)
            t_svr = predict_svr(CE, sigma, HD)

        st.divider()
        st.subheader("Résultats")
        c1, c2, c3 = st.columns(3)
        c1.metric("Multiplicatif", f"{t_mul:.2f} s")
        c2.metric("Formule experte", f"{t_exp:.2f} s")
        c3.metric("SVR‑RBF", f"{t_svr:.2f} s")

        st.divider()
        st.subheader("Sensibilité du modèle à la CEV")
        with st.expander("Voir détail de la sensibilité"):
            ce_range = np.linspace(0.36, 0.50, 100)
            t_mul_curve = [predict_multiplicative(ce, sigma, HD) for ce in ce_range]
            t_exp_curve = [predict_expert(ce, sigma, HD)       for ce in ce_range]
            t_svr_curve = [predict_svr(ce, sigma, HD)          for ce in ce_range]

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(ce_range, t_mul_curve, '--', linewidth=3,
                    color='tab:green', label='Multiplicatif')
            ax.plot(ce_range, t_exp_curve, '-', linewidth=2,
                    color='tab:blue', label='Expert')
            ax.plot(ce_range, t_svr_curve, '-.', linewidth=2,
                    color='tab:red', label='SVR')
            ax.scatter([CE], [t_mul], color='tab:green',
                       edgecolor='k', s=80, zorder=5)
            ax.scatter([CE], [t_exp], color='tab:blue',
                       edgecolor='k', s=80, zorder=5)
            ax.scatter([CE], [t_svr], color='tab:red',
                       edgecolor='k', s=80, zorder=5)
            ax.set_xlabel("Carbone équivalent (CEV)")
            ax.set_ylabel("t₈/₅ prédit (s)")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig, use_container_width=True)

        st.info("© Projet t₈/₅ Predictor - Expert & Data Science")
