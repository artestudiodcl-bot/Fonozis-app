import streamlit as st
import requests
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
# LOGIN (BANDA + USUARIO)
# ======================================================

# ======================================================
# BANDAS Y CONTRASEÑAS
# ======================================================

BANDAS = {
    "Fonozis": "1234",
    "Rafa": "abc123",
    "blink182": "punkrock"
}

# ======================================================
# LOGIN
# ======================================================
# ======================================================
# BANDAS Y CONTRASEÑAS
# ======================================================

BANDAS = {
    "fonozis": "1234",
    "rafa": "abc123"
}

# ======================================================
# LOGIN
# ======================================================

import uuid

# =========================
# CREATE OR JOIN BAND
# =========================

st.title("🎸 Jam - Login")

mode = st.radio("Modo", ["Unirse a banda", "Crear banda"])

name = st.text_input("Tu nombre")

band_name = st.text_input("Nombre de la banda")
password = st.text_input("Contraseña", type="password")

# =========================
# CREATE BAND
# =========================

if st.button("Entrar"):

    if not name or not band_name or not password:
        st.error("Completa todos los campos")
        st.stop()

    band_name = band_name.strip().lower()

    # buscar banda
    res = requests.post(
        f"{BASE_URL}/rest/v1/bands?select=*",
        headers=HEADERS,
        json={}
    )

    bands = res.json() if res.status_code == 200 else []

    existing = next((b for b in bands if b["name"] == band_name), None)

    # =========================
    # CREATE MODE
    # =========================

    if mode == "Crear banda":

        if existing:
            st.error("Esa banda ya existe")
        else:

            requests.post(
                f"{BASE_URL}/rest/v1/bands",
                headers=HEADERS,
                json={
                    "name": band_name,
                    "password": password
                }
            )

            st.success("Banda creada")

    # =========================
    # JOIN MODE
    # =========================

    else:

        if not existing:
            st.error("Banda no existe")
        elif existing["password"] != password:
            st.error("Contraseña incorrecta")
        else:

            st.session_state.band_id = existing["id"]
            st.session_state.band_name = band_name
            st.session_state.user_name = name

            st.success("Bienvenido 🎸")
            st.rerun()

    st.stop()# ======================================================
# VARIABLES GLOBALES
# ======================================================

BANDA = st.session_state.banda
USUARIO = st.session_state.usuario

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Fonozis",
    page_icon="🎸",
    layout="centered"
)

st.title(f"Jam | {USUARIO}")
st.caption(f"Banda activa: {BANDA}")

st.markdown("""
### Bienvenido a Jam
Guarda ideas, organiza fechas y comparte demos con tu banda.
""")

# ======================================================
# CSS CHAT
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
    max-width: 80%;
}

