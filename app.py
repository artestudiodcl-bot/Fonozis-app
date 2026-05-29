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

if "banda" not in st.session_state:

    st.title("🎸 Acceso a Jam")

    banda = st.text_input(
        "Nombre de la banda"
    ).strip().lower()

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    usuario = st.text_input(
        "Tu nombre"
    )

    if st.button("Entrar"):

        # validar banda
        if banda in BANDAS:

            # validar password
            if BANDAS[banda] == password:

                st.session_state.banda = banda
                st.session_state.usuario = usuario

                st.success("✅ Acceso permitido")

                st.rerun()

            else:

                st.error("❌ Contraseña incorrecta")

        else:

            st.error("❌ Banda no encontrada")

    st.stop()

# ======================================================
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

    # ==================================================
    # ENVIAR MENSAJE
    # ==================================================

    def enviar_mensaje():

        texto = st.session_state.msg_input

        if texto.strip():

            filename = (
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{USUARIO}.txt"
            )

            # ✅ carpeta interna del bucket
            path = f"{BANDA}/{filename}"

            contenido = f"{USUARIO}|{texto}"

            response = requests.post(
                f"{BASE_URL}/storage/v1/object/mensajes/{path}",
                headers={
                    **HEADERS,
                    "Content-Type": "text/plain"
                },
                data=contenido.encode("utf-8")
            )

            if response.status_code not in [200, 201]:
                st.error(response.text)

            st.session_state.msg_input = ""

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