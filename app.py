import streamlit as st
from openai import OpenAI
import PyPDF2
import requests
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="USA Real Estate AI (OpenAI + Vision)", page_icon="🏠", layout="wide")

# Récupération des clés
openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

def get_street_view_image(address, api_key):
    """Récupère l'image de la façade via Google Maps API"""
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    params = {"size": "600x400", "location": address, "key": api_key, "fov": "90"}
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except:
        return None
    return None

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("⚙️ Configuration")
    selected_state = st.selectbox("État US", ["Pennsylvania", "Florida", "New Jersey", "New York"])
    uploaded_file = st.file_uploader("Charger le PDF d'enchère", type="pdf")
    
    if st.button("🗑️ Effacer la session"):
        st.session_state.clear()
        st.rerun()

# --- ZONE PRINCIPALE ---
st.title("🏠 USA Real Estate Investment Advisor")
st.caption("Intelligence Documentaire (GPT-4o) + Inspection Visuelle (Street View)")

if not openai_key:
    st.warning("👈 Veuillez configurer votre OPENAI_API_KEY dans les secrets.")
elif uploaded_file:
    client = OpenAI(api_key=openai_key)
    
    with st.spinner("Analyse approfondie en cours..."):
        try:
            # 1. Extraction du texte du PDF
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text()

            # 2. Demander l'adresse exacte à GPT-4o pour Google Maps
            addr_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": f"Extrais uniquement l'adresse complète du bien immobilier de ce texte : {pdf_text}"}]
            )
            address = addr_res.choices[0].message.content.strip()

            # 3. Affichage sur deux colonnes
            col1, col2 = st.columns([3, 2])

            with col1:
                st.success(f"📍 Adresse détectée : {address}")
                st.subheader("📄 Analyse du Dossier")
                analysis_res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": f"Analyse les dettes et les risques de ce bien en {selected_state} et donne le Max Bid (70% rule) : {pdf_text}"}]
                )
                st.markdown(analysis_res.choices[0].message.content)

            with col2:
                st.subheader("👁️ Vue Extérieure")
                if maps_key:
                    img = get_street_view_image(address, maps_key)
                    if img:
                        st.image(img, use_container_width=True, caption=f"Façade détectée à {address}")
                    else:
                        st.error("Image Street View non disponible pour cette adresse.")
                else:
                    st.info("Ajoutez votre MAPS_API_KEY pour voir la photo du bien.")

        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {e}")
