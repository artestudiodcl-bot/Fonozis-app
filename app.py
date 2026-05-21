import streamlit as st

# Carga segura desde los Secrets
BASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

# Ejemplo de cómo usarla en tus llamadas a la API
headers_api = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}
