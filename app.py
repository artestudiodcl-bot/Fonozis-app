import streamlit as st
import requests
from datetime import datetime

# ======================================================
# SUPABASE CONFIG
# ======================================================

PROJECT_ID = "yzwwstvrqjtaaoqxbwtz"
BASE_URL = f"https://{PROJECT_ID}.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6d3dzdHZycWp0YWFvcXhid3R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMTc2NTUsImV4cCI6MjA5NDg5MzY1NX0.XZJbD4TRwC0rAB3IabHYFbyN4fZ53i1gKpjGtImJjgg"
HEADERS = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "apikey": SUPABASE_KEY
}

# ======================================================
# SESSION SAFE INIT
# ======================================================

st.session_state.setdefault("banda", None)
st.session_state.setdefault("usuario", None)

# ======================================================
# LOGIN / CREATE BAND
# ======================================================

if not st.session_state.banda:

    st.title("🎸 Jam - Acceso")

    modo = st.radio("Modo", ["Unirse a banda", "Crear banda"])

    banda_input = st.text_input("Nombre de la banda")
    usuario = st.text_input("Tu nombre")
    password = st.text_input("Contraseña", type="password")

    # Bandas demo (después lo cambiamos a DB real)
    BANDAS = {
        "fonozis": "1234",
        "rafa": "abc123"
    }

    if st.button("Entrar"):

        if not banda_input or not usuario or not password:
            st.error("Completa todos los campos")
            st.stop()

        banda = banda_input.strip().lower().replace(" ", "")

        # =========================
        # CREAR BANDA
        # =========================
        if modo == "Crear banda":

            if banda in BANDAS:
                st.error("❌ Esa banda ya existe")
                st.stop()

            BANDAS[banda] = password
            st.success("✅ Banda creada")

        # =========================
        # UNIRSE
        # =========================
        else:

            if banda not in BANDAS:
                st.error("❌ Banda no encontrada")
                st.stop()

            if BANDAS[banda] != password:
                st.error("❌ Contraseña incorrecta")
                st.stop()

        # guardar sesión
        st.session_state.banda = banda
        st.session_state.usuario = usuario

        st.rerun()

    st.stop()

# ======================================================
# VARIABLES SEGURAS
# ======================================================

BANDA = st.session_state.banda
USUARIO = st.session_state.usuario

# ======================================================
# UI
# ======================================================

st.title(f"🎸 Jam | {BANDA}")
st.caption(f"Usuario: {USUARIO}")

tab1, tab2, tab3, tab4 = st.tabs([
    "🎙️ Ideas",
    "💬 Muro",
    "🎧 Audios",
    "📅 Fechas"
])

# ======================================================
# CHAT
# ======================================================

with tab2:

    st.subheader("💬 Muro")

    def send_msg():

        text = st.session_state.msg

        if text:

            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{USUARIO}.txt"
            path = f"mensajes/{BANDA}/{filename}"

            requests.post(
                f"{BASE_URL}/storage/v1/object/{path}",
                headers={**HEADERS, "Content-Type": "text/plain"},
                data=f"{USUARIO}|{text}".encode("utf-8")
            )

            st.session_state.msg = ""

    st.text_input("Escribe mensaje", key="msg", on_change=send_msg)

    res = requests.post(
        f"{BASE_URL}/storage/v1/object/list/mensajes",
        headers=HEADERS,
        json={"prefix": f"{BANDA}/"}
    )

    if res.status_code == 200:

        for m in sorted(res.json(), key=lambda x: x["name"]):

            url = f"{BASE_URL}/storage/v1/object/public/mensajes/{BANDA}/{m['name']}"

            data = requests.get(url).text

            if "|" in data:
                user, text = data.split("|", 1)

                if user == USUARIO:
                    st.markdown(f"🟦 **Tú:** {text}")
                else:
                    st.markdown(f"🟨 **{user}:** {text}")

# ======================================================
# AUDIOS
# ======================================================

with tab3:

    st.subheader("🎧 Audios")

    res = requests.post(
        f"{BASE_URL}/storage/v1/object/list/audios",
        headers=HEADERS,
        json={"prefix": f"{BANDA}/"}
    )

    if res.status_code == 200:

        for f in res.json():

            url = f"{BASE_URL}/storage/v1/object/public/audios/{BANDA}/{f['name']}"
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

    if st.button("Guardar"):

        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        path = f"fechas/{BANDA}/{filename}"

        contenido = f"{fecha}|{hora}|{titulo}|{lugar}|{USUARIO}"

        requests.post(
            f"{BASE_URL}/storage/v1/object/{path}",
            headers={**HEADERS, "Content-Type": "text/plain"},
            data=contenido.encode("utf-8")
        )

        st.success("Guardado")

# ======================================================
# LOGOUT
# ======================================================

st.sidebar.button("Cerrar sesión", on_click=lambda: st.session_state.clear())
