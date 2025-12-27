import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Banking Expert Advisor", layout="wide")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.write("🌐 **Language / Langue**")
    language = st.selectbox(
        "Sélectionnez la langue",
        ["English", "French"],
        label_visibility="collapsed"
    )

    st.write("---")

    st.write("📍 **Select State / Choisir l'État**")
    states_list = ["New York", "Pennsylvania", "California", "Florida"]
    # La variable 'selected_state' doit être utilisée partout pour être dynamique
    selected_state = st.selectbox(
        "Zone d'analyse :",
        options=states_list,
        index=0
    )

    st.write("---")

    # Upload PDF
    st.write("📄 **Télécharger un PDF**")
    uploaded_file = st.file_uploader(
        "Glissez-déposez le fichier ici",
        type=["pdf"]
    )

# --- LOGIQUE D'AFFICHAGE DYNAMIQUE ---
# On définit les textes selon la langue et l'État sélectionné
if language == "French":
    title = "Expertise de Services Bancaires"
    desc = f"Analyse des opérations et enchères pour l'État de : **{selected_state}**"
    info_msg = f"Veuillez charger un PDF pour {selected_state}."
else:
    title = "Banking Services Expert"
    desc = f"Analysis of operations and auctions for the State of: **{selected_state}**"
    info_msg = f"Please upload a PDF for {selected_state}."

# --- AFFICHAGE SUR LA PAGE PRINCIPALE ---
st.title(f"🏦 {title}")
st.header(selected_state) # Affiche l'état sélectionné en gros
st.write(desc)

if not uploaded_file:
    st.info(info_msg)
    
    # Rappel de vos compétences (Ecobank) adaptées à l'État choisi
    st.markdown(f"**Focus Expert :** Customer Relationship Management (CRM) - {selected_state}")
else:
    st.success(f"Analyse en cours pour {selected_state}...")
