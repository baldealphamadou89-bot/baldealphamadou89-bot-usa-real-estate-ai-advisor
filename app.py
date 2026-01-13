import streamlit as st
from openai import OpenAI
import PyPDF2
from fpdf import FPDF
import base64
import os
import urllib.parse
import json
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. DATABASE & CONFIG ---
st.set_page_config(page_title="Alpha Balde | Real Estate AI", page_icon="🏢", layout="wide")

def init_db():
    conn = sqlite3.connect('alpha_invest_vault.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS deals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, address TEXT, state TEXT, max_bid REAL, roi REAL, risk_level TEXT)''')
    conn.commit()
    conn.close()

def save_deal(address, state, max_bid, roi, risk):
    conn = sqlite3.connect('alpha_invest_vault.db')
    c = conn.cursor()
    c.execute("INSERT INTO deals (date, address, state, max_bid, roi, risk_level) VALUES (?, ?, ?, ?, ?, ?)",
              (datetime.now().strftime("%Y-%m-%d %H:%M"), address, state, max_bid, roi, risk))
    conn.commit()
    conn.close()

init_db()

# --- 2. CSS FIX (FORCE VISIBILITÉ) ---
st.markdown("""
    <style>
    /* Fix pour les metrics illisibles */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #1e1e1e !important;
    }
    .stMetric {
        background-color: #ffffff !important;
        padding: 15px;
        border-radius: 10px;
        border-bottom: 5px solid #d32f2f;
    }
    .report-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 6px solid #d32f2f; color: #1e1e1e; }
    h1, h2, h3 { color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. UI AVEC ONGLETS ---
st.title("Conseiller en IA pour l'immobilier")
st.markdown(f"👨‍💻 **Alpha Balde** | Ancien employé de banque (Ecobank Guinée)")

# Création explicite des onglets
tab1, tab2 = st.tabs(["🚀 Analyseur de Deal", "📜 Historique"])

with tab1:
    with st.sidebar:
        st.header("Paramètres")
        selected_lang = st.selectbox("Langue", ["Français", "English", "Español"])
        selected_state = st.selectbox("État", ["New York", "New Jersey", "Florida", "California", "Texas"])
        arv = st.number_input("After Repair Value ($)", value=250000)
        repairs = st.number_input("Travaux ($)", value=40000)
        max_bid = (arv * 0.70) - repairs
        
        uploaded_file = st.file_uploader("Charger le PDF d'enchère", type="pdf")

    if uploaded_file:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        with st.spinner("Analyse en cours..."):
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = "".join([p.extract_text() for p in reader.pages])
            
            # Analyse simplifiée pour la démo
            address = "Détection en cours..." # Simulation ou appel API
            roi = 15.5 # Simulation
            risk = "Low"
            
            # Rapport
            report_text = "Analyse détaillée générée par l'IA d'Alpha Balde..."
            
            save_deal(address, selected_state, max_bid, roi, risk)
            
            st.success("Analyse terminée !")
            col1, col2 = st.columns(2)
            col1.metric("Offre Max", f"${max_bid:,.0f}")
            col2.metric("ROI Est.", f"{roi}%")
            
            st.markdown(f'<div class="report-card">{report_text}</div>', unsafe_allow_html=True)
    else:
        st.info("Veuillez charger un document PDF pour commencer.")

with tab2:
    st.header("Historique des dossiers")
    conn = sqlite3.connect('alpha_invest_vault.db')
    df = pd.read_sql_query("SELECT * FROM deals", conn)
    conn.close()
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("Aucun historique pour le moment.")


