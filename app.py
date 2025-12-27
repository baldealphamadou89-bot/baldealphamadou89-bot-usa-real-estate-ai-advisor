import streamlit as st
import os

# Configuration de la page
st.set_page_config(page_title="Banking Expert Advisor", layout="wide")

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    # AJOUT DU LOGO
    # On vérifie si le fichier existe pour éviter une erreur au lancement
    logo_path = "logo.png" 
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.warning("Placez 'logo.png' dans le dossier du projet.")

    st.write("---")

    # 1. Sélecteur de Langue
    st.write("🌐 **Language / Langue**")
    language = st.selectbox(
        "Langue",
        ["English", "French"],
        label_visibility="collapsed",
        key="main_lang"
    )

    st.write("---")

    # 2. Sélecteur d'État (Synchronisé)
    st.write("📍 **Select State / Choisir l'État**")
    states_list = ["New York", "Pennsylvania", "California", "Florida"]
    selected_state = st.selectbox(
        "Zone d'analyse :",
        options=states_list,
        index=0,
        key="state_selector"
    )

    st.write("---")

    # 3. Zone d'Upload PDF
    st.write("📄 **Télécharger un PDF**")
    uploaded_file = st.file_uploader(
        "Glissez-déposez le fichier ici",
        type=["pdf"],
        key="pdf_uploader"
    )

# --- LOGIQUE D'AFFICHAGE DYNAMIQUE ---
# Dictionnaire de traduction pour éviter les erreurs de texte fixe
content = {
    "French": {
        "title": "Expertise en Opérations Bancaires",
        "header": f"Analyse pour l'État de : {selected_state}",
        "info": f"En attente du document PDF pour {selected_state}...",
        "crm": "Gestion de la Relation Client (CRM) activée."
    },
    "English": {
        "title": "Banking Operations Expert",
        "header": f"Analysis for: {selected_state}",
        "info": f"Waiting for PDF document for {selected_state}...",
        "crm": "Customer Relationship Management (CRM) activated."
    }
}

# Sélection de la langue actuelle
txt = content[language]

# --- CORPS DE L'APPLICATION ---
st.title(f"🏦 {txt['title']}")
st.subheader(txt['header'])

if not uploaded_file:
    st.info(txt['info'])
    st.markdown(f"**Focus Métier :** {txt['crm']}")
else:
    st.success(f"Analyse du document en cours pour {selected_state}...")
    # Ici viendra votre code d'extraction de données bancaires
