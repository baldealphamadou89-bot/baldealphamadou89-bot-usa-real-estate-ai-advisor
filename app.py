import streamlit as st
import google.generativeai as genai
import requests
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="USA Real Estate AI", page_icon="🏠", layout="wide")

gemini_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Gemini Key", type="password")
maps_key = st.secrets.get("MAPS_API_KEY") or st.sidebar.text_input("Maps Key", type="password")

def get_model(api_key):
    try:
        genai.configure(api_key=api_key)
        # Test de plusieurs variantes de noms pour contourner l'erreur 404
        for name in ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']:
            try:
                m = genai.GenerativeModel(name)
                # Petit test de connectivité
                m.generate_content("test") 
                return m
            except:
                continue
        return None
    except:
        return None

# --- INTERFACE ---
st.title("🏠 USA Real Estate Investment Advisor")
st.caption("Expertise Bancaire (ex-Ecobank) + Intelligence Artificielle")

if not gemini_key:
    st.warning("👈 Entrez votre clé API dans la barre latérale.")
else:
    model = get_model(gemini_key)
    
    uploaded_file = st.sidebar.file_uploader("Charger le PDF d'enchère", type="pdf")
    selected_state = st.sidebar.selectbox("État", ["Pennsylvania", "Florida", "New York", "California"])

    if uploaded_file and model:
        with st.spinner("Analyse en cours..."):
            try:
                pdf_data = uploaded_file.read()
                
                # 1. Extraction Adresse
                res_addr = model.generate_content([
                    "Extrais l'adresse complète de ce document PDF.",
                    {"mime_type": "application/pdf", "data": pdf_data}
                ])
                address = res_addr.text.strip()
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.success(f"📍 Adresse : {address}")
                    prompt = f"Analyse ce document pour une enchère en {selected_state}. Liste les dettes et calcule le Max Bid (70% rule)."
                    report = model.generate_content([prompt, {"mime_type": "application/pdf", "data": pdf_data}])
                    st.markdown(report.text)
                
                with col2:
                    if maps_key:
                        st.subheader("👁️ Vision")
                        st.info("Récupération de la façade via Google Maps...")
                        # (La fonction Street View reste la même)
            except Exception as e:
                st.error(f"Erreur d'analyse : {e}")
                st.info("Vérifiez que 'Generative Language API' est bien ACTIVÉE dans votre console Google Cloud.")
