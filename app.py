import streamlit as st
from openai import OpenAI
import PyPDF2
from fpdf import FPDF
import base64
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Alpha Balde | Real Estate AI", page_icon="🏠", layout="wide")

# --- 2. STYLE CSS ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-top: 4px solid #d32f2f; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .roi-card { background-color: #fff3f3; padding: 20px; border-radius: 15px; border: 2px dashed #d32f2f; text-align: center; }
    .report-card { background-color: white; padding: 25px; border-radius: 15px; border-left: 6px solid #d32f2f; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

def get_base64_logo(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def create_pdf(address, analysis, state, max_bid, lang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Expert Analysis - {state}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(211, 47, 47)
    pdf.cell(200, 10, f"MAX BID LIMIT (70% Rule): ${max_bid:,.2f}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    clean_text = analysis.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. SIDEBAR & LOGO ---
with st.sidebar:
    logo_data = get_base64_logo("logo.png.jpeg")
    if logo_data:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{logo_data}" width="130"></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    selected_lang = st.selectbox("🌐 Language", ["English", "Français", "Español"])
    states_list = ["New York", "New Jersey", "Pennsylvania", "California", "Florida", "Texas", "Maryland"]
    selected_state = st.selectbox("📍 State", states_list)
    
    st.markdown("### 💰 Financial Inputs")
    arv = st.number_input("Estimated ARV ($)", min_value=0, value=100000, step=5000)
    repairs = st.number_input("Estimated Repairs ($)", min_value=0, value=20000, step=1000)
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload Auction PDF", type="pdf")

# --- 4. CALCUL DE LA RÈGLE DES 70% ---
max_bid = (arv * 0.70) - repairs

# --- 5. CORPS DE L'APPLI ---
st.title("USA Real Estate AI Advisor")
st.subheader("👨‍💻 Alpha Balde | Expert Bancaire (Ex-Ecobank)")

if uploaded_file:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    with st.spinner("Analyse et calcul de rentabilité..."):
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "".join([p.extract_text() for p in reader.pages])

        # Analyse IA
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Expert bancaire. Réponds en {selected_lang}. Analyse les risques pour {selected_state}."},
                {"role": "user", "content": f"Analyse ce document. L'investisseur suit la règle des 70%. Son ARV est de {arv}$ et les travaux {repairs}$. Son enchère max est {max_bid}$. Commente la viabilité : {pdf_text}"}
            ]
        )
        report_text = response.choices[0].message.content
        
        # Extraction adresse
        addr_res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Return ONLY the address."}]
        )
        address = addr_res.choices[0].message.content.strip()

    # --- AFFICHAGE DES RÉSULTATS ---
    st.markdown("---")
    
    # KPIs Financiers
    c1, c2, c3 = st.columns(3)
    c1.metric("ARV (Value)", f"${arv:,}")
    c2.metric("Repairs Cost", f"-${repairs:,}")
    with c3:
        st.markdown(f"""
            <div class="roi-card">
                <p style="margin:0; font-size:0.9em; color:#d32f2f;">MAX BID (70% RULE)</p>
                <h2 style="margin:0; color:#d32f2f;">${max_bid:,.0f}</h2>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.3])
    
    with col_left:
        st.subheader("📸 Property View")
        if "MAPS_API_KEY" in st.secrets:
            st.image(f"https://maps.googleapis.com/maps/api/streetview?size=600x400&location={address}&key={st.secrets['MAPS_API_KEY']}")
        
    with col_right:
        st.subheader("📄 Expert Analysis")
        st.markdown(f'<div class="report-card">{report_text}</div>', unsafe_allow_html=True)
        
        # Bouton PDF
        pdf_data = create_pdf(address, report_text, selected_state, max_bid, selected_lang)
        st.download_button("📥 Download Report with ROI", data=pdf_data, file_name="Alpha_Balde_Analysis.pdf")

else:
    st.info("👋 Bienvenue Alpha. Entrez les données financières à gauche et chargez un PDF pour calculer votre enchère maximale.")

st.markdown("<br><hr><center>© 2025 Alpha Balde | Real Estate Intelligence</center>", unsafe_allow_html=True)
