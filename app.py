import streamlit as st
import requests
from datetime import datetime
from streamlit_audio_recorder import audio_recorder

# --- CONFIGURACIÓN ---
PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZycWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMTc2NTUsImV4cCI6MjA5NDg5MzY1NX0.XZJbD4TRwC0rAB3IabHYFbyN4fZ53i1gKpjGtImJjgg"
st.set_page_config(page_title="Fonozis", page_icon="🎸")

# --- CSS PARA ESTILO CHAT ---
st.markdown("""
    <style>
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 20px;
        margin-bottom: 10px;
        background-color: #007AFF;
        color: white;
        width: fit-content;
        max-width: 80%;
        font-family: sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎸 Fonozis: HQ de la Banda")

tab1, tab2, tab3 = st.tabs(["🎙️ Grabar/Subir", "💬 Muro de Control", "🎧 Audios"])

# --- TAB 1: GRABAR Y SUBIR ---
with tab1:
    st.subheader("Capturar nueva idea")
    comentario = st.text_input("Etiqueta (ej. Riff nuevo, Solo):")
    
    # Grabador de audio
    audio_bytes = audio_recorder(text="Presiona para grabar", recording_color="#e74c3c", neutral_color="#3498db")
    
    if audio_bytes and st.button("Publicar grabación"):
        prefijo = comentario.replace(' ', '_') if comentario else "Grabacion"
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{prefijo}.wav"
        
        url_subida = f"{BASE_URL}/storage/v1/object/audios/{filename}"
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY, "Content-Type": "audio/wav"}
        
        with st.spinner('Publicando...'):
            res = requests.post(url_subida, headers=headers, data=audio_bytes)
        
        if res.status_code == 200:
            st.success("¡Publicado con éxito!")
            st.rerun()
        else:
            st.error(f"Error al subir: {res.status_code}")

# --- TAB 2: MURO DE CONTROL ---
with tab2:
    st.subheader("Muro de Control")
    
    if "msg_input" not in st.session_state:
        st.session_state.msg_input = ""

    def enviar_mensaje():
        msg = st.session_state.msg_input
        if msg:
            msg_filename = f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
            url_msg = f"{BASE_URL}/storage/v1/object/mensajes/{msg_filename}"
            headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
            requests.post(url_msg, headers=headers, data=msg.encode('utf-8'))
            st.session_state.msg_input = ""

    st.text_input("Escribe algo para la banda:", key="msg_input", on_change=enviar_mensaje)
    
    if st.button("Enviar"):
        enviar_mensaje()
        st.rerun()

    # Leer mensajes
    res_list_msg = requests.post(f"{BASE_URL}/storage/v1/object/list/mensajes", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    if res_list_msg.status_code == 200:
        mensajes = sorted(res_list_msg.json(), key=lambda x: x['name'])
        for m in mensajes:
            content = requests.get(f"{BASE_URL}/storage/v1/object/public/mensajes/{m['name']}", headers={"apikey": SUPABASE_KEY}).text
            st.markdown(f'<div class="chat-bubble">{content}</div>', unsafe_allow_html=True)

# --- TAB 3: LISTA DE AUDIOS ---
with tab3:
    st.subheader("Audios Disponibles")
    if st.button("Actualizar lista"):
        st.rerun()
        
    res_list = requests.post(f"{BASE_URL}/storage/v1/object/list/audios", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    
    if res_list.status_code == 200:
        for f in reversed(res_list.json()):
            nombre_mostrar = f['name'].split('_', 1)[-1].replace('.wav', '').replace('_', ' ')
            file_url = f"{BASE_URL}/storage/v1/object/public/audios/{f['name']}"
            with st.expander(f"🎵 {nombre_mostrar}"):
                st.audio(file_url)
    else:
        st.info("La caja está vacía.")
