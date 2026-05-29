import streamlit as st
import requests
from datetime import datetime

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
# SESSION STATE
# ======================================================

st.session_state.setdefault("band_id", None)
st.session_state.setdefault("band_name", None)
st.session_state.setdefault("user_name", None)

# ======================================================
# LOGIN / CREATE BAND
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

        # =========================
        # BUSCAR BANDA
        # =========================

        res = requests.get(
            f"{BASE_URL}/rest/v1/bands?name=eq.{banda}",
            headers=HEADERS
        )

        if res.status_code != 200:
            st.error(res.text)
            st.stop()

        data = res.json()

        # =========================
        # CREAR
        # =========================

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

            # volver a buscar
            res = requests.get(
                f"{BASE_URL}/rest/v1/bands?name=eq.{banda}",
                headers=HEADERS
            )

            data = res.json()

        # =========================
        # UNIRSE
        # =========================

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
# VARIABLES SEGURAS
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
        "📅 Fechas",
    ]
)

# ======================================================
# TAB 1 - CHAT
# ======================================================

with tab1:

    st.subheader("💬 Muro")

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

    st.text_input(
        "Escribe mensaje",
        key="msg",
        on_change=send_msg
    )

    res = requests.get(
        f"{BASE_URL}/rest/v1/messages"
        f"?band_id=eq.{BAND_ID}"
        f"&order=created_at.asc",
        headers=HEADERS
    )

    if res.status_code == 200:

        mensajes = res.json()

        for m in mensajes:

            if m["user_name"] == USUARIO:
                st.markdown(
                    f"🟦 **Tú:** {m['message']}"
                )
            else:
                st.markdown(
                    f"🟨 **{m['user_name']}:** {m['message']}"
                )

# ======================================================
# TAB 2 - SUBIR AUDIO
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
            else:
                st.error(res.text)

# ======================================================
# TAB 3 - LISTAR AUDIOS
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

        for f in sorted(
            res.json(),
            key=lambda x: x["name"],
            reverse=True
        ):

            url = (
                f"{BASE_URL}/storage/v1/object/public/"
                f"audios/{BANDA}/{f['name']}"
            )

            st.audio(url)

# ======================================================
# TAB 4 - FECHAS
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
            f"{fecha}|{hora}|{titulo}|"
            f"{lugar}|{USUARIO}"
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
        else:
            st.error(res.text)

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.markdown("---")

if st.sidebar.button("Cerrar sesión"):

    st.session_state.clear()
    st.rerun()
