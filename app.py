import streamlit as st
import requests
from datetime import datetime

# CONFIGURACIÓN
PROJECT_ID = "yzwwstvzqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"
# Asegúrate de usar tu clave 'anon' pública aquí
SUPABASE_KEY = "PEGA_AQUÍ_TU_CLAVE_ANON" 

st.title("🎸 Fonozis: Caja de Audios")

# UPLOAD
archivo = st.file_uploader("Sube un audio para la banda", type=["mp3", "wav"])

if archivo and st.button("Subir archivo"):
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.name}"
    url_subida = f"{BASE_URL}/storage/v1/object/audios/{filename}"
    
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Content-Type": archivo.type
    }
    
    res = requests.post(url_subida, headers=headers, data=archivo.getvalue())
    if res.status_code == 200:
        st.success("¡Archivo subido!")
        st.rerun()
    else:
        st.error(f"Error al subir: {res.status_code}")

# LISTAR ARCHIVOS (esto es un truco simple para listar)
st.subheader("Audios Disponibles")
# Nota: La forma más fácil de verlos es listar tu bucket en la web de Supabase
st.info("Revisa la pestaña Storage en Supabase para ver la lista completa de archivos.")
