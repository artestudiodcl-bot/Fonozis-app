import streamlit as st
import requests
from datetime import datetime

# Configuración básica
PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZycWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMTc2NTUsImV4cCI6MjA5NDg5MzY1NX0.XZJbD4TRwC0rAB3IabHYFbyN4fZ53i1gKpjGtImJjgg" 

st.set_page_config(page_title="Fonozis", page_icon="🎸")

st.title("🎸 Fonozis")

# --- INTERFAZ DE GRABACIÓN ---
st.subheader("Capturar Idea")

# Este es el selector nativo. En iPhone/Android, al tocarlo 
# te dará la opción "Tomar foto/video" o "Grabar sonido".
archivo = st.file_uploader(
    "Toca aquí para grabar o subir audio", 
    type=["mp3", "wav", "m4a"], 
    accept_multiple_files=False
)

if archivo:
    st.audio(archivo)
    etiqueta = st.text_input("Etiqueta para esta idea:")
    
    if st.button("Publicar en la banda"):
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{etiqueta.replace(' ', '_')}.mp3"
        url_subida = f"{BASE_URL}/storage/v1/object/audios/{filename}"
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
        
        with st.spinner('Publicando...'):
            res = requests.post(url_subida, headers=headers, data=archivo.getvalue())
            
        if res.status_code == 200:
            st.success("¡Idea guardada!")
            st.rerun()
        else:
            st.error("Error al subir.")

# --- LISTA DE AUDIOS ---
st.divider()
st.subheader("Biblioteca de Ideas")
res_list = requests.post(f"{BASE_URL}/storage/v1/object/list/audios", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
if res_list.status_code == 200:
    for f in reversed(res_list.json()):
        file_url = f"{BASE_URL}/storage/v1/object/public/audios/{f['name']}"
        with st.expander(f"🎵 {f['name'].replace('.mp3', '')}"):
            st.audio(file_url)
