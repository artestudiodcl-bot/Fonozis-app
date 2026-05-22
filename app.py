import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZycWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMTc2NTUsImV4cCI6MjA5NDg5MzY1NX0.XZJbD4TRwC0rAB3IabHYFbyN4fZ53i1gKpjGtImJjgg"
# Configuración con el icono de la banda
st.set_page_config(
    page_title="Fonozis", 
    page_icon="logo_app.png"  # Asegúrate de tener este archivo en tu repo
)

# --- CSS ESTILO APP ---
st.markdown("""
    <style>
    .chat-bubble { padding: 12px 16px; border-radius: 15px; margin-bottom: 10px; background-color: #f1f0f0; color: #000; width: fit-content; max-width: 90%; }
    </style>
""", unsafe_allow_html=True)

st.title("🎸 Fonozis: HQ de la Banda")

tab1, tab2, tab3 = st.tabs(["🎙️ Subir Idea", "💬 Muro", "🎧 Audios"])

# --- TAB 1: SUBIR IDEA ---
with tab1:
    st.subheader("Capturar idea")
    st.info("💡 **Tip:** Si no aparece el botón grabar, usa la 'Grabadora' de tu celular y sube el archivo resultante aquí.")
    
    comentario = st.text_input("Etiqueta (ej. Riff nuevo):")
    archivo = st.file_uploader("Selecciona el archivo de audio (MP3/WAV)", type=["mp3", "wav"])
    
    if archivo and st.button("Publicar en el Muro"):
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{comentario.replace(' ', '_')}.mp3"
        url_subida = f"{BASE_URL}/storage/v1/object/audios/{filename}"
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY, "Content-Type": "audio/mpeg"}
        
        with st.spinner('Publicando...'):
            res = requests.post(url_subida, headers=headers, data=archivo.getvalue())
        
        if res.status_code == 200:
            st.success("¡Publicado!")
            st.rerun()
        else:
            st.error("Error al subir el archivo.")

# --- TAB 2: MURO ---
with tab2:
    st.subheader("Muro de Control")
    if "msg_input" not in st.session_state: st.session_state.msg_input = ""
    def enviar():
        if st.session_state.msg_input:
            msg_filename = f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
            url_msg = f"{BASE_URL}/storage/v1/object/mensajes/{msg_filename}"
            requests.post(url_msg, headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, data=st.session_state.msg_input.encode('utf-8'))
            st.session_state.msg_input = ""
    
    st.text_input("Mensaje para la banda:", key="msg_input", on_change=enviar)
    
    res_list_msg = requests.post(f"{BASE_URL}/storage/v1/object/list/mensajes", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    if res_list_msg.status_code == 200:
        for m in sorted(res_list_msg.json(), key=lambda x: x['name']):
            content = requests.get(f"{BASE_URL}/storage/v1/object/public/mensajes/{m['name']}", headers={"apikey": SUPABASE_KEY}).text
            st.markdown(f'<div class="chat-bubble">{content}</div>', unsafe_allow_html=True)

# --- TAB 3: AUDIOS ---
with tab3:
    st.subheader("Audios Disponibles")
    if st.button("Actualizar Lista"): st.rerun()
    res_list = requests.post(f"{BASE_URL}/storage/v1/object/list/audios", headers={"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}, json={"prefix": ""})
    if res_list.status_code == 200:
        for f in reversed(res_list.json()):
            nombre = f['name'].split('_', 1)[-1].replace('.mp3', '').replace('_', ' ')
            file_url = f"{BASE_URL}/storage/v1/object/public/audios/{f['name']}"
            with st.expander(f"🎵 {nombre}"): st.audio(file_url)
