import streamlit as st
import requests

# CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="Fonozis")
st.title("🎸 Fonozis: HQ")

# URL DIRECTA (Asegúrate de que este ID sea el correcto de tu proyecto en Supabase)
# Copia este ID desde el panel de Supabase: Project Settings > API
PROJECT_ID = "yzwwstvzqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"

st.write(f"Conectando a: {BASE_URL}")

# PRUEBA DE CONEXIÓN SIMPLE
try:
    # Intentamos conectar a la API REST de Supabase
    response = requests.get(f"{BASE_URL}/rest/v1/", timeout=5)
    st.write(f"Respuesta del servidor: {response.status_code}")
    
    if response.status_code == 200:
        st.success("¡Conexión exitosa con Supabase!")
    else:
        st.error(f"El servidor respondió con código: {response.status_code}")
except Exception as e:
    st.error("No se pudo conectar al servidor. Revisa si el ID del proyecto es correcto.")
    st.code(str(e))
