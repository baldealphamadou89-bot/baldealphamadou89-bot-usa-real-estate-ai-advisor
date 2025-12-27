import streamlit as st
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="USA Real Estate AI (OpenAI)", page_icon="🏠", layout="wide")

# Récupération de la nouvelle clé
openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

if openai_key:
    client = OpenAI(api_key=openai_key)

# --- ZONE PRINCIPALE ---
st.title("🇺🇸 USA Real Estate AI Advisor (Powered by GPT-4o)")

if not openai_key:
    st.warning("👈 Veuillez ajouter votre clé OPENAI_API_KEY dans les secrets.")
else:
    with st.sidebar:
        st.header("📋 Options")
        selected_state = st.selectbox("État US", ["Pennsylvania", "Florida", "New York"])
        uploaded_file = st.file_uploader("Charger le PDF d'enchère", type="pdf")

    if uploaded_file:
        with st.spinner("Analyse par GPT-4o en cours..."):
            # Note: Pour OpenAI, on extrait le texte du PDF car GPT-4o 
            # préfère le texte direct ou les images.
            import PyPDF2
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text()

            # 1. Extraction Adresse
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es un expert immobilier US."},
                    {"role": "user", "content": f"Donne l'adresse uniquement : {pdf_text}"}
                ]
            )
            address = response.choices[0].message.content
            st.success(f"📍 Adresse : {address}")

            # 2. Analyse Financière
            # On demande l'analyse des dettes comme vous le faisiez chez Ecobank
            report_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": f"Analyse ces dettes et calcule le Max Bid (70% rule) pour cet immeuble en {selected_state}: {pdf_text}"}
                ]
            )
            st.markdown(report_res.choices[0].message.content)
