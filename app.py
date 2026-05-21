import streamlit as st
import requests

# HARDCODEAMOS LOS DATOS AQUÍ (SOLO PARA PROBAR)
# ¡CUIDADO! Esto es solo para verificar que conecta.
BASE_URL = "https://yzwwstvzqjtaaoqxbwtz.supabase.co"
SUPABASE_KEY = "PEGA_AQUÍ_TU_CLAVE_ANON_COMPLETA"

st.title("🎸 Fonozis: HQ - Test de Conexión")

headers_api = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Intentamos leer la tabla de mensajes
try:
    res = requests.get(f"{BASE_URL}/rest/v1/mensajes", headers=headers_api)
    st.write(f"Estado de conexión: {res.status_code}")
    if res.status_code == 200:
        st.success("¡CONECTADO CON ÉXITO!")
        st.write(res.json())
    else:
        st.error(f"Error 401/Otros: {res.text}")
except Exception as e:
    st.error(f"Error crítico: {e}")
