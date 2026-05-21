import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# URL y KEY FIJAS (Sin usar secrets.toml)
BASE_URL = "https://yzwwstvzqjtaaoqxbwtz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZ6cWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTY2MjA5MTMsImV4cCI6MjAzMjE5NjkxM30.XZJbDd4TRwCOzAB3IabHYFbyN4fZ53i1gKpjGTimJgg"

st.set_page_config(page_title="Fonozis", layout="centered")

headers_api = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

st.title("🎸 Fonozis: HQ")

# Prueba simple de conexión
try:
    res = requests.get(f"{BASE_URL}/rest/v1/mensajes", headers=headers_api)
    if res.status_code == 200:
        st.success("¡Conexión establecida!")
    else:
        st.error(f"Error de conexión: {res.status_code} - {res.text}")
except Exception as e:
    st.error(f"Fallo crítico: {str(e)}")
