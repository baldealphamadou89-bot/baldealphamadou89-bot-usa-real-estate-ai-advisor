import streamlit as st
from openai import OpenAI
import PyPDF2
import requests
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="USA Real Estate AI (OpenAI)", page_icon="🏠", layout="wide")

# Récupération de la clé OpenAI dans les Secrets
openai_key = st.secrets.get("OPENAI_API_KEY")
maps_key = st.secrets.get("MAPS_API_KEY")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("⚙️ Configuration")
    if not openai_key:
        openai_key = st.text_input("Entrez votre OpenAI API Key", type="password")
    else:
        st.success("✅ Clé OpenAI chargée")
    
    selected_state = st.selectbox("État US", ["Pennsylvania", "Florida", "New Jersey", "New York"])
    uploaded_file = st.file_uploader("Charger le PDF d'enchère", type="pdf")

# --- ZONE PRINCIPALE ---
st.title("🏠 USA Real Estate Investment Advisor")
st.caption("Expertise Bancaire (ex-Ecobank) + Analyse GPT-4o")

if not openai_key:
    st.warning("👈 Veuillez configurer votre clé API OpenAI.")
elif uploaded_file:
    client = OpenAI(api_key=openai_key)
    
    with st.spinner("Analyse par GPT-4o en cours..."):
        try:
            # 1. Extraction du texte du PDF
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text()

            # 2. Analyse par GPT-4o
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"Tu es un expert immobilier aux USA spécialisé dans les enchères en {selected_state}."},
                    {"role": "user", "content": f"Analyse ce texte de document d'enchère. Extrais l'adresse, liste les dettes et risques, et calcule le Max Bid (règle des 70%) : \n\n{pdf_text}"}
                ]
            )
            
            resultat = response.choices[0].message.content
            st.markdown(resultat)

        except Exception as e:
            st.error(f"Erreur : {e}")
