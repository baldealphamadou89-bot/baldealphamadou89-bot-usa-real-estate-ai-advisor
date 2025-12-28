import streamlit as st
from openai import OpenAI
import PyPDF2
from fpdf import FPDF
import base64
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Alpha Balde | Real Estate AI Advisor", page_icon="🏠", layout="wide")

# --- RÉCUPÉRATION DES CLÉS (Secrets Streamlit) ---
openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

# --- GESTION DU LOGO ---
# Cette fonction permet d'afficher votre logo local "logo.png.jpeg" 
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- GÉNÉRATION DU PDF DE SORTIE ---
def create_pdf(address, analysis_text, lang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    title = "Investment Analysis" if lang == "English" else ("Rapport d'Analyse" if lang == "Français" else "Informe de Análisis")
    pdf.cell(200, 10, title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Property: {address}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    clean_text = analysis_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- DICTIONNAIRE MULTILINGUE ---
languages = {
    "English": {
        "welcome": "USA Real Estate AI Advisor",
        "dev": "Developed by Alpha Balde | Banking Expert (Ex-Ecobank)",
        "obj": "AI-driven analysis of US real estate auctions for secure investment.",
        "upload": "Upload Auction PDF",
        "analysis": "Financial & Legal Analysis",
        "save": "📥 Save Report (PDF)"
    },
    "Français": {
        "welcome": "USA Real Estate AI Advisor",
        "dev": "Développé par Alpha Balde | Expert Bancaire (Ex-Ecobank)",
        "obj": "Analyse par IA des enchères immobilières aux USA pour sécuriser vos investissements.",
        "upload": "Charger le PDF d'enchère",
        "analysis": "Analyse Financière & Juridique",
        "save": "📥 Sauvegarder le Rapport (PDF)"
    },
    "Español": {
        "welcome": "USA Real Estate AI Advisor",
        "dev": "Desarrollado por Alpha Balde | Experto Bancario (Ex-Ecobank)",
        "obj": "Análisis por IA de subastas inmobiliarias en EE. UU. para inversiones seguras.",
        "upload": "Cargar PDF de la subasta",
        "analysis": "Análisis Financiero y Legal",
        "save": "📥 Guardar Informe (PDF)"
    }
}

# --- SIDEBAR & LANGUE ---
selected_lang = st.sidebar.selectbox("🌐 Language / Langue / Idioma", ["English", "Français", "Español"])
t = languages[selected_lang]

# --- AFFICHAGE DU LOGO ET TITRE ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    logo_path = "logo.png.jpeg"
    if os.path.exists(logo_path):
        bin_str = get_base64_of_bin_file(logo_path)
        st.markdown(f'<img src="data:image/jpeg;base64,{bin_str}" width="150">', unsafe_allow_html=True)
    else:
        st.title("🏠")

with col_title:
    st.title(t['welcome'])
    st.subheader(f"👨‍💻 {t['dev']}")

st.info(t['obj'])
st.divider()

# --- LOGIQUE PRINCIPALE ---
uploaded_file = st.sidebar.file_uploader(t['upload'], type="pdf")

if uploaded_file:
    client = OpenAI(api_key=openai_key)
    with st.spinner("Analyse multicritère..."):
        # 1. Lecture PDF
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "".join([p.extract_text() for p in reader.pages])

        # 2. Analyse IA
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Expert analyst at Ecobank. Reply in {selected_lang}."},
                {"role": "user", "content": f"Extract address and analyze liens/risks: {pdf_text}"}
            ]
        )
        report = response.choices[0].message.content
        
        # 3. Extraction de l'adresse pour Street View
        addr_res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Return ONLY the physical address: {pdf_text}"}]
        )
        address = addr_res.choices[0].message.content.strip()

        # 4. Affichage
        st.success(f"📍 {address}")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("👁️ Street View")
            if maps_key:
                st.image(f"https://maps.googleapis.com/maps/api/streetview?size=600x400&location={address}&key={maps_key}")
            else:
                st.warning("Maps API key missing.")

        with c2:
            st.subheader(f"📄 {t['analysis']}")
            st.markdown(report)
            
            # Bouton de sauvegarde
            pdf_data = create_pdf(address, report, selected_lang)
            st.download_button(label=t['save'], data=pdf_data, file_name=f"Report_{address}.pdf", mime="application/pdf")

st.markdown(f'<div style="text-align: center; margin-top: 50px; color: grey;">© 2025 Alpha Balde | Banking & AI Expertise</div>', unsafe_allow_html=True)
