import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZycWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMTc2NTUsImV4cCI6MjA5NDg5MzY1NX0.XZJbD4TRwC0rAB3IabHYFbyN4fZ53i1gKpjGtImJjgg"
st.set_page_config(page_title="Fonozis", page_icon="🎸")

st.title("🎸 Fonozis: HQ de la Banda")

# --- INTERFAZ ---
st.subheader("Capturar nueva idea")

# Instrucción clara para que el usuario sepa qué hacer al tocar el botón
st.warning("⚠️ **Instrucción para el celular:** Al tocar 'Upload', elige 'Grabar' o 'Tomar audio' para crear una nueva nota de voz.")

archivo = st.file_uploader(
    "Selecciona o graba tu idea (MP3/WAV)", 
    type=["mp3", "wav", "m4a"], 
    accept_multiple_files=False
)

etiqueta = st.text_input("Etiqueta de la idea (ej: Riff Intro):")

if archivo and st.button("Publicar en la banda"):
    # Limpiamos el nombre del archivo para que sea compatible con la web
    prefijo = etiqueta.replace(' ', '_') if etiqueta else "Idea"
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{prefijo}.mp3"
    
    url_subida = f"{BASE_URL}/storage/v1/object/audios/{filename}"
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
    
    with st.spinner('Publicando en el servidor...'):
        res = requests.post(url_subida, headers=headers, data=archivo.getvalue())
        
    if res.status_code == 200:
        st.success("¡Audio publicado correctamente!")
        st.rerun()
    else:
        st.error("Error al subir el archivo. Revisa los permisos en Supabase.")

st.divider()

# --- BIBLIOTECA ---
st.subheader("Biblioteca de Ideas")
res_list = requests.post(f"{BASE_URL}/storage/v1/object/list/audios", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})

if res_list.status_code == 200:
    audios = sorted(res_list.json(), key=lambda x: x['name'], reverse=True)
    for f in audios:
        file_url = f"{BASE_URL}/storage/v1/object/public/audios/{f['name']}"
        nombre_limpio = f['name'].split('_', 1)[-1].replace('.mp3', '').replace('_', ' ')
        with st.expander(f"🎵 {nombre_limpio}"):
            st.audio(file_url)