.chat-bubble-other {
    background-color: #E9E9EB;
    color: black;
    padding: 10px 15px;
    border-radius: 18px;
    margin: 8px 0;
    width: fit-content;
    max-width: 80%;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# TABS
# ======================================================

tab1, tab2, tab3, tab4 = st.tabs(
    ["🎙️ Subir Idea", "💬 Muro", "🎧 Audios", "📅 Fechas"]
)

# ======================================================
# TAB 1 - SUBIR AUDIO
# ======================================================

with tab1:

    st.subheader("🎙️ Grabar idea")

    etiqueta = st.text_input("Nombre de la idea")
    audio = st.audio_input("🎤 Grabar idea")

    if audio and etiqueta:

        st.audio(audio)

        if st.button("Publicar idea"):

            filename = (
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
                f"_{USUARIO}_{etiqueta.replace(' ', '_')}.m4a"
            )

            path = f"audios/{BANDA}/{filename}"

            response = requests.post(
                f"{BASE_URL}/storage/v1/object/{path}",
                headers={**HEADERS, "Content-Type": "audio/mp4"},
                data=audio.read()
            )

            if response.status_code in [200, 201]:
                st.success("✅ Idea publicada")
                st.rerun()
            else:
                st.error(response.text)

# ======================================================
# TAB 2 - CHAT
# ======================================================
with tab2:

    st.subheader("💬 Muro de la banda")

def send_message():

    text = st.session_state.msg

    if text:

        requests.post(
            f"{BASE_URL}/rest/v1/messages",
            headers=HEADERS,
            json={
                "band_id": st.session_state.band_id,
                "user_name": st.session_state.user_name,
                "message": text
            }
        )

        st.session_state.msg = ""

st.text_input("Escribe mensaje", key="msg", on_change=send_message)

# =========================
# LOAD MESSAGES
# =========================

res = requests.post(
    f"{BASE_URL}/rest/v1/messages?select=*",
    headers=HEADERS,
    json={}
)

messages = res.json() if res.status_code == 200 else []

messages = [
    m for m in messages
    if m.get("band_id") == st.session_state.band_id
]

for m in sorted(messages, key=lambda x: x["created_at"]):

    if m["user_name"] == st.session_state.user_name:
        st.markdown(f"**🟦 Tú:** {m['message']}")
    else:
        st.markdown(f"**{m['user_name']}:** {m['message']}")
    # ==================================================
    # INPUT
    # ==================================================

    st.text_input(
        "Escribe un mensaje",
        key="msg_input",
        on_change=enviar_mensaje
    )

    # ==================================================
    # LISTAR MENSAJES
    # ==================================================

    response = requests.post(
        f"{BASE_URL}/storage/v1/object/list/mensajes",
        headers=HEADERS,
        json={
            "prefix": f"{BANDA}/"
        }
    )

    if response.status_code == 200:

        mensajes = sorted(
            response.json(),
            key=lambda x: x["name"]
        )

        for m in mensajes:

            # nombre real del archivo
            archivo = m["name"]

            # URL pública correcta
            url = (
                f"{BASE_URL}/storage/v1/object/public/"
                f"mensajes/{BANDA}/{archivo}"
            )

            contenido = requests.get(url).text

            if "|" in contenido:

                usuario, texto = contenido.split("|", 1)

                clase = (
                    "chat-bubble-me"
                    if usuario == USUARIO
                    else "chat-bubble-other"
                )

                st.markdown(
                    f"""
                    <div class="{clase}">
                        {texto}
                        <br>
                        <small>{usuario}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    else:

        st.error(response.text)
# ======================================================
# TAB 3 - AUDIOS
# ======================================================

with tab3:

    st.subheader("🎧 Ideas de la banda")

    response = requests.post(
        f"{BASE_URL}/storage/v1/object/list/audios",
        headers=HEADERS,
        json={"prefix": f"audios/{BANDA}/"}
    )

    if response.status_code == 200:

        archivos = sorted(response.json(), key=lambda x: x["name"], reverse=True)

        for f in archivos:

            url = f"{BASE_URL}/storage/v1/object/public/audios/{BANDA}/{f['name']}"

            nombre = f["name"].replace(".m4a", "").replace("_", " ")

            with st.expander(f"🎵 {nombre}"):
                st.audio(url, format="audio/mp4")

# ======================================================
# TAB 4 - FECHAS
# ======================================================

with tab4:

    st.subheader("📅 Fechas de la banda")

    fecha = st.date_input("Fecha")
    hora = st.time_input("Hora")
    titulo = st.text_input("Evento")
    lugar = st.text_input("Lugar")

    if st.button("Guardar fecha"):

        filename = f"fecha_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        path = f"fechas/{BANDA}/{filename}"

        contenido = f"{fecha}|{hora}|{titulo}|{lugar}|{USUARIO}"

        response = requests.post(
            f"{BASE_URL}/storage/v1/object/{path}",
            headers={**HEADERS, "Content-Type": "text/plain"},
            data=contenido.encode("utf-8")
        )

        if response.status_code in [200, 201]:
            st.success("✅ Fecha guardada")
            st.rerun()
        else:
            st.error(response.text)

    st.markdown("---")
    st.markdown("## 📌 Próximas fechas")

    response = requests.post(
        f"{BASE_URL}/storage/v1/object/list/fechas",
        headers=HEADERS,
        json={"prefix": f"fechas/{BANDA}/"}
    )

    if response.status_code == 200:

        fechas = sorted(response.json(), key=lambda x: x["name"], reverse=True)

        for f in fechas:

            url = f"{BASE_URL}/storage/v1/object/public/fechas/{BANDA}/{f['name']}"

            contenido = requests.get(url).text
            datos = contenido.split("|")

            if len(datos) >= 5:

                st.markdown(f"""
                ### 🎸 {datos[2]}
                📅 **Fecha:** {datos[0]}
                🕒 **Hora:** {datos[1]}
                📍 **Lugar:** {datos[3]}
                👤 {datos[4]}
                ---
                """)

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.markdown("---")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.clear()
    st.rerun()
