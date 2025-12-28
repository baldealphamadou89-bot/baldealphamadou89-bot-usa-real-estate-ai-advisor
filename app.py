import streamlit as st
from openai import OpenAI
import PyPDF2
from fpdf import FPDF
import base64
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Alpha Balde | Real Estate AI", page_icon="🏠", layout="wide")

openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def create_pdf(address, analysis_text, state, lang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    title = f"Investment Report - {state}"
    pdf.cell(200, 10, title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Property: {address}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    clean_text = analysis_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- TRADUCTIONS ---
languages = {
    "English": {"welcome": "USA Real Estate AI Advisor", "state_label": "Select State", "upload": "Upload PDF", "save": "📥 Save PDF"},
    "Français": {"welcome": "USA Real Estate AI Advisor", "state_label": "Choisir l'État", "upload": "Charger le PDF", "save": "📥 Sauvegarder PDF"},
    "Español": {"welcome": "USA Real Estate AI Advisor", "state_label": "Seleccionar Estado", "upload": "Cargar PDF", "save": "📥 Guardar PDF"}
}

# --- SIDEBAR : LANGUE & ÉTATS ---
selected_lang = st.sidebar.selectbox("🌐 Language", ["English", "Français", "Español"])
t = languages[selected_lang]

# Réintégration de la liste des États demandés
states_list = ["New York", "New Jersey", "Pennsylvania", "California", "Florida", "Texas", "Maryland"]
selected_state = st.sidebar.selectbox(t['state_label'], states_list)

# --- EN-TÊTE AVEC LOGO ---
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
    st.subheader(f"👨‍💻 Alpha Balde | Expert Bancaire (Ex-Ecobank)")

st.divider()

# --- ANALYSE ---
uploaded_file = st.sidebar.file_uploader(t['upload'], type="pdf")

if uploaded_file:
    client = OpenAI(api_key=openai_key)
    with st.spinner(f"Analyse des spécificités juridiques pour {selected_state}..."):
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "".join([p.extract_text() for p in reader.pages])

        # Analyse IA incluant l'État sélectionné
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Expert bancaire Ecobank. Analyse selon les lois de {selected_state}. Réponds en {selected_lang}."},
                {"role": "user", "content": f"Analyse les dettes et risques pour cette propriété située dans l'État de {selected_state} : {pdf_text}"}
            ]
        )
        report = response.choices[0].message.content
        
        # Extraction adresse
        addr_res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Return ONLY the address: {pdf_text}"}]
        )
        address = addr_res.choices[0].message.content.strip()

        st.success(f"📍 {address} ({selected_state})")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("👁️ Street View")
            if maps_key:
                st.image(f"https://maps.googleapis.com/maps/api/streetview?size=600x400&location={address}, {selected_state}&key={maps_key}")

        with c2:
            st.subheader(f"📄 Analyse ({selected_state})")
            st.markdown(report)
            
            # Bouton PDF
            pdf_data = create_pdf(address, report, selected_state, selected_lang)
            st.download_button(label=t['save'], data=pdf_data, file_name=f"Report_{selected_state}.pdf", mime="application/pdf")

st.markdown(f'<div style="text-align: center; margin-top: 50px; color: grey;">© 2025 Alpha Balde | Banking & AI Expertise</div>', unsafe_allow_html=True)
