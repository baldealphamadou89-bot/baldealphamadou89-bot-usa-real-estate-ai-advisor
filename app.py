import streamlit as st
from openai import OpenAI
import PyPDF2
from fpdf import FPDF
import base64
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Alpha Balde | Real Estate AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. STYLE CSS PERSONNALISÉ (UI PREMIUM) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        border-top: 4px solid #d32f2f; 
    }
    div.stButton > button:first-child {
        background-color: #d32f2f; color: white; border-radius: 8px; border: none;
        padding: 0.6rem 2rem; font-weight: bold; width: 100%; transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #b71c1c; border: none; color: white; transform: translateY(-2px); }
    .report-card { 
        background-color: white; 
        padding: 25px; 
        border-radius: 15px; 
        border-left: 6px solid #d32f2f; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        color: #333; 
    }
    h1, h2, h3 { color: #1e1e1e; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS TECHNIQUES ---
def get_base64_logo(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def create_pdf(address, analysis, state, lang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Investment Analysis Report: {state}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Property: {address}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    # Nettoyage pour éviter les erreurs d'encodage PDF
    clean_text = analysis.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. DICTIONNAIRE MULTILINGUE ---
languages = {
    "English": {
        "welcome": "USA Real Estate AI Advisor",
        "state_label": "Select State",
        "upload_label": "Upload Auction PDF",
        "analysis_header": "Financial & Legal Analysis",
        "save_btn": "Download Expert Report (PDF)",
        "exp_text": "Banking Expert (Ex-Ecobank)",
        "landing_msg": "Please upload a document to begin the expert analysis."
    },
    "Français": {
        "welcome": "USA Real Estate AI Advisor",
        "state_label": "Choisir l'État",
        "upload_label": "Charger le PDF d'enchère",
        "analysis_header": "Analyse Financière & Juridique",
        "save_btn": "Télécharger le Rapport d'Expert (PDF)",
        "exp_text": "Expert Bancaire (Ex-Ecobank)",
        "landing_msg": "Veuillez charger un document pour commencer l'analyse d'expert."
    },
    "Español": {
        "welcome": "USA Real Estate AI Advisor",
        "state_label": "Seleccionar Estado",
        "upload_label": "Cargar PDF de subasta",
        "analysis_header": "Análisis Financiero y Legal",
        "save_btn": "Descargar Informe de Experto (PDF)",
        "exp_text": "Experto Bancario (Ex-Ecobank)",
        "landing_msg": "Por favor, cargue un documento para comenzar el análisis experto."
    }
}

# --- 5. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    # Chargement du logo local "logo.png.jpeg"
    logo_data = get_base64_logo("logo.png.jpeg")
    if logo_data:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{logo_data}" width="140"></div>', unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center;'>🏠</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    selected_lang = st.selectbox("🌐 Language / Idioma", ["English", "Français", "Español"])
    t = languages[selected_lang]
    
    # Réintégration de la liste des 7 États demandés
    states_list = ["New York", "New Jersey", "Pennsylvania", "California", "Florida", "Texas", "Maryland"]
    selected_state = st.selectbox(f"📍 {t['state_label']}", states_list)
    
    st.markdown("---")
    uploaded_file = st.file_uploader(t['upload_label'], type="pdf")
    st.markdown(f'<p style="font-size: 0.85em; color: #d32f2f; text-align: center; font-weight: bold;">{t["exp_text"]}</p>', unsafe_allow_html=True)

# --- 6. CORPS DE L'APPLICATION ---
st.markdown(f"<h1 style='text-align: center; margin-bottom: 0;'>{t['welcome']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #d32f2f; font-weight: bold; font-size: 1.2em; margin-top: 0;'>👨‍💻 Alpha Balde | {t['exp_text']}</p>", unsafe_allow_html=True)

if uploaded_file:
    # Vérification des clés API dans les secrets
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("Missing OpenAI API Key in Streamlit Secrets.")
    else:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        with st.spinner(f"Analyse des spécificités juridiques de {selected_state}..."):
            # Extraction du texte du PDF
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = "".join([p.extract_text() for p in reader.pages])

            # Analyse IA avec contexte État + Langue
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"Tu es Alpha Balde, expert bancaire. Analyse selon les lois immobilières de {selected_state}. Réponds en {selected_lang}."},
                    {"role": "user", "content": f"Analyse les dettes (liens), les taxes et les risques d'investissement pour ce document : {pdf_text}"}
                ]
            )
            report_text = response.choices[0].message.content
            
            # Extraction de l'adresse pour Street View
            addr_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": f"Return ONLY the physical address: {pdf_text}"}]
            )
            address = addr_res.choices[0].message.content.strip()

        # --- 7. AFFICHAGE DES RÉSULTATS (DASHBOARD) ---
        st.markdown("---")
        
        # Indicateurs KPIs
        k1, k2, k3 = st.columns(3)
        k1.metric("Jurisdiction", selected_state)
        k2.metric("Analysis Mode", "Expert Banking")
        k3.metric("Status", "✅ Completed")

        col1, col2 = st.columns([1, 1.3], gap="large")
        
        with col1:
            st.subheader("📸 Property Visualization")
            if "MAPS_API_KEY" in st.secrets:
                maps_url = f"https://maps.googleapis.com/maps/api/streetview?size=600x400&location={address}, {selected_state}&key={st.secrets['MAPS_API_KEY']}"
                st.image(maps_url, use_container_width=True, caption=f"Address: {address}")
            else:
                st.info(f"📍 Property detected: {address}")
                st.warning("Google Maps API Key missing for Street View.")

        with col2:
            st.subheader(f"📄 {t['analysis_header']}")
            st.markdown(f'<div class="report-card">{report_text}</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            # Génération et bouton de téléchargement PDF
            pdf_data = create_pdf(address, report_text, selected_state, selected_lang)
            st.download_button(
                label=f"📥 {t['save_btn']}",
                data=pdf_data,
                file_name=f"Expert_Report_{selected_state}_{address.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

else:
    # Écran de bienvenue (Landing Page)
    st.markdown("---")
    st.info(f"👋 **{t['landing_msg']}**")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🏦 Banking Expertise")
        st.write("Leveraging 5+ years at Ecobank Guinea in cash operations and CRM.")
    with c2:
        st.markdown("### ⚖️ State Compliance")
        st.write(f"Tailored rules for: {', '.join(states_list)}.")
    with c3:
        st.markdown("### 🚀 AI Precision")
        st.write("Advanced GPT-4o analysis for deep lien detection and risk assessment.")

st.markdown("<br><hr><center>© 2025 Alpha Balde | Real Estate Banking Intelligence</center>", unsafe_allow_html=True)
