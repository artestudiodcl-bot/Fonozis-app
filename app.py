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
    nombre = st.selectbox("¿Quién eres?", ["Elige tu nombre", "Noe (Bajo)", "Gaston (Guitarra)", "Ana (Voz)", "Carlos (Batería)"])
    if st.button("Entrar") and nombre != "Elige tu nombre":
        st.session_state.usuario = nombre
        st.rerun()
    st.stop()

# --- CSS ESTILO IMESSAGE ---
st.markdown("""
    <style>
    .chat-bubble-me { background-color: #007AFF; color: white; padding: 10px 15px; border-radius: 18px; margin: 5px 0; width: fit-content; margin-left: auto; text-align: right; }
    .chat-bubble-other { background-color: #E9E9EB; color: black; padding: 10px 15px; border-radius: 18px; margin: 5px 0; width: fit-content; text-align: left; }
    </style>
""", unsafe_allow_html=True)

st.title(f"🎸 Fonozis | {st.session_state.usuario}")

tab1, tab2, tab3 = st.tabs(["🎙️ Subir Idea", "💬 Muro", "🎧 Audios"])

# --- TAB 1: SUBIR IDEA ---
with tab1:
    archivo = st.file_uploader("Selecciona o graba tu idea", type=["mp3", "wav", "m4a"])
    etiqueta = st.text_input("Nombre de la idea:")
    
    if archivo and etiqueta and st.button("Publicar"):
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
    if "msg_input" not in st.session_state: st.session_state.msg_input = ""

    def enviar_mensaje():
        if st.session_state.msg_input:
            msg_filename = f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}_{st.session_state.usuario}.txt"
            content = f"{st.session_state.usuario}|{st.session_state.msg_input}"
            requests.post(f"{BASE_URL}/storage/v1/object/mensajes/{msg_filename}", 
                          headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, 
                          data=content.encode('utf-8'))
            st.session_state.msg_input = ""

    st.text_input("Escribe un mensaje:", key="msg_input", on_change=enviar_mensaje)

    res_list_msg = requests.post(f"{BASE_URL}/storage/v1/object/list/mensajes", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    if res_list_msg.status_code == 200:
        mensajes = sorted(res_list_msg.json(), key=lambda x: x['name'], reverse=True)
        for m in mensajes:
            raw_content = requests.get(f"{BASE_URL}/storage/v1/object/public/mensajes/{m['name']}", headers={"apikey": SUPABASE_KEY}).text
            if "|" in raw_content:
                user, text = raw_content.split("|", 1)
                clase = "chat-bubble-me" if user == st.session_state.usuario else "chat-bubble-other"
                st.markdown(f'<div class="{clase}">{text} <br><small style="font-size:9px; opacity:0.6;">{user}</small></div>', unsafe_allow_html=True)

# --- TAB 3: AUDIOS ---
with tab3:
    res_list = requests.post(f"{BASE_URL}/storage/v1/object/list/audios", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    if res_list.status_code == 200:
        for f in reversed(res_list.json()):
            nombre_archivo = f['name'].split('_', 1)[-1]
            file_url = f"{BASE_URL}/storage/v1/object/public/audios/{f['name']}"
            with st.expander(f"🎵 {nombre_archivo.replace('_', ' ')}"):
                st.audio(file_url)

if st.sidebar.button("Cerrar sesión"):
    del st.session_state.usuario
    st.rerun()
