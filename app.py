import streamlit as st
from openai import OpenAI
import PyPDF2
from fpdf import FPDF
import requests

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Alpha Balde | Real Estate AI", page_icon="🏠", layout="wide")

openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

# --- FONCTION GÉNÉRATION PDF ---
def create_pdf(address, analysis_text, lang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    title = "Real Estate Investment Report" if lang == "English" else "Rapport d'Investissement Immobilier"
    pdf.cell(200, 10, title, ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Address: {address}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    # Nettoyage des caractères spéciaux pour le PDF
    clean_text = analysis_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    
    return pdf.output(dest='S').encode('latin-1')

# --- DICTIONNAIRE MULTILINGUE ---
languages = {
    "English": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Developed by Alpha Balde",
        "objective": "This platform combines AI (GPT-4o) and banking expertise to analyze US real estate auctions.",
        "save_btn": "📥 Download Analysis Report (PDF)",
        "analysis_title": "Financial & Legal Analysis",
        "sidebar_title": "Settings"
    },
    "Français": {
        "welcome": "USA Real Estate AI Advisor",
        "dev_by": "Développé par Alpha Balde",
        "objective": "Cette plateforme combine l'IA (GPT-4o) et l'expertise bancaire pour analyser les enchères immobilières aux USA.",
        "save_btn": "📥 Télécharger le Rapport d'Analyse (PDF)",
        "analysis_title": "Analyse Financière & Juridique",
        "sidebar_title": "Paramètres"
    }
}

# --- SÉLECTION DE LA LANGUE ---
selected_lang = st.sidebar.selectbox("🌐 Language", ["English", "Français"])
t = languages[selected_lang]

# --- EN-TÊTE AVEC VOTRE LOGO (Image des clés fournie) ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    # Utilisation d'un lien direct vers l'image des clés
    st.image("https://i.ibb.co/L6V2MvL/house-keys.png", width=150) # Lien alternatif vers image de clés

with col_title:
    st.title(t['welcome'])
    st.subheader(f"👨‍💻 {t['dev_by']}")

st.markdown(f'<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b;">{t["objective"]}</div>', unsafe_allow_html=True)
st.divider()

# --- LOGIQUE D'ANALYSE ---
uploaded_file = st.sidebar.file_uploader(t["sidebar_title"], type="pdf")

if uploaded_file:
    client = OpenAI(api_key=openai_key)
    with st.spinner("Analyzing..."):
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "".join([p.extract_text() for p in reader.pages])

        # Extraction adresse
        addr_res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Return ONLY the physical address: {pdf_text}"}]
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
                          {"role": "user", "content": f"Analyze debts and liens from this text: {pdf_text}"}]
            )
            report_text = analysis.choices[0].message.content
            st.markdown(report_text)

            # --- LE BOUTON DE TÉLÉCHARGEMENT PDF ---
            st.divider()
            try:
                pdf_data = create_pdf(address, report_text, selected_lang)
                st.download_button(
                    label=t["save_btn"],
                    data=pdf_data,
                    file_name=f"Expertise_{address.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error generating PDF: {e}")

# --- PIED DE PAGE ---
st.markdown(f'<div style="text-align: center; margin-top: 50px; color: grey; font-size: 0.8em;">© 2025 Alpha Balde | AI & Banking Expertise</div>', unsafe_allow_html=True)
