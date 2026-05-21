import streamlit as st
import requests
from datetime import datetime

# CONFIGURACIÓN
PROJECT_ID = "yzwwstvzqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"
# PEGA AQUÍ TU CLAVE ANON QUE COPIASTE DE SUPABASE (LA QUE EMPIEZA POR eyJ...)
SUPABASE_KEY = "TU_CLAVE_ANON" 

st.set_page_config(page_title="Fonozis", page_icon="🎸")
st.title("🎸 Fonozis: Caja de Audios")

# --- 1. SUBIDA DE ARCHIVOS ---
archivo = st.file_uploader("Sube un audio para la banda", type=["mp3", "wav"])

if archivo and st.button("Subir archivo"):
    # Nombre único para el archivo
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.name.replace(' ', '_')}"
    url_subida = f"{BASE_URL}/storage/v1/object/audios/{filename}"
    
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Content-Type": archivo.type
    }
    
    with st.spinner('Subiendo archivo...'):
        res = requests.post(url_subida, headers=headers, data=archivo.getvalue())
        
    if res.status_code == 200:
        st.success("¡Archivo subido con éxito!")
        st.rerun() # Recargamos para ver el nuevo archivo
    else:
        st.error(f"Error al subir: {res.status_code} - {res.text}")

# --- 2. LISTAR ARCHIVOS ---
st.divider()
st.subheader("Audios Disponibles")

url_listado = f"{BASE_URL}/storage/v1/object/list/audios"
headers = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "apikey": SUPABASE_KEY
}

try:
    res_list = requests.post(url_listado, headers=headers, json={"prefix": ""})
    
    if res_list.status_code == 200:
        archivos = res_list.json()
        if archivos:
            # Mostramos los más nuevos primero
            for f in reversed(archivos):
                file_url = f"{BASE_URL}/storage/v1/object/public/audios/{f['name']}"
                with st.container():
                    st.audio(file_url)
                    st.caption(f"Archivo: {f['name']}")
                    st.write("---")
        else:
            st.info("La caja está vacía. ¡Sube el primer audio!")
    else:
        st.warning("No se pudieron cargar los audios. Verifica tu conexión.")
except Exception as e:
    st.error(f"Error al conectar con el servidor: {e}")
