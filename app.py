import streamlit as st
import requests
from datetime import datetime

# ======================================================
# CONFIG SUPABASE
# ======================================================

PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"

SUPABASE_KEY = "TU_SUPABASE_KEY"

HEADERS = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "apikey": SUPABASE_KEY
}

# ======================================================
# SEGURIDAD SESSION STATE
# ======================================================

st.session_state.setdefault("banda", None)
st.session_state.setdefault("user_name", None)

# ======================================================
# LOGIN
# ======================================================

if not st.session_state.banda or not st.session_state.user_name:

    st.title("🎸 Acceso a Jam")

    banda_input = st.text_input("Nombre de la banda")
    usuario_input = st.text_input("Tu nombre")
    password_input = st.text_input("Contraseña", type="password")

    BANDAS = {
        "fonozis": "1234",
        "rafa": "abc123"
    }

    if st.button("Entrar"):

        banda = banda_input.strip().lower().replace(" ", "")
        usuario = usuario_input.strip()

        if not banda or not usuario or not password_input:
            st.error("Completa todos los campos")
            st.stop()

        if banda not in BANDAS:
            st.error("❌ Banda no encontrada")
            st.stop()

        if BANDAS[banda] != password_input:
            st.error("❌ Contraseña incorrecta")
            st.stop()

        st.session_state.banda = banda
        st.session_state.user_name = usuario

        st.rerun()

    st.stop()

# ======================================================
# VARIABLES SEGURAS
# ======================================================

BANDA = st.session_state.banda
USUARIO = st.session_state.user_name

# ======================================================
# UI GENERAL
# ======================================================

st.title(f"🎸 Jam | {BANDA}")
st.caption(f"Usuario: {USUARIO}")

tab1, tab2, tab3, tab4 = st.tabs([
    "🎙️ Subir Idea",
    "💬 Muro",
    "🎧 Audios",
    "📅 Fechas"
])

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

            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{USUARIO}.txt"
            path = f"mensajes/{BANDA}/{filename}"

            contenido = f"{USUARIO}|{text}"

            response = requests.post(
                f"{BASE_URL}/storage/v1/object/{path}",
                headers={**HEADERS, "Content-Type": "text/plain"},
                data=contenido.encode("utf-8")
            )

            if response.status_code not in [200, 201]:
                st.error(response.text)

            st.session_state.msg = ""

    st.text_input("Escribe un mensaje", key="msg", on_change=send_message)

    response = requests.post(
        f"{BASE_URL}/storage/v1/object/list/mensajes",
        headers=HEADERS,
        json={"prefix": f"{BANDA}/"}
    )

    if response.status_code == 200:

        mensajes = sorted(response.json(), key=lambda x: x["name"])

        for m in mensajes:

            url = f"{BASE_URL}/storage/v1/object/public/mensajes/{BANDA}/{m['name']}"

            contenido = requests.get(url).text

            if "|" in contenido:

                user, text = contenido.split("|", 1)

                style = "chat-bubble-me" if user == USUARIO else "chat-bubble-other"

                st.markdown(f"""
                <div class="{style}">
                    {text}<br>
                    <small>{user}</small>
                </div>
                """, unsafe_allow_html=True)

# ======================================================
# TAB 3 - AUDIOS
# ======================================================

with tab3:

    st.subheader("🎧 Ideas de la banda")

    response = requests.post(
        f"{BASE_URL}/storage/v1/object/list/audios",
        headers=HEADERS,
        json={"prefix": f"{BANDA}/"}
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
        json={"prefix": f"{BANDA}/"}
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
                📅 {datos[0]}
                🕒 {datos[1]}
                📍 {datos[3]}
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
