import streamlit as st
from openai import OpenAI
import PyPDF2
import requests
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="USA Real Estate AI Advisor", page_icon="🏠", layout="wide")

openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

def get_street_view_image(address, api_key):
    """Récupère l'image Street View avec un nettoyage strict de l'adresse"""
    if not address or len(address) < 10:
        return None
        
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    # Nettoyage profond pour ne garder que l'essentiel
    clean_address = address.replace('\n', ' ').strip()
    
    params = {
        "size": "600x400",
        "location": clean_address,
        "key": api_key,
        "fov": "90"
    }
    try:
        response = requests.get(base_url, params=params)
        # Vérification que le contenu est bien une image valide
        if response.status_code == 200 and len(response.content) > 5000:
            return Image.open(BytesIO(response.content))
    except:
        return None
    return None

# --- INTERFACE PRINCIPALE ---
st.title("🇺🇸 USA Real Estate Investment Advisor")

if not openai_key:
    st.error("🔑 OPENAI_API_KEY manquante dans les Secrets.")
else:
    client = OpenAI(api_key=openai_key)
    
    with st.sidebar:
        st.header("📋 Options")
        selected_state = st.selectbox("État US", ["Pennsylvania", "Florida", "New York", "California"])
        uploaded_file = st.file_uploader("Charger le PDF d'enchère", type="pdf")

    if uploaded_file:
        with st.spinner("Analyse du document en cours..."):
            try:
                # 1. Extraction du texte PDF
                reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = "".join([page.extract_text() for page in reader.pages])

                # 2. Extraction STRICTE de l'adresse par l'IA
                addr_res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": f"Donne uniquement l'adresse complète (numéro, rue, ville, zip) sans aucun autre commentaire : {pdf_text}"}]
                )
                address = addr_res.choices[0].message.content.strip()

                # --- AFFICHAGE DE L'ADRESSE DÉTECTÉE ---
                st.info(f"📍 **Adresse identifiée :** {address}")

                col1, col2 = st.columns([1, 1])

                with col1:
                    st.subheader("👁️ Vue Street View")
                    if maps_key:
                        img = get_street_view_image(address, maps_key)
                        if img:
                            st.image(img, use_container_width=True)
                        else:
                            st.warning(f"Image non trouvée. Vérifiez que la 'Street View Static API' est ACTIVÉE dans votre console Google Cloud pour le projet associé à votre clé.")
                    else:
                        st.warning("Clé Google Maps manquante dans les Secrets.")

                with col2:
                    st.subheader("📄 Analyse Financière")
                    report_res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": f"Analyse les dettes et le Max Bid (70% rule) pour ce bien en {selected_state} : {pdf_text}"}]
                    )
                    st.markdown(report_res.choices[0].message.content)

            except Exception as e:
                st.error(f"Erreur d'analyse : {e}")
