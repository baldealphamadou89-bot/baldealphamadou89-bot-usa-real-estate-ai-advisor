import streamlit as st
from openai import OpenAI
import PyPDF2
from fpdf import FPDF
import base64
import os
import urllib.parse

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Alpha Balde | Real Estate AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. STYLE CSS ---
st.markdown("""
    <style>
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        border-top: 4px solid #d32f2f; 
    }
    .external-link {
        display: block; padding: 10px; margin: 5px 0;
        background-color: #f8f9fa; color: #1a73e8;
        text-decoration: none; border-radius: 8px;
        text-align: center; font-weight: bold; border: 1px solid #d32f2f;
        transition: 0.3s;
    }
    .external-link:hover { background-color: #ffebee; border-color: #b71c1c; }
    .report-card { background-color: white; padding: 25px; border-radius: 15px; border-left: 6px solid #d32f2f; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

def get_base64_logo(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

def create_pdf(address, analysis, state, lang, max_bid=0):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Analysis: {state}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 11)
    clean_text = analysis.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. DICTIONNAIRE MULTILINGUE ---
languages = {
    "English": {"welcome": "USA Real Estate AI Advisor", "state_label": "Select State", "upload_label": "Upload Auction PDF", "analysis_header": "Financial & Legal Analysis", "save_btn": "Download Expert Report (PDF)", "exp_text": "Banking Expert (Ex-Ecobank)", "landing_msg": "Please upload a document to begin.", "max_bid_label": "Max Bid", "comps_label": "Market Comparison"},
    "Français": {"welcome": "USA Real Estate AI Advisor", "state_label": "Choisir l'État", "upload_label": "Charger le PDF d'enchère", "analysis_header": "Analyse Financière & Juridique", "save_btn": "Télécharger le Rapport d'Expert (PDF)", "exp_text": "Expert Bancaire (Ex-Ecobank)", "landing_msg": "Veuillez charger un document pour commencer.", "max_bid_label": "Offre Max", "comps_label": "Comparaison Marché"},
    "Español": {"welcome": "USA Real Estate AI Advisor", "state_label": "Seleccionar Estado", "upload_label": "Cargar PDF", "analysis_header": "Análisis", "save_btn": "Descargar Informe", "exp_text": "Experto Bancario (Ex-Ecobank)", "landing_msg": "Por favor, cargue un documento.", "max_bid_label": "Puja Máxima", "comps_label": "Comparativa"}
}

# --- 4. BARRE LATÉRALE ---
with st.sidebar:
    logo_data = get_base64_logo("logo.png.jpeg")
    if logo_data:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{logo_data}" width="140"></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    selected_lang = st.selectbox("🌐 Language", ["English", "Français", "Español"])
    t = languages[selected_lang]
    
    states_list = ["New York", "New Jersey", "Pennsylvania", "California", "Florida", "Texas", "Maryland"]
    selected_state = st.selectbox(f"📍 {t['state_label']}", states_list)

    st.markdown("### 📊 Financial Calculator")
    arv = st.number_input("ARV ($)", min_value=0, value=200000)
    repairs = st.number_input("Repairs ($)", min_value=0, value=30000)
    max_bid = (arv * 0.70) - repairs
    
    st.markdown("---")
    uploaded_file = st.file_uploader(t['upload_label'], type="pdf")
    
    # Zone dynamique pour les liens (placée ICI pour être visible dans la sidebar)
    comps_container = st.container()
    
    st.markdown(f'<p style="color: #d32f2f; text-align: center; font-weight: bold; margin-top:20px;">{t["exp_text"]}</p>', unsafe_allow_html=True)

# --- 5. CORPS DE L'APPLI ---
st.markdown(f"<h1 style='text-align: center;'>{t['welcome']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #d32f2f; font-weight: bold;'>👨‍💻 Alpha Balde | {t['exp_text']}</p>", unsafe_allow_html=True)

if uploaded_file:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    with st.spinner("Analyse en cours..."):
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "".join([p.extract_text() for p in reader.pages])

        # Vérification État
        check_res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Return ONLY the US State name: {pdf_text[:1000]}"}])
        detected_state = check_res.choices[0].message.content.strip()

        if detected_state.lower() not in selected_state.lower():
            st.error(f"⚠️ Incohérence État : Document={detected_state} / Sélection={selected_state}")
            st.stop()

        # Analyse
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": f"Expert bancaire en {selected_state}."}, {"role": "user", "content": f"Analyse : {pdf_text}"}]
        )
        report_text = response.choices[0].message.content
        
        addr_res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Return ONLY the physical address: {pdf_text}"}])
        address = addr_res.choices[0].message.content.strip()

    # --- AFFICHAGE DES LIENS DANS LA SIDEBAR ---
    q = urllib.parse.quote(f"{address}, {selected_state}")
    with comps_container:
        st.markdown(f"### 🔍 {t['comps_label']}")
        st.markdown(f'<a href="https://www.zillow.com/homes/{q}_rb/" target="_blank" class="external-link">🏠 Zillow</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="https://www.trulia.com/search/{q}" target="_blank" class="external-link">🌳 Trulia</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="https://www.redfin.com/whereonearth?search_location={q}" target="_blank" class="external-link">🚩 Redfin</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="https://www.homes.com/search/?q={q}" target="_blank" class="external-link">🏘️ Homes.com</a>', unsafe_allow_html=True)

    # --- DASHBOARD ---
    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    k1.metric("State", selected_state)
    k2.metric("Address", address[:20] + "...")
    k3.metric(t['max_bid_label'], f"${max_bid:,.0f}")

    col1, col2 = st.columns([1, 1.3], gap="large")
    with col1:
        st.subheader("📸 Property")
        if "MAPS_API_KEY" in st.secrets:
            st.image(f"https://maps.googleapis.com/maps/api/streetview?size=600x400&location={q}&key={st.secrets['MAPS_API_KEY']}")
    with col2:
        st.subheader(f"📄 {t['analysis_header']}")
        st.markdown(f'<div class="report-card">{report_text}</div>', unsafe_allow_html=True)
        pdf_data = create_pdf(address, report_text, selected_state, selected_lang, max_bid)
        st.download_button(f"📥 {t['save_btn']}", pdf_data, f"Report_{selected_state}.pdf")

else:
    st.info(t['landing_msg'])

st.markdown("<br><hr><center>© 2025 Alpha Balde</center>", unsafe_allow_html=True)
