import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Banking Expert Advisor", layout="wide")

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    # 1. Sélecteur de Langue
    st.write("🌐 **Language / Langue / Idioma**")
    language = st.selectbox(
        "", # Label vide car le texte est au-dessus
        ["English", "French", "Spanish"],
        label_visibility="collapsed"
    )

    st.write("---") # Séparateur horizontal

    # 2. Sélecteur d'État (Nouvelle section ajoutée)
    st.write("📍 **Select State / Choisir l'État**")
    states_list = ["New York", "Pennsylvania", "California", "Florida"]
    selected_state = st.selectbox(
        "Sélectionnez la zone d'analyse :",
        options=states_list,
        index=0
    )

    st.write("---")

    # 3. Zone d'Upload PDF
    st.write("📄 **Upload PDF**")
    uploaded_file = st.file_uploader(
        "Drag and drop file here",
        type=["pdf"],
        help="Limit 200MB per file • PDF"
    )
    
    if uploaded_file:
        st.sidebar.success(f"Fichier '{uploaded_file.name}' prêt.")

    # Bouton de gestion en bas (comme sur votre capture)
    st.write("---")
    if st.button("Gérer l'application"):
        st.info("Paramètres d'administration ouverts.")

# --- CONTENU PRINCIPAL ---
# En-tête dynamique basé sur votre expérience bancaire
st.title("🏦 Banking Expert Advisor")
st.subheader(f"Analyse des opérations et enchères pour : {selected_state}")

# Affichage d'un message d'accueil si aucun fichier n'est chargé
if not uploaded_file:
    st.info(f"Veuillez charger un document PDF pour commencer l'analyse des données de l'État de {selected_state}.")
    
    # Rappel visuel pour l'utilisateur
    st.markdown(f"""
    **Expertise actuelle activée :**
    * **Région :** {selected_state}
    * **Focus :** Customer Relationship Management (CRM) et Opérations bancaires.
    """)
else:
    # Ici, vous placerez votre logique de traitement du PDF
    st.success(f"Analyse lancée pour le document dans l'État de {selected_state}...")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="État sélectionné", value=selected_state)
    with col2:
        st.metric(label="Fichier", value=uploaded_file.name[:20] + "...")


