import streamlit as st
import folium
from streamlit_folium import st_folium
from openai import OpenAI
import PyPDF2
import requests

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Alpha Balde | Real Estate AI", page_icon="🏠", layout="wide")

openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

# --- DICTIONNAIRE MULTILINGUE ---
languages = {
    "English": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Developed by Alpha Balde",
        "objective": "This platform combines AI (GPT-4o) and banking expertise to analyze US real estate auctions. It identifies debts, calculates ROI, and assesses risks to secure your investments.",
        "sidebar_title": "Settings",
        "upload_label": "Upload Auction PDF",
        "analysis_title": "Financial & Legal Analysis",
        "footer": "© 2025 Alpha Balde | AI & Banking Expertise"
    },
    "Français": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Développé par Alpha Balde",
        "objective": "Cette plateforme combine l'IA (GPT-4o) et l'expertise bancaire pour analyser les enchères immobilières aux USA. Elle identifie les dettes, calcule le ROI et évalue les risques pour sécuriser vos investissements.",
        "sidebar_title": "Paramètres",
        "upload_label": "Charger le PDF d'enchère",
        "analysis_title": "Analyse Financière & Juridique",
        "footer": "© 2025 Alpha Balde | Expertise IA & Bancaire"
    },
    "Español": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Desarrollado por Alpha Balde",
        "objective": "Esta plataforma combina IA (GPT-4o) y experiencia bancaria para analizar subastas inmobiliarias en EE. UU. Identifica deudas, calcula el ROI y evalúa riesgos para asegurar sus inversiones.",
        "sidebar_title": "Ajustes",
        "upload_label": "Cargar PDF de subasta",
        "analysis_title": "Análisis Financiero y Legal",
        "footer": "© 2025 Alpha Balde | Experiencia en IA y Banca"
    }
}

# --- SÉLECTION DE LA LANGUE ---
selected_lang = st.sidebar.selectbox("🌐 Language", ["English", "Français", "Español"])
t = languages[selected_lang]

# --- EN-TÊTE AVEC LOGO ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    # Utilisation de l'image de maison avec clés pour le logo
    st.image("https://img.freepik.com/vecteurs-premium/cle-maison-concept-immobilier_24877-21141.jpg", width=150)

with col_title:
    st.title(t['welcome'])
    st.subheader(f"👨‍💻 {t['dev_by']}")

# --- MESSAGE D'ACCUEIL ---
with st.container():
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 20px;">
        {t['objective']}
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- LOGIQUE DE L'APPLICATION ---
with st.sidebar:
    st.header(t['sidebar_title'])
    uploaded_file = st.file_uploader(t['upload_label'], type="pdf")

if uploaded_file:
    if not openai_key:
        st.error("Clé API OpenAI manquante dans les secrets.")
    else:
        client = OpenAI(api_key=openai_key)
        with st.spinner("Analyse en cours..."):
            # Extraction Texte
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = "".join([p.extract_text() for p in reader.pages])

            # Extraction Adresse
            addr_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": f"Donne uniquement l'adresse complète : {pdf_text}"}]
            )
            address = addr_res.choices[0].message.content.strip()
            st.info(f"📍 **Adresse identifiée :** {address}")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("👁️ Street View")
                if maps_key:
                    street_url = f"https://maps.googleapis.com/maps/api/streetview?size=600x400&location={address}&key={maps_key}"
                    st.image(street_url, use_container_width=True)
                else:
                    st.warning("Clé Google Maps manquante.")

            with col2:
                st.subheader(f"📄 {t['analysis_title']}")
                report_res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": f"Réponds en {selected_lang}"},
                              {"role": "user", "content": f"Analyse les dettes : {pdf_text}"}]
                )
                st.markdown(report_res.choices[0].message.content)

# --- PIED DE PAGE ---
st.markdown(f"""
    <div style="text-align: center; margin-top: 50px; color: grey; font-size: 0.8em;">
        {t['footer']}
    </div>
""", unsafe_allow_html=True)
