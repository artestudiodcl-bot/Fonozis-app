import streamlit as st
import requests
import os
from datetime import datetime

# ======================================================
# CONFIG SUPABASE
# ======================================================

PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"

BASE_URL = f"https://{PROJECT_ID}.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZycWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMTc2NTUsImV4cCI6MjA5NDg5MzY1NX0.XZJbD4TRwC0rAB3IabHYFbyN4fZ53i1gKpjGtImJjgg"

HEADERS = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "apikey": SUPABASE_KEY
}

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Fonozis",
    page_icon="🎸",
    layout="centered"
)

# ======================================================
# LOGIN SIMPLE
# ======================================================

if "usuario" not in st.session_state:

    st.title("🎸 Fonozis")

    nombre = st.selectbox(
        "¿Quién eres?",
        [
            "Selecciona",
            "Noe (Bajo)",
            "Gaston (Guitarra)",
            "Ana (Voz)",
            "Carlos (Batería)"
        ]
    )

    if st.button("Entrar"):

        if nombre != "Selecciona":

            st.session_state.usuario = nombre
            st.rerun()

    st.stop()

# ======================================================
# CSS
# ======================================================

st.markdown("""
<style>

.chat-bubble-me {
    background-color: #007AFF;
    color: white;
    padding: 10px 15px;
    border-radius: 18px;
    margin: 8px 0;
    width: fit-content;
    margin-left: auto;
    text-align: right;
    max-width: 80%;
}

.chat-bubble-other {
    background-color: #E9E9EB;
    color: black;
    padding: 10px 15px;
    border-radius: 18px;
    margin: 8px 0;
    width: fit-content;
    text-align: left;
    max-width: 80%;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================

st.title(f"🎸 Fonozis | {st.session_state.usuario}")

tab1, tab2, tab3 = st.tabs(
    ["🎙️ Subir Idea", "💬 Muro", "🎧 Audios"]
)

# ======================================================
# TAB 1 - SUBIR AUDIO
# ======================================================

with tab1:

    st.subheader("🎙️ Grabar idea")

    etiqueta = st.text_input(
        "Nombre de la idea"
    )

    audio = st.audio_input(
        "🎤 Grabar idea"
    )

    if audio and etiqueta:

        st.audio(audio)

        if st.button("Publicar idea"):

            filename = (
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
                f"_{st.session_state.usuario}"
                f"_{etiqueta.replace(' ', '_')}.m4a"
            )

            upload_headers = {
                **HEADERS,
                "Content-Type": "audio/mp4"
            }

            with st.spinner("Subiendo audio..."):

                response = requests.post(
                    f"{BASE_URL}/storage/v1/object/audios/{filename}",
                    headers=upload_headers,
                    data=audio.read()
                )

            st.write(response.status_code)

            if response.status_code in [200, 201]:

                st.success("✅ Idea publicada")
                st.rerun()

            else:

                st.error(response.text)

# ======================================================
# TAB 2 - CHAT
# ======================================================

with tab2:

    st.subheader("💬 Muro")

    if "msg_input" not in st.session_state:
        st.session_state.msg_input = ""

    def enviar_mensaje():

        texto = st.session_state.msg_input

        if texto.strip():

            filename = (
                f"msg_"
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
                f"_{st.session_state.usuario}.txt"
            )

            contenido = (
                f"{st.session_state.usuario}|{texto}"
            )

            requests.post(
                f"{BASE_URL}/storage/v1/object/mensajes/{filename}",
                headers={
                    **HEADERS,
                    "Content-Type": "text/plain"
                },
                data=contenido.encode("utf-8")
            )

            st.session_state.msg_input = ""

    st.text_input(
        "Escribe un mensaje",
        key="msg_input",
        on_change=enviar_mensaje
    )

    response = requests.post(
        f"{BASE_URL}/storage/v1/object/list/mensajes",
        headers=HEADERS,
        json={"prefix": ""}
    )

    if response.status_code == 200:

        mensajes = sorted(
            response.json(),
            key=lambda x: x["name"],
            reverse=True
        )

        for m in mensajes:

            archivo_url = (
                f"{BASE_URL}/storage/v1/object/public/"
                f"mensajes/{m['name']}"
            )

            contenido = requests.get(
                archivo_url
            ).text

            if "|" in contenido:

                usuario, texto = contenido.split("|", 1)

                clase = (
                    "chat-bubble-me"
                    if usuario == st.session_state.usuario
                    else "chat-bubble-other"
                )

                st.markdown(
                    f"""
                    <div class="{clase}">
                        {texto}
                        <br>
                        <small style="opacity:0.6;">
                            {usuario}
                        </small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# ======================================================
# TAB 3 - AUDIOS
# ======================================================

with tab3:

    st.subheader("🎧 Ideas de la banda")

    if st.button("🔄 Actualizar"):
        st.rerun()

    response = requests.post(
        f"{BASE_URL}/storage/v1/object/list/audios",
        headers=HEADERS,
        json={"prefix": ""}
    )

    if response.status_code == 200:

        archivos = sorted(
            response.json(),
            key=lambda x: x["name"],
            reverse=True
        )

        for f in archivos:

            nombre_archivo = (
                f["name"]
                .replace(".m4a", "")
                .replace("_", " ")
            )

            file_url = (
                f"{BASE_URL}/storage/v1/object/public/"
                f"audios/{f['name']}"
            )

            with st.expander(f"🎵 {nombre_archivo}"):

                st.audio(
                    file_url,
                    format="audio/mp4"
                )

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.markdown("---")

if st.sidebar.button("Cerrar sesión"):

    del st.session_state.usuario
    st.rerun()
