import streamlit as st
import requests
from datetime import datetime

# CONFIGURACIÓN
PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZycWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMTc2NTUsImV4cCI6MjA5NDg5MzY1NX0.XZJbD4TRwC0rAB3IabHYFbyN4fZ53i1gKpjGtImJjgg" 

st.set_page_config(page_title="Fonozis", page_icon="🎸")
st.title("🎸 Fonozis: HQ de la Banda")

# PESTAÑAS PARA ORGANIZAR
tab1, tab2 = st.tabs(["📤 Subir Idea", "🎧 Escuchar Audios"])

with tab1:
    st.subheader("Subir nueva idea")
    comentario = st.text_input("¿Qué grabaste? (ej. Riff nuevo, Bajo intro)")
    archivo = st.file_uploader("Selecciona el archivo", type=["mp3", "wav"])

    if archivo and st.button("Publicar en el muro"):
        # Incluimos el comentario en el nombre del archivo
        prefijo = comentario.replace(' ', '_') if comentario else "Sin_nombre"
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{prefijo}_{archivo.name.replace(' ', '_')}"
        
        url_subida = f"{BASE_URL}/storage/v1/object/audios/{filename}"
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY, "Content-Type": archivo.type}
        
        with st.spinner('Publicando...'):
            res = requests.post(url_subida, headers=headers, data=archivo.getvalue())
        
        if res.status_code == 200:
            st.success("¡Publicado con éxito!")
        else:
            st.error("Error al subir.")

with tab2:
    st.subheader("Audios Disponibles")
    if st.button("Actualizar lista"):
        st.rerun()

    url_listado = f"{BASE_URL}/storage/v1/object/list/audios"
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
    
    res_list = requests.post(url_listado, headers=headers, json={"prefix": ""})
    
    if res_list.status_code == 200:
        archivos = res_list.json()
        for f in reversed(archivos):
            # Limpiamos el nombre para que se vea bonito
            nombre_mostrar = f['name'].split('_', 1)[-1].replace('_', ' ')
            file_url = f"{BASE_URL}/storage/v1/object/public/audios/{f['name']}"
            
            with st.expander(f"🎵 {nombre_mostrar}"):
                st.audio(file_url)
                st.caption(f"Subido el: {f['name'][:8]}")
    else:
        st.info("La caja está vacía. ¡Sube tu primera idea!")
