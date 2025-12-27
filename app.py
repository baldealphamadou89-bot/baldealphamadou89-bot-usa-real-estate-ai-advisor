import streamlit as st
from openai imimport streamlit as st
from openai import OpenAI
import PyPDF2
import requests
from PIL import Image
from io import BytesIO

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="USA Real Estate AI Advisor", page_icon="🏠", layout="wide")

# Récupération des clés depuis les Secrets
openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

def get_street_view_image(address, api_key):
    """Appel à l'API Google Street View avec nettoyage d'adresse"""
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    
    # Nettoyage pour éviter les erreurs de formatage
    clean_address = address.replace('\n', ' ').replace('Address:', '').replace('Adresse:', '').strip()
    
    params = {
        "size": "600x400",
        "location": clean_address,
        "key": api_key,
        "fov": "90",
        "pitch": "0"
    }
    try:
        response = requests.get(base_url, params=params)
        # On vérifie si Google renvoie une vraie image (plus de 5ko)
        if response.status_code == 200 and len(response.content) > 5000:
            return Image.open(BytesIO(response.content))
        return None
    except:
        return None

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("⚙️ Paramètres")
    st.info("Analyseur d'enchères immobilières")
    selected_state = st.selectbox("État visé", ["Pennsylvania", "Florida", "New Jersey", "New York", "California"])
    uploaded_file = st.file_uploader("Charger le document d'enchère (PDF)", type="pdf")
    
    if st.button("🗑️ Réinitialiser"):
        st.session_state.clear()
        st.rerun()

# --- ZONE DE RAPPORT ---
st.title("🇺🇸 USA Real Estate Investment Advisor")
st.caption("Intelligence Artificielle GPT-4o + Validation Visuelle Google Street View")

if not openai_key:
    st.error("🔑 La clé OPENAI_API_KEY est manquante dans les Secrets.")
elif uploaded_file:
    client = OpenAI(api_key=openai_key)
    
    with st.spinner("Analyse du dossier et récupération des visuels..."):
        try:
            # 1. Lecture du PDF
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = "".join([page.extract_text() for page in reader.pages])

            # 2. Extraction de l'adresse par l'IA (Instruction stricte)
            addr_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": f"Donne uniquement l'adresse physique du bien sans aucun autre texte : {pdf_text}"}]
            )
            address = addr_res.choices[0].message.content.strip()

            # 3. Mise en page
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("👁️ Inspection de la Façade")
                if maps_key:
                    img = get_street_view_image(address, maps_key)
                    if img:
                        st.image(img, use_container_width=True, caption=f"Vue Street View : {address}")
                    else:
                        st.warning(f"⚠️ Image non trouvée pour : {address}. Vérifiez que la 'Street View Static API' est activée dans Google Cloud.")
                else:
                    st.info("💡 Ajoutez MAPS_API_KEY pour voir l'image.")

            with col2:
                st.subheader("📄 Analyse Financière & Juridique")
                report_res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"Tu es un analyste expert en saisies immobilières en {selected_state}. Analyse avec précision comme pour un dossier bancaire."},
                        {"role": "user", "content": f"Analyse les dettes et calcule le Max Bid (70% rule) : {pdf_text}"}
                    ]
                )
                st.markdown(report_res.choices[0].message.content)

        except Exception as e:
            st.error(f"Erreur technique : {e}")port OpenAI
import PyPDF2
import requests
from PIL import Image
from io import BytesIO

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="USA Real Estate AI Advisor", page_icon="🏠", layout="wide")

# Récupération des clés depuis les Secrets
openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

def get_street_view_image(address, api_key):
    """Appel à l'API Google Street View"""
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        "size": "600x400",
        "location": address,
        "key": api_key,
        "fov": "90",
        "pitch": "0"
    }
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except:
        return None
    return None

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("⚙️ Paramètres")
    st.info(f"Analyseur d'enchères immobilières")
    selected_state = st.selectbox("État visé", ["Pennsylvania", "Florida", "New Jersey", "New York", "California"])
    uploaded_file = st.file_uploader("Charger le document d'enchère (PDF)", type="pdf")
    
    if st.button("🗑️ Réinitialiser"):
        st.session_state.clear()
        st.rerun()

# --- ZONE DE RAPPORT ---
st.title("🇺🇸 USA Real Estate Investment Advisor")
st.caption("Intelligence Artificielle GPT-4o + Validation Visuelle Google Street View")

if not openai_key:
    st.error("🔑 La clé OPENAI_API_KEY est manquante dans les Secrets.")
elif uploaded_file:
    client = OpenAI(api_key=openai_key)
    
    with st.spinner("Analyse du dossier et récupération des visuels..."):
        try:
            # 1. Lecture du PDF
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = "".join([page.extract_text() for page in reader.pages])

            # 2. Extraction de l'adresse par l'IA
            addr_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": f"Extrais uniquement l'adresse physique complète de ce bien : {pdf_text}"}]
            )
            address = addr_res.choices[0].message.content.strip()

            # 3. Mise en page
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("👁️ Inspection de la Façade")
                if maps_key:
                    img = get_street_view_image(address, maps_key)
                    if img:
                        st.image(img, use_container_width=True, caption=f"Vue Street View : {address}")
                    else:
                        st.warning("⚠️ Image non trouvée pour cette adresse spécifique.")
                else:
                    st.info("💡 Ajoutez MAPS_API_KEY pour voir l'image.")

            with col2:
                st.subheader("📄 Analyse Financière & Juridique")
                report_res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"Tu es un analyste expert en saisies immobilières en {selected_state}."},
                        {"role": "user", "content": f"Analyse les dettes, la priorité des liens et calcule le Max Bid (70% rule) : {pdf_text}"}
                    ]
                )
                st.markdown(report_res.choices[0].message.content)

        except Exception as e:
            st.error(f"Erreur technique : {e}")

