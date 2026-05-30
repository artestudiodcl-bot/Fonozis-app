import streamlit as st
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ======================================================
# CONFIG
# ======================================================

st.set_page_config(
    page_title="Jam",
    page_icon="🎸",
    layout="centered"
)

PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZycWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMTc2NTUsImV4cCI6MjA5NDg5MzY1NX0.XZJbD4TRwC0rAB3IabHYFbyN4fZ53i1gKpjGtImJjgg"
HEADERS = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json",
}

# ======================================================
# SESSION
# ======================================================

st.session_state.setdefault("band_id", None)
st.session_state.setdefault("band_name", None)
st.session_state.setdefault("user_name", None)

# ======================================================
# LOGIN / CREAR BANDA
# ======================================================

if not st.session_state.band_id:

    st.title("🎸 Jam")
   modo = st.radio(
        "Modo",
        ["Unirse a banda", "Crear banda"]
    )

    nombre = st.text_input("Tu nombre")
    banda_input = st.text_input("Nombre de la banda")
    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if st.button("Entrar"):

        if not nombre or not banda_input or not password:
            st.error("Completa todos los campos")
            st.stop()

        banda = banda_input.strip().lower()

        # Buscar banda
        res = requests.get(
            f"{BASE_URL}/rest/v1/bands?name=eq.{banda}",
            headers=HEADERS
        )

        if res.status_code != 200:
            st.error(res.text)
            st.stop()

        data = res.json()

        # Crear banda
        if modo == "Crear banda":

            if data:
                st.error("❌ Esa banda ya existe")
                st.stop()

            create_res = requests.post(
                f"{BASE_URL}/rest/v1/bands",
                headers=HEADERS,
                json={
                    "name": banda,
                    "password": password
                }
            )

            if create_res.status_code not in [200, 201]:
                st.error(create_res.text)
                st.stop()

            # buscar otra vez
            res = requests.get(
                f"{BASE_URL}/rest/v1/bands?name=eq.{banda}",
                headers=HEADERS
            )

            data = res.json()

        # Entrar
        if not data:
            st.error("❌ Banda no encontrada")
            st.stop()

        band = data[0]

        if band["password"] != password:
            st.error("❌ Contraseña incorrecta")
            st.stop()

        st.session_state.band_id = band["id"]
        st.session_state.band_name = band["name"]
        st.session_state.user_name = nombre

        st.rerun()

    st.stop()

# ======================================================
# VARIABLES
# ======================================================

BAND_ID = st.session_state.band_id
BANDA = st.session_state.band_name
USUARIO = st.session_state.user_name

# ======================================================
# HEADER
# ======================================================

st.title(f"🎸 Jam | {BANDA}")
st.caption(f"Usuario: {USUARIO}")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "💬 Muro",
        "🎙️ Ideas",
        "🎧 Audios",
        "📅 Fechas"
    ]
)

# ======================================================
# CHAT
# ======================================================

with tab1:

    st.subheader("💬 Muro")

    # ==========================================
    # REFRESH AUTOMÁTICO
    # ==========================================

    st_autorefresh(
        interval=3000,
        key="chat_refresh"
    )

    # ==========================================
    # ENVIAR MENSAJE
    # ==========================================

    def send_msg():

        text = st.session_state.msg

        if text.strip():

            res = requests.post(
                f"{BASE_URL}/rest/v1/messages",
                headers=HEADERS,
                json={
                    "band_id": BAND_ID,
                    "user_name": USUARIO,
                    "message": text
                }
            )

            if res.status_code not in [200, 201]:
                st.error(res.text)

            st.session_state.msg = ""

    # ==========================================
    # INPUT
    # ==========================================

    st.text_input(
        "Escribe mensaje",
        key="msg",
        on_change=send_msg
    )

    # ==========================================
    # LEER MENSAJES
    # ==========================================

    res = requests.get(
        f"{BASE_URL}/rest/v1/messages"
        f"?band_id=eq.{BAND_ID}"
        f"&order=created_at.asc",
        headers=HEADERS
    )

    # ==========================================
    # MOSTRAR + TOAST
    # ==========================================

    if res.status_code == 200:

        mensajes = res.json()

        # -------------------------
        # CONTADOR PARA NOTIFICACIÓN
        # -------------------------

        total_actual = len(mensajes)

        if "last_count" not in st.session_state:
            st.session_state.last_count = total_actual

        # -------------------------
        # NUEVO MENSAJE
        # -------------------------

        if total_actual > st.session_state.last_count:

            ultimo = mensajes[-1]

            if ultimo["user_name"] != USUARIO:

                st.toast(
                    f"🎸 Nuevo mensaje de {ultimo['user_name']}"
                )

        st.session_state.last_count = total_actual

        # -------------------------
        # SI VACÍO
        # -------------------------

        if not mensajes:
            st.caption("No hay mensajes todavía 🎸")

        # -------------------------
        # MOSTRAR MENSAJES
        # -------------------------

        # ==========================================
