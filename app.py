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
    genai.configure(api_key=api_key)
    # Utilisation de gemini-1.5-flash pour une meilleure compatibilité et rapidité
    return genai.GenerativeModel('gemini-1.5-flash')

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
st.caption("Système Expert : Intelligence Documentaire + Analyse par Vision Artificielle")

if not gemini_key:
    st.warning("👈 Veuillez configurer votre clé API dans la barre latérale pour activer l'IA.")
else:
    model = setup_models(gemini_key)
    
    if uploaded_file:
        with st.spinner("Analyse approfondie en cours..."):
            pdf_bytes = uploaded_file.read()
            
            # 1. Extraction Adresse
            addr_prompt = f"Extrais uniquement l'adresse complète du bien immobilier de ce document situé en {selected_state}."
            try:
                # Analyse du PDF pour trouver l'adresse
                addr_res = model.generate_content([addr_prompt, {"mime_type": "application/pdf", "data": pdf_bytes}])
                address = addr_res.text.strip()
                
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.success(f"📍 Adresse détectée : {address}")
                    st.subheader("📄 Rapport d'Analyse Juridique & Financière")
                    
                    full_prompt = f"""
                    Agis en tant qu'expert en immobilier aux USA. Analyse ce document pour {selected_state}.
                    Donne : 
                    1. Détail des dettes et priorité des liens (tax liens, mortgages, etc.).
                    2. Risques juridiques spécifiques à l'état (redemption periods, etc.).
                    3. Calcul du Max Bid selon la règle des 70% (ARV - repairs - debts).
                    """
                    report = model.generate_content([full_prompt, {"mime_type": "application/pdf", "data": pdf_bytes}])
                    st.markdown(report.text)

                with col2:
                    st.subheader("👁️ Inspection du Toit et Façade")
                    if maps_key:
                        img = get_street_view_image(address, maps_key)
                        if img:
                            st.image(img, use_container_width=True, caption="Vue Street View du bien")
                            vision_prompt = "Analyse l'état visuel du toit, des fenêtres et de la façade sur cette image. Y a-t-il des signes visibles de dommages ou d'abandon ?"
                            v_res = model.generate_content([vision_prompt, img])
                            st.info("Verdict Vision IA :")
                            st.write(v_res.text)
                    else:
                        st.info("Ajoutez une clé Maps pour l'inspection visuelle automatique.")

            except Exception as e:
                st.error(f"Erreur d'analyse : {e}")
