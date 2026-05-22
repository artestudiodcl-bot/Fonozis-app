import streamlit as st
import requests
from datetime import datetime

# CONFIGURACIÓN
PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZycWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMTc2NTUsImV4cCI6MjA5NDg5MzY1NX0.XZJbD4TRwC0rAB3IabHYFbyN4fZ53i1gKpjGtImJjgg" 

st.set_page_config(page_title="Fonozis", page_icon="🎸")
st.title("🎸 Fonozis: HQ de la Banda")

tab1, tab2, tab3 = st.tabs(["🎙️ Grabar/Subir", "💬 Muro de Texto", "🎧 Audios"])

# --- 1. GRABAR Y SUBIR ---
with tab1:
    st.subheader("Capturar idea")
    # Nota: Streamlit necesita una librería extra para grabar (streamlit-audio-recorder)
    # Por ahora, mantendremos la subida de archivos que ya funciona muy bien.
    comentario = st.text_input("Etiqueta para el audio:")
    archivo = st.file_uploader("Sube tu archivo de audio", type=["mp3", "wav"])
    
    if archivo and st.button("Subir audio"):
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{comentario.replace(' ', '_')}.mp3"
        url_subida = f"{BASE_URL}/storage/v1/object/audios/{filename}"
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY, "Content-Type": "audio/mpeg"}
        requests.post(url_subida, headers=headers, data=archivo.getvalue())
        st.success("¡Audio subido!")

# --- 2. MURO DE MENSAJES (Texto) ---
with tab2:
    st.subheader("Muro de mensajes")
    msg = st.text_input("Escribe algo para la banda:")
    if st.button("Enviar mensaje"):
        msg_filename = f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        url_msg = f"{BASE_URL}/storage/v1/object/mensajes/{msg_filename}"
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
        requests.post(url_msg, headers=headers, data=msg.encode('utf-8'))
        st.rerun()

    # Leer mensajes
    res_msg = requests.post(f"{BASE_URL}/storage/v1/object/list/mensajes", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    if res_msg.status_code == 200:
        for m in reversed(res_msg.json()):
            content = requests.get(f"{BASE_URL}/storage/v1/object/public/mensajes/{m['name']}", headers={"apikey": SUPABASE_KEY}).text
            st.info(f"{content}")

# --- 3. AUDIOS ---
with tab3:
    st.subheader("Lista de Audios")
    res_list = requests.post(f"{BASE_URL}/storage/v1/object/list/audios", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    if res_list.status_code == 200:
        for f in reversed(res_list.json()):
            file_url = f"{BASE_URL}/storage/v1/object/public/audios/{f['name']}"
            with st.expander(f"🎵 {f['name']}"):
                st.audio(file_url)
