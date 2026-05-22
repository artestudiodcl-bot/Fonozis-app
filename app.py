import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZycWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMTc2NTUsImV4cCI6MjA5NDg5MzY1NX0.XZJbD4TRwC0rAB3IabHYFbyN4fZ53i1gKpjGtImJjgg"
st.set_page_config(page_title="Fonozis", page_icon="🎸")

# --- LOGIN SIMBÓLICO ---
if "usuario" not in st.session_state:
    st.title("🎸 Fonozis: Identifícate")
    nombre = st.selectbox("¿Quién eres?", ["Elige tu nombre", "Juan (Bajo)", "Pedro (Guitarra)", "Ana (Voz)", "Carlos (Batería)"])
    if st.button("Entrar") and nombre != "Elige tu nombre":
        st.session_state.usuario = nombre
        st.rerun()
    st.stop() # Detiene la ejecución hasta que elijan nombre

# Si ya hay usuario, mostramos la app
st.title(f"🎸 Fonozis | {st.session_state.usuario}")

tab1, tab2, tab3 = st.tabs(["🎙️ Subir Idea", "💬 Muro", "🎧 Audios"])

# --- TAB 1: SUBIR IDEA ---
with tab1:
    archivo = st.file_uploader("Selecciona o graba tu idea", type=["mp3", "wav", "m4a"])
    etiqueta = st.text_input("Nombre de la idea:")
    
    if archivo and etiqueta and st.button("Publicar"):
        # Incluimos el nombre del usuario automáticamente en el nombre del archivo
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{st.session_state.usuario}_{etiqueta.replace(' ', '_')}.mp3"
        url_subida = f"{BASE_URL}/storage/v1/object/audios/{filename}"
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
        
        with st.spinner('Publicando...'):
            res = requests.post(url_subida, headers=headers, data=archivo.getvalue())
        
        if res.status_code == 200:
            st.success("¡Publicado!")
            st.rerun()

# --- TAB 2: MURO ---
with tab2:
    msg = st.text_input("Escribe un mensaje:")
    if st.button("Enviar al muro"):
        msg_filename = f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}_{st.session_state.usuario}.txt"
        content = f"{st.session_state.usuario}: {msg}"
        requests.post(f"{BASE_URL}/storage/v1/object/mensajes/{msg_filename}", 
                      headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, 
                      data=content.encode('utf-8'))
        st.rerun()

    # Mostrar mensajes
    res_list_msg = requests.post(f"{BASE_URL}/storage/v1/object/list/mensajes", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    if res_list_msg.status_code == 200:
        for m in sorted(res_list_msg.json(), key=lambda x: x['name'], reverse=True):
            content = requests.get(f"{BASE_URL}/storage/v1/object/public/mensajes/{m['name']}", headers={"apikey": SUPABASE_KEY}).text
            st.write(f"💬 {content}")

# --- TAB 3: AUDIOS ---
with tab3:
    res_list = requests.post(f"{BASE_URL}/storage/v1/object/list/audios", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    if res_list.status_code == 200:
        for f in reversed(res_list.json()):
            # Separamos el nombre para que sea legible
            nombre_archivo = f['name'].split('_', 1)[-1]
            file_url = f"{BASE_URL}/storage/v1/object/public/audios/{f['name']}"
            with st.expander(f"🎵 {nombre_archivo.replace('_', ' ')}"):
                st.audio(file_url)

if st.sidebar.button("Cerrar sesión"):
    del st.session_state.usuario
    st.rerun()
