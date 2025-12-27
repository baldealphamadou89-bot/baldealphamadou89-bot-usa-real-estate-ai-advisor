import streamlit as st
from openai import OpenAI
import PyPDF2
from fpdf import FPDF
import base64
import requests
from io import BytesIO

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Alpha Balde | Real Estate AI", page_icon="🏠", layout="wide")

openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

# --- FONCTION POUR LE LOGO (MÉTHODE INFAILLIBLE) ---
def get_base64_logo():
    # Lien direct vers l'image de la maison rouge et des clés que vous avez fournie
    url = "https://img.freepik.com/vecteurs-premium/cle-maison-concept-immobilier_24877-21141.jpg"
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return None

logo_b64 = get_base64_logo()

# --- FONCTION GÉNÉRATION PDF ---
def create_pdf(address, analysis_text, lang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    title = "Real Estate Report" if lang == "English" else "Rapport Immobilier" if lang == "Français" else "Informe Inmobiliario"
    pdf.cell(200, 10, title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Address: {address}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    # Nettoyage des caractères spéciaux
    clean_text = analysis_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- TRADUCTIONS (INCLUANT L'ESPAGNOL) ---
languages = {
    "English": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Developed by Alpha Balde",
        "exp": "Banking Expert (Ex-Ecobank)",
        "save_btn": "📥 Download Analysis Report (PDF)",
        "analysis_title": "Financial & Legal Analysis",
        "obj": "This platform combines AI (GPT-4o) and banking expertise to analyze US real estate auctions."
    },
    "Français": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Développé par Alpha Balde",
        "exp": "Expert Bancaire (Ex-Ecobank)",
        "save_btn": "📥 Télécharger le Rapport d'Analyse (PDF)",
        "analysis_title": "Analyse Financière & Juridique",
        "obj": "Cette plateforme combine l'IA (GPT-4o) et l'expertise bancaire pour analyser les enchères immobilières aux USA."
    },
    "Español": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Desarrollado por Alpha Balde",
        "exp": "Experto Bancario (Ex-Ecobank)",
        "save_btn": "📥 Descargar Informe de Análisis (PDF)",
        "analysis_title": "Análisis Financiero y Legal",
        "obj": "Esta plataforma combina IA (GPT-4o) y experiencia bancaria para analizar subastas inmobiliarias en EE. UU."
    }
}

# --- SÉLECTION DE LA LANGUE ---
selected_lang = st.sidebar.selectbox("🌐 Language / Langue / Idioma", ["English", "Français", "Español"])
t = languages[selected_lang]

# --- EN-TÊTE ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="180">', unsafe_allow_html=True)
    else:
        st.title("🏠")

with col_title:
    st.title(t['welcome'])
    st.subheader(f"👨‍💻 {t['dev_by']} | 🏦 {t['exp']}")

st.info(t['obj'])
st.divider()

# --- LOGIQUE D'ANALYSE ---
uploaded_file = st.sidebar.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    client = OpenAI(api_key=openai_key)
    with st.spinner("Processing..."):
        # Extraction Texte
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "".join([p.extract_text() for p in reader.pages])

        # Extraction Adresse
        addr_res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Return ONLY the address: {pdf_text}"}]
        )
        address = addr_res.choices[0].message.content.strip()
        st.success(f"📍 **{address}**")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📸 Street View")
            if maps_key:
                st.image(f"https://maps.googleapis.com/maps/api/streetview?size=600x400&location={address}&key={maps_key}")

        with c2:
            st.subheader(f"📄 {t['analysis_title']}")
            analysis = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": f"Reply in {selected_lang}"},
                          {"role": "user", "content": f"Analyze debts and liens: {pdf_text}"}]
            )
            report_text = analysis.choices[0].message.content
            st.markdown(report_text)

            # --- BOUTON DE TÉLÉCHARGEMENT PDF ---
            st.divider()
            pdf_data = create_pdf(address, report_text, selected_lang)
            st.download_button(
                label=t["save_btn"],
                data=pdf_data,
                file_name=f"Expertise_Alpha_Balde.pdf",
                mime="application/pdf"
            )

# --- PIED DE PAGE ---
st.markdown(f'<div style="text-align: center; margin-top: 50px; color: grey; font-size: 0.8em;">© 2025 Alpha Balde | AI & Banking Expertise</div>', unsafe_allow_html=True)
