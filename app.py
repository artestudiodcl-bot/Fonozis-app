import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Fonozis - Band Hub", page_icon="🎸", layout="centered")

# Intentar importar el grabador de audio nativo de forma segura
try:
    from audio_recorder_streamlit import audio_recorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False

# Conexión básica a Supabase vía API Rest
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

# Estilo personalizado general (Chat de interfaz limpia estilo iPhone)
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    h1, h2, h3 { color: #FF4B4B !important; }
    .chat-container { display: flex; flex-direction: column; gap: 15px; padding: 10px; margin-bottom: 20px; }
    .msg-row { display: flex; width: 100%; margin-bottom: 2px; }
    .msg-row.derecha { justify-content: flex-end; }
    .msg-row.izquierda { justify-content: flex-start; }
    .burbuja { max-width: 75%; padding: 12px 16px; border-radius: 18px; font-family: sans-serif; font-size: 15px; line-height: 1.4; }
    .derecha .burbuja { background-color: #007AFF; color: white; border-bottom-right-radius: 4px; }
    .izquierda .burbuja { background-color: #26262b; color: #e4e6eb; border-bottom-left-radius: 4px; }
    .msg-meta { font-size: 11px; margin-bottom: 5px; display: block; opacity: 0.7; font-weight: bold; }
    .derecha .msg-meta { color: #d0e3ff; }
    .izquierda .msg-meta { color: #a0a3a8; }
    </style>
    """, unsafe_allow_html=True)

# SELECCIÓN DE USUARIO
st.title("🎸 Fonozis: HQ de la Banda")
integrantes = ["Integrante 1", "Integrante 2", "Integrante 3", "Integrante 4"]
usuario_actual = st.sidebar.selectbox("¿Quién está usando la app?", integrantes)

tab_audios, tab_mensajes, tab_fechas = st.tabs(["🎵 Audios", "💬 Mensajes", "📅 Fechas"])

# --- APARTADO: AUDIOS ---
with tab_audios:
    st.header("Banco de Audios")
    modo_audio = st.radio("Elige cómo añadir audio:", ["Subir archivo", "Grabar en vivo"])
    audio_bytes = None
    
    if modo_audio == "Subir archivo":
        archivo_subido = st.file_uploader("Sube un archivo (MP3/WAV)", type=["mp3", "wav"])
        if archivo_subido:
            audio_bytes = archivo_subido.read()
    else:
        if AUDIO_RECORDER_AVAILABLE:
            st.write("Haz clic en el micrófono para empezar a grabar (se pondrá rojo y registrará en WAV):")
            audio_bytes = audio_recorder(text="", recording_color="#ff4b4b", neutral_color="#ffffff")
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
        else:
            st.error("El componente de grabación en vivo no está disponible en este navegador.")
        
    nombre_audio = st.text_input("Nombre de la pista / Idea:")
    categoria = st.selectbox("Categoría", ["Riff suelto", "Ensayo completo", "Maqueta", "Mezcla"])
    
    if st.button("Guardar Audio en el Banco"):
        if audio_bytes and nombre_audio:
            filename = f"{int(datetime.now().timestamp())}_{nombre_audio.replace(' ', '_')}.wav"
            
            # Encabezados explícitos para subir al Storage público
            storage_headers = {
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "apikey": SUPABASE_KEY,
                "Content-Type": "audio/wav"
            }
            
            upload_url = f"{SUPABASE_URL}/storage/v1/object/banco-audios/{filename}"
            res_upload = requests.post(upload_url, headers=storage_headers, data=audio_bytes)
            
            if res_upload.status_code in [200, 201]:
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/banco-audios/{filename}"
                
                # Encabezados de Base de Datos corregidos
                db_headers = {
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "apikey": SUPABASE_KEY,
                    "Content-Type": "application/json"
                }
                
                # CORRECCIÓN AQUÍ: Cambiado 'categorya' a 'categoria' para que coincida perfectamente
                payload = {
                    "nombre": nombre_audio, 
                    "categoria": categoria, 
                    "usuario": usuario_actual, 
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                    "archivo_url": public_url
                }
                requests.post(f"{SUPABASE_URL}/rest/v1/audios", headers=db_headers, json=payload)
                st.success("¡Audio guardado exitosamente!")
                st.rerun()
            else:
                st.error(f"Error al subir el archivo al almacenamiento (Código: {res_upload.status_code})")

    st.write("---")
    st.subheader("Audios de la Banda")
    
    read_headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
    try:
        res_audios = requests.get(f"{SUPABASE_URL}/rest/v1/audios?order=id.desc", headers=read_headers)
        audios_db = res_audios.json() if res_audios.status_code == 200 else []
    except:
        audios_db = []
    
    if not audios_db or not isinstance(audios_db, list):
        st.info("Aún no hay audios guardados.")
    else:
        for aud in audios_db:
            with st.expander(f"🎵 {aud.get('nombre', 'Audio')} ({aud.get('categoria', 'Suelto')}) - por {aud.get('usuario', 'Desconocido')}"):
                st.write(f"Grabado el: {aud.get('fecha', '')}")
                if aud.get('archivo_url'):
                    st.audio(aud.get('archivo_url'))

# --- APARTADO: MENSAJES ---
with tab_mensajes:
    st.header("Muro de Control")
    
    read_headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
    try:
        res_msg = requests.get(f"{SUPABASE_URL}/rest/v1/mensajes?order=id.asc", headers=read_headers)
        mensajes_db = res_msg.json() if res_msg.status_code == 200 else []
    except:
        mensajes_db = []
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    if isinstance(mensajes_db, list):
        for msg in mensajes_db:
            es_propio = msg.get('usuario') == usuario_actual
            clase_lado = "derecha" if es_propio else "izquierda"
            nombre_mostrar = "Tú" if es_propio else msg.get('usuario', 'Anónimo')
            
            html_burbuja = f'<div class="msg-row {clase_lado}"><div class="burbuja"><span class="msg-meta">{nombre_mostrar} • {msg.get("fecha", "")}</span>{msg.get("texto", "")}</div></div>'
            st.markdown(html_burbuja, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    texto_chat = st.text_area("Escribe un mensaje para la banda...", key="caja_chat_input")
    if st.button("Enviar Mensaje 🚀"):
        if texto_chat.strip():
            write_headers = {
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json"
            }
            payload = {"usuario": usuario_actual, "texto": texto_chat.strip(), "fecha": datetime.now().strftime("%H:%M")}
            requests.post(f"{SUPABASE_URL}/rest/v1/mensajes", headers=write_headers, json=payload)
            st.rerun()

# --- APARTADO: FECHAS ---
with tab_fechas:
    st.header("Agenda del Rock")
    col1, col2 = st.columns(2)
    with col1:
        fecha_evento = st.date_input("Fecha del evento")
        tipo_evento = st.selectbox("Tipo de evento", ["Ensayo", "Concierto", "Grabación", "Reunión"])
    with col2:
        descripcion_evento = st.text_input("Detalles")
    
    if st.button("Agendar Fecha"):
        if descripcion_evento:
            write_headers = {
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json"
            }
            payload = {"fecha_evento": fecha_evento.strftime("%Y-%m-%d"), "tipo": tipo_evento, "detalles": descripcion_evento, "creado_por": usuario_actual}
            requests.post(f"{SUPABASE_URL}/rest/v1/fechas", headers=write_headers, json=payload)
            st.success("¡Fecha anotada en la nube!")
            st.rerun()
            
    st.write("---")
    st.subheader("Próximos Compromisos")
    read_headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
    try:
        res_fechas = requests.get(f"{SUPABASE_URL}/rest/v1/fechas", headers=read_headers)
        fechas_db = res_fechas.json() if res_fechas.status_code == 200 else []
    except:
        fechas_db = []
    
    if not fechas_db or not isinstance(fechas_db, list):
        st.info("No hay fechas programadas.")
    else:
        df_fechas = pd.DataFrame(fechas_db)
        df_display = df_fechas.rename(columns={"fecha_evento": "Fecha", "tipo": "Tipo", "detalles": "Detalles", "creado_por": "Creado por"})
        st.dataframe(df_display[["Fecha", "Tipo", "Detalles", "Creado por"]].sort_values(by="Fecha"), use_container_width=True)