# CSS ESTILO IPHONE
# ==========================================

st.markdown("""
<style>

.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.msg-me {
    background: #007AFF;
    color: white;
    padding: 10px 14px;
    border-radius: 18px;
    width: fit-content;
    max-width: 75%;
    margin-left: auto;
    font-size: 16px;
}

.msg-other {
    background: #E9E9EB;
    color: black;
    padding: 10px 14px;
    border-radius: 18px;
    width: fit-content;
    max-width: 75%;
    margin-right: auto;
    font-size: 16px;
}

.msg-name {
    font-size: 12px;
    opacity: 0.7;
    margin-top: 4px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# MOSTRAR MENSAJES
# ==========================================

for m in mensajes:

    usuario_msg = m["user_name"]
    texto_msg = m["message"]

    if usuario_msg == USUARIO:

        st.markdown(
            f"""
            <div class="msg-me">
                {texto_msg}
                <div class="msg-name">
                    Tú
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="msg-other">
                {texto_msg}
                <div class="msg-name">
                    {usuario_msg}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )# ======================================================
# SUBIR AUDIO
# ======================================================

with tab2:

    st.subheader("🎙️ Grabar idea")

    etiqueta = st.text_input(
        "Nombre de la idea"
    )

    audio = st.audio_input(
        "🎤 Grabar"
    )

    if audio and etiqueta:

        st.audio(audio)

        if st.button("Publicar idea"):

            filename = (
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
                f"_{USUARIO}_"
                f"{etiqueta.replace(' ', '_')}.m4a"
            )

            path = f"audios/{BANDA}/{filename}"

            res = requests.post(
                f"{BASE_URL}/storage/v1/object/{path}",
                headers={
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "apikey": SUPABASE_KEY,
                    "Content-Type": "audio/mp4",
                },
                data=audio.read()
            )

            if res.status_code in [200, 201]:
                st.success("✅ Publicado")
                st.rerun()

# ======================================================
# LISTA AUDIOS
# ======================================================

with tab3:

    st.subheader("🎧 Audios")

    res = requests.post(
        f"{BASE_URL}/storage/v1/object/list/audios",
        headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
        },
        json={
            "prefix": f"{BANDA}/"
        }
    )

    if res.status_code == 200:

        archivos = sorted(
            res.json(),
            key=lambda x: x["name"],
            reverse=True
        )

        for f in archivos:

            url = (
                f"{BASE_URL}/storage/v1/object/public/"
                f"audios/{BANDA}/{f['name']}"
            )

            st.audio(url)

# ======================================================
# FECHAS
# ======================================================

with tab4:

    st.subheader("📅 Fechas")

    fecha = st.date_input("Fecha")
    hora = st.time_input("Hora")
    titulo = st.text_input("Evento")
    lugar = st.text_input("Lugar")

    if st.button("Guardar fecha"):

        filename = (
            f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        )

        contenido = (
            f"{fecha}|{hora}|{titulo}|{lugar}|{USUARIO}"
        )

        path = f"fechas/{BANDA}/{filename}"

        res = requests.post(
            f"{BASE_URL}/storage/v1/object/{path}",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "apikey": SUPABASE_KEY,
                "Content-Type": "text/plain",
            },
            data=contenido.encode("utf-8")
        )

        if res.status_code in [200, 201]:
            st.success("✅ Guardado")
            st.rerun()

# ======================================================
# LOGOUT
# ======================================================

st.sidebar.markdown("---")

if st.sidebar.button("Cerrar sesión"):

    st.session_state.clear()
    st.rerun()
