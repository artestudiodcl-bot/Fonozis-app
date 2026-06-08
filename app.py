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

st.markdown("""
<style>

.msg-me{
    background:#007AFF;
    color:white;
    padding:12px;
    border-radius:18px;
    margin-top:6px;
    margin-bottom:6px;
    margin-left:25%;
}

.msg-other{
    background:#2C2C2E;
    color:white;
    padding:12px;
    border-radius:18px;
    margin-top:6px;
    margin-bottom:6px;
    margin-right:25%;
}

.msg-name{
    font-size:11px;
    opacity:0.7;
    margin-top:5px;
}

</style>
""", unsafe_allow_html=True)

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

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💬 Muro",
        "🎙 Ideas",
        "🎧 Audios",
        "📅 Fechas",
        "🎵 Set List"
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
    "Mensaje",
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

# ==========================================
# MOSTRAR MENSAJES
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
        
with tab1:

    st.subheader("💬 Muro")

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
            )

# ======================================================
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
        "prefix": ""
    }
)

    if res.status_code == 200:

        archivos = sorted(
            res.json(),
            key=lambda x: x["name"],
            reverse=True
        )

        for f in archivos:
            
            if "." not in f["name"]:
                continue

            url = (
    f"{BASE_URL}/storage/v1/object/public/"
    f"audios/{f['name']}"
)
            
            st.audio(url)

# ======================================================
# FECHAS
# ======================================================
with tab4:

    st.subheader("📅 Fechas")

    fecha = st.date_input("Fecha")
    hora = st.time_input("Hora")
    titulo = st.text_input("Evento", key="evento_fecha")
    lugar = st.text_input("Lugar", key="lugar_fecha")

    # =========================
    # GUARDAR FECHA
    # =========================

    if st.button("Guardar fecha"):

        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

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
            st.success("✅ Fecha guardada")
            st.rerun()
        else:
            st.error(res.text)

    # =========================
    # LISTAR FECHAS
    # =========================

    st.markdown("---")
    st.subheader("📅 Próximas fechas")

    res = requests.post(
        f"{BASE_URL}/storage/v1/object/list/fechas",
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

        archivos = [
            f for f in archivos
            if f["name"].endswith(".txt")
        ]

        if not archivos:
            st.info("No hay fechas registradas")

        for f in archivos:

            url = (
                f"{BASE_URL}/storage/v1/object/public/"
                f"fechas/{BANDA}/{f['name']}"
            )

            contenido = requests.get(url).content.decode("utf-8")

            datos = contenido.split("|")

            if len(datos) >= 5:

                fecha_txt = datos[0]
                hora_txt = datos[1]
                titulo_txt = datos[2]
                lugar_txt = datos[3]
                usuario_txt = datos[4]

                st.markdown(
                    f"""
### 🎸 {titulo_txt}

📅 Fecha: {fecha_txt}

🕒 Hora: {hora_txt}

📍 Lugar: {lugar_txt}

👤 Agregado por: {usuario_txt}

---
"""
                )

    else:
        st.error("No se pudieron cargar las fechas")
     
# ======================================================
# Set List
# ======================================================

with tab5:
    
    st.subheader("🎵 Set List")

    set_name = st.text_input(
        "Nombre del Set",
        key="set_name"
    )

    song_name = st.text_input(
        "Canción",
        key="song_name"
    )

    bpm = st.number_input(
        "BPM",
        min_value=40,
        max_value=300,
        value=120
    )

    key_signature = st.text_input(
        "Tonalidad",
        key="key_signature"
    )

    if st.button("Agregar canción"):

        payload = {
            "banda": BANDA,
            "set_name": set_name,
            "song_name": song_name,
            "bpm": bpm,
            "key_signature": key_signature,
            "position": 999
        }

        res = requests.post(
            f"{BASE_URL}/rest/v1/setlists",
            headers={
                **HEADERS,
                "Prefer": "return=minimal"
            },
            json=payload
        )

        if res.status_code in [200, 201]:
            st.success("✅ Canción agregada")
            st.rerun()

    st.markdown("---")
    st.subheader("🎸 Sets guardados")

    res = requests.get(
        f"{BASE_URL}/rest/v1/setlists?banda=eq.{BANDA}&order=set_name.asc",
        headers=HEADERS
    )

    if res.status_code == 200:

        canciones = res.json()

        sets = {}

        for c in canciones:

            nombre_set = c["set_name"]

            if nombre_set not in sets:
                sets[nombre_set] = []

            sets[nombre_set].append(c)

        for nombre_set, items in sets.items():

            with st.expander(f"🎵 {nombre_set}"):

                for i, cancion in enumerate(items, start=1):

                    st.write(
                        f"{i}. "
                        f"{cancion['song_name']} "
                        f"• {cancion['bpm']} BPM "
                        f"• {cancion['key_signature']}"
)
# ======================================================
# LOGOUT
# ======================================================

st.sidebar.markdown("---")

if st.sidebar.button("Cerrar sesión"):

    st.session_state.clear()
    st.rerun()
