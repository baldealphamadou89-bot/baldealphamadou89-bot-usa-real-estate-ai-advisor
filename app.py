import streamlit as st
import folium
from streamlit_folium import st_folium
from openai import OpenAI
import PyPDF2
import requests
from PIL import Image
from io import BytesIO
from fpdf import FPDF

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Alpha Balde | Real Estate Advisor", page_icon="🏠", layout="wide")

openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

# --- DICTIONNAIRE MULTILINGUE ---
languages = {
    "English": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Developed by Alpha Balde",
        "objective": "This platform combines AI (GPT-4o) and banking expertise to analyze US real estate auctions. It identifies debts, calculates ROI, and assesses risks.",
        "sidebar_title": "Settings",
        "upload_label": "Upload Auction PDF",
        "analysis_title": "Financial & Legal Analysis",
        "risk_score": "INVESTMENT GRADE",
        "roi_label": "Estimated ROI",
        "street_view": "Street View Inspection",
        "map_title": "Property Location",
        "footer": "© 2025 Alpha Balde | AI & Banking Expertise"
    },
    "Français": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Développé par Alpha Balde",
        "objective": "Cette plateforme combine l'IA (GPT-4o) et l'expertise bancaire pour analyser les enchères immobilières aux USA. Elle identifie les dettes, calcule le ROI et évalue les risques.",
        "sidebar_title": "Paramètres",
        "upload_label": "Charger le PDF d'enchère",
        "analysis_title": "Analyse Financière & Juridique",
        "risk_score": "SCORE D'INVESTISSEMENT",
        "roi_label": "ROI Estimé",
        "street_view": "Inspection de la Façade",
        "map_title": "Localisation du Bien",
        "footer": "© 2025 Alpha Balde | Expertise IA & Bancaire"
    },
    "Español": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Desarrollado por Alpha Balde",
        "objective": "Esta plataforma combina IA (GPT-4o) y experiencia bancaria para analizar subastas inmobiliarias en EE. UU. Identifica deudas, calcula el ROI y evalúa riesgos.",
        "sidebar_title": "Ajustes",
        "upload_label": "Cargar PDF de subasta",
        "analysis_title": "Análisis Financiero y Legal",
        "risk_score": "CALIFICACIÓN DE RIESGO",
        "roi_label": "ROI Estimado",
        "street_view": "Inspección de Fachada",
        "map_title": "Ubicación de la Propiedad",
        "footer": "© 2025 Alpha Balde | Experiencia en IA y Banca"
    }
}

# --- SÉLECTION DE LA LANGUE ---
selected_lang = st.sidebar.selectbox("🌐 Language", ["English", "Français", "Español"])
t = languages[selected_lang]

# --- EN-TÊTE AVEC LOGO ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    # Image de couverture élégante
    st.image("https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=400&q=80")
with col_title:
    st.title(t['welcome'])
    st.subheader(f"👨‍💻 {t['dev_by']}")

with st.container():
    st.markdown(f"""<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b;">{t['objective']}</div>""", unsafe_allow_html=True)

st.divider()

# --- LOGIQUE PRINCIPALE ---
if uploaded_file := st.sidebar.file_uploader(t['upload_label'], type="pdf"):
    client = OpenAI(api_key=openai_key)
    
    with st.spinner("Analyse multicritère en cours..."):
        # 1. Extraction PDF
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "".join([p.extract_text() for p in reader.pages])

        # 2. IA : Extraction Adresse et Analyse
        addr_res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Extract ONLY the physical address from this text: {pdf_text}"}]
        )
        address = addr_res.choices[0].message.content.strip()
        st.info(f"📍 **{address}**")

        # 3. Calculatrice (Sidebar)
        st.sidebar.divider()
        arv = st.sidebar.number_input("ARV ($)", value=300000)
        rehab = st.sidebar.number_input("Rehab ($)", value=40000)
        roi = ((arv - rehab - (arv*0.7)) / (arv*0.7)) * 100

        # 4. Affichage Colonnes
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader(f"🏠 {t['street_view']}")
            if maps_key:
                street_url = f"https://maps.googleapis.com/maps/api/streetview?size=600x400&location={address}&key={maps_key}"
                st.image(street_url, use_container_width=True)
            
            st.subheader(f"🗺️ {t['map_title']}")
            m = folium.Map(location=[39.9526, -75.1652], zoom_start=13) # Coordonnées par défaut (Philadelphie)
            folium.Marker([39.9526, -75.1652], popup=address).add_to(m)
            st_folium(m, height=250, use_container_width=True)

        with c2:
            st.subheader(f"⚖️ {t['analysis_title']}")
            ana_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": f"Expert analyst. Reply in {selected_lang}."},
                          {"role": "user", "content": f"Analyze debts and liens: {pdf_text}"}]
            )
            st.markdown(ana_res.choices[0].message.content)
            
            # Score de Risque
            st.metric(t['risk_score'], "Grade A" if roi > 20 else "Grade B")
            st.metric(t['roi_label'], f"{roi:.1f}%")

# --- FOOTER ---
st.markdown(f"""<div style="text-align: center; margin-top: 50px; color: grey; font-size: 0.8em;">{t['footer']}</div>""", unsafe_allow_html=True)
