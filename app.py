import streamlit as st
import google.generativeai as genai
import requests
from PIL import Image
from io import BytesIO

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="USA Real Estate AI Advisor", 
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- RÉCUPÉRATION SÉCURISÉE DES CLÉS (Secrets ou Manuel) ---
gemini_key = st.secrets.get("GOOGLE_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

def setup_models(api_key):
    try:
        genai.configure(api_key=api_key)
        # Astuce : on utilise 'gemini-1.5-flash-latest' qui est souvent mieux reconnu
        return genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception as e:
        st.error(f"Erreur de configuration du modèle : {e}")
        return None

def get_street_view_image(address, api_key):
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
    
    if not gemini_key:
        gemini_key = st.text_input("1. Entrez votre Gemini API Key", type="password")
    else:
        st.success("✅ Clé Gemini chargée via Secrets")
        
    if not maps_key:
        maps_key = st.text_input("2. Entrez Google Maps API Key (Optionnel)", type="password")
    else:
        st.success("✅ Clé Maps chargée via Secrets")

    st.divider()
    st.header("📋 Analyse de l'Enchère")
    selected_state = st.selectbox("État US", ["California", "Florida", "New Jersey", "New York", "Pennsylvania"])
    uploaded_file = st.file_uploader("3. Charger le PDF d'enchère", type="pdf")
    
    if st.button("🗑️ Effacer la session"):
        st.session_state.clear()
        st.rerun()

# --- ZONE PRINCIPALE ---
st.title("🇺🇸 USA Real Estate Investment Advisor")
st.caption("Système Expert : Intelligence Documentaire + Vision IA")

if not gemini_key:
    st.warning("👈 Veuillez configurer votre clé API dans la barre latérale.")
else:
    model = setup_models(gemini_key)
    
    if model and uploaded_file:
        with st.spinner("Analyse approfondie en cours..."):
            try:
                pdf_bytes = uploaded_file.read()
                
                # 1. Extraction Adresse
                addr_prompt = f"Extrais uniquement l'adresse complète du bien immobilier de ce document situé en {selected_state}."
                addr_res = model.generate_content([addr_prompt, {"mime_type": "application/pdf", "data": pdf_bytes}])
                address = addr_res.text.strip()
                
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.success(f"📍 Adresse détectée : {address}")
                    st.subheader("📄 Rapport d'Analyse Juridique & Financière")
                    
                    full_prompt = f"""
                    Agis en tant qu'expert en immobilier aux USA. Analyse ce document pour {selected_state}.
                    Donne : 
                    1. Détail des dettes et priorité des liens.
                    2. Risques juridiques spécifiques à l'état.
                    3. Calcul du Max Bid selon la règle des 70%.
                    """
                    report = model.generate_content([full_prompt, {"mime_type": "application/pdf", "data": pdf_bytes}])
                    st.markdown(report.text)

                with col2:
                    st.subheader("👁️ Inspection Visuelle")
                    if maps_key:
                        img = get_street_view_image(address, maps_key)
                        if img:
                            st.image(img, use_container_width=True, caption="Vue Street View")
                            v_res = model.generate_content(["Analyse l'état du toit et des fenêtres.", img])
                            st.info("Verdict Vision :")
                            st.write(v_res.text)
                    else:
                        st.info("Ajoutez une clé Maps pour la vision.")

            except Exception as e:
                st.error(f"Erreur d'analyse : {e}")
                st.info("Conseil : Vérifiez que votre bibliothèque google-generativeai est à jour.")
