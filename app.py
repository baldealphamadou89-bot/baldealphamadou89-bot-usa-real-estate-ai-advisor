import streamlit as st
from openai import OpenAI
import PyPDF2
from fpdf import FPDF
import base64
import requests

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Alpha Balde | Real Estate AI", page_icon="🏠", layout="wide")

openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

# --- FONCTION POUR LE LOGO (INFAILLIBLE) ---
def get_base64_image(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return None

# URL de votre logo (Maison + Clés)
LOGO_URL = "https://raw.githubusercontent.com/BaldeAlpha/public-images/main/house_keys_final.png"
logo_base64 = get_base64_image("https://img.freepik.com/vecteurs-premium/cle-maison-concept-immobilier_24877-21141.jpg")

# --- FONCTION GÉNÉRATION PDF ---
def create_pdf(address, analysis_text, lang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    title = "Real Estate Report" if lang == "English" else "Rapport Immobilier"
    pdf.cell(200, 10, title, ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Address: {address}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    clean_text = analysis_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- TRADUCTIONS ---
languages = {
    "English": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Developed by Alpha Balde",
        "exp": "Banking Expert (Ex-Ecobank)",
        "save_btn": "📥 Download Analysis Report (PDF)",
        "analysis_title": "Financial & Legal Analysis"
    },
    "Français": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Développé par Alpha Balde",
        "exp": "Expert Bancaire (Ex-Ecobank)",
        "save_btn": "📥 Télécharger le Rapport d'Analyse (PDF)",
        "analysis_title": "Analyse Financière & Juridique"
    }
}

selected_lang = st.sidebar.selectbox("🌐 Language", ["English", "Français"])
t = languages[selected_lang]

# --- EN-TÊTE ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if logo_base64:
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" width="150">', unsafe_allow_html=True)
    else:
        st.write("🏠") # Fallback si l'image échoue

with col_title:
    st.title(t['welcome'])
    st.subheader(f"👨‍💻 {t['dev_by']} | 🏦 {t['exp']}")

st.divider()

# --- ANALYSE ---
uploaded_file = st.sidebar.file_uploader("Upload Auction PDF", type="pdf")

if uploaded_file:
    client = OpenAI(api_key=openai_key)
    with st.spinner("Analyse en cours..."):
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "".join([p.extract_text() for p in reader.pages])

        addr_res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Return ONLY the address: {pdf_text}"}]
        )
        address = addr_res.choices[0].message.content.strip()
        st.info(f"📍 **{address}**")

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
                          {"role": "user", "content": f"Analyze debts and risks: {pdf_text}"}]
            )
            report_text = analysis.choices[0].message.content
            st.markdown(report_text)

            # BOUTON DE TÉLÉCHARGEMENT PDF
            st.divider()
            pdf_data = create_pdf(address, report_text, selected_lang)
            st.download_button(
                label=t["save_btn"],
                data=pdf_data,
                file_name=f"Alpha_Balde_Analysis.pdf",
                mime="application/pdf"
            )

st.markdown(f'<div style="text-align: center; margin-top: 50px; color: grey;">© 2025 Alpha Balde | AI & Banking Expertise</div>', unsafe_allow_html=True)
