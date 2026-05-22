import streamlit as st
import requests
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

# --- CONFIGURACIÓN ---
PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZycWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMTc2NTUsImV4cCI6MjA5NDg5MzY1NX0.XZJbD4TRwC0rAB3IabHYFbyN4fZ53i1gKpjGtImJjgg"
st.set_page_config(page_title="Fonozis", page_icon="🎸")

st.title("🎸 Fonozis: HQ de la Banda")

tab1, tab2, tab3 = st.tabs(["🎙️ Grabador", "💬 Muro", "🎧 Audios"])

# --- TAB 1: GRABADOR WEBRTC ---
with tab1:
    st.subheader("Grabar Idea en Vivo")
    
    # Esto inicializa el componente de audio en vivo
    webrtc_ctx = webrtc_streamer(
        key="audio-recorder",
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": False, "audio": True},
    )
    
    st.info("Nota: Al presionar 'Start', el navegador pedirá acceso al micrófono. Autorízalo para activar la grabación.")

# --- TAB 2: MURO (Chat) ---
with tab2:
    st.subheader("Muro de Control")
    if "msg_input" not in st.session_state: st.session_state.msg_input = ""
    def enviar():
        if st.session_state.msg_input:
            msg_filename = f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
            requests.post(f"{BASE_URL}/storage/v1/object/mensajes/{msg_filename}", 
                          headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, 
                          data=st.session_state.msg_input.encode('utf-8'))
            st.session_state.msg_input = ""
    
    st.text_input("Mensaje para la banda:", key="msg_input", on_change=enviar)
    
    res_list_msg = requests.post(f"{BASE_URL}/storage/v1/object/list/mensajes", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    if res_list_msg.status_code == 200:
        for m in sorted(res_list_msg.json(), key=lambda x: x['name']):
            content = requests.get(f"{BASE_URL}/storage/v1/object/public/mensajes/{m['name']}", headers={"apikey": SUPABASE_KEY}).text
            st.markdown(f"**Chat:** {content}")

# --- TAB 3: AUDIOS ---
with tab3:
    st.subheader("Audios Disponibles")
    if st.button("Actualizar"): st.rerun()
    res_list = requests.post(f"{BASE_URL}/storage/v1/object/list/audios", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    if res_list.status_code == 200:
        for f in reversed(res_list.json()):
            file_url = f"{BASE_URL}/storage/v1/object/public/audios/{f['name']}"
            with st.expander(f"🎵 {f['name']}"): st.audio(file_url)
