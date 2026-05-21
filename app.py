import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Fonozis - Band Hub",
    page_icon="🎸",
    layout="centered"
)

# Estilo personalizado
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    h1, h2, h3 { color: #FF4B4B !important; }
    </style>
    """, unsafe_allow_html=True)

# INICIALIZACIÓN DEL ESTADO
if 'audios' not in st.session_state:
    st.session_state.audios = []
if 'mensajes' not in st.session_state:
    st.session_state.mensajes = [
        {"usuario": "Sistema", "texto": "¡Bienvenidos al Muro de Control de la banda!", "fecha": "2026-05-20"}
    ]
if 'fechas' not in st.session_state:
    st.session_state.fechas = []

# SELECCIÓN DE USUARIO
st.title("🎸 Fonozis: HQ de la Banda")
integrantes = ["Integrante 1", "Integrante 2", "Integrante 3", "Integrante 4"]
usuario_actual = st.sidebar.selectbox("¿Quién está usando la app?", integrantes)
st.sidebar.write(f"Conectado como: **{usuario_actual}**")

# SISTEMA DE PESTAÑAS
tab_audios, tab_mensajes, tab_fechas = st.tabs(["🎵 Audios", "💬 Mensajes", "📅 Fechas"])

# --- APARTADO: AUDIOS ---
with tab_audios:
    st.header("Banco de Audios")
    
    modo_audio = st.radio("Elige cómo añadir audio:", ["Subir archivo existente", "Grabar en vivo desde el micro"])
    
    audio_bytes = None
    
    if modo_audio == "Subir archivo existente":
        archivo_subido = st.file_uploader("Sube un archivo (MP3/WAV)", type=["mp3", "wav"])
        if archivo_subido:
            audio_bytes = archivo_subido.read()
    
    else:
        st.write("Presiona el botón para grabar (el cuadro cambiará cuando detengas la grabación):")
        # Grabador nativo estable
        grabacion = mic_recorder(
            start_prompt="🔴 Iniciar Grabación",
            stop_prompt="⏹️ Detener y Procesar",
            just_once=False,
            key='grabador_banda'
        )
        if grabacion:
            audio_bytes = grabacion['bytes']
        
    nombre_audio = st.text_input("Nombre de la pista / Idea:")
    categoria = st.selectbox("Categoría", ["Riff suelto", "Ensayo completo", "Maqueta", "Mezcla"])
    
    if st.button("Guardar Audio en el Banco", key="btn_audio"):
        if audio_bytes and nombre_audio:
            st.session_state.audios.append({
                "nombre": nombre_audio,
                "categoria": categoria,
                "usuario": usuario_actual,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "archivo": audio_bytes
            })
            st.success(f"¡'{nombre_audio}' guardado con éxito!")
        else:
            st.warning("Por favor, asegúrate de haber grabado/subido un audio y ponerle un nombre.")
            
    st.write("---")
    st.subheader("Audios de la Banda")
    if not st.session_state.audios:
        st.info("Aún no hay audios guardados.")
    else:
        for aud in reversed(st.session_state.audios):
            with st.expander(f"🎵 {aud['nombre']} ({aud['categoria']}) - por {aud['usuario']}"):
                st.write(f"Subido/Grabado el: {aud['fecha']}")
                st.audio(aud['archivo'], format='audio/wav')

# --- APARTADO: MENSAJES ---
with tab_mensajes:
    st.header("Muro de Control")
    nuevo_msg = st.text_area("Escribe una idea, propuesta o letra de canción:")
    if st.button("Enviar al Muro", key="btn_msg"):
        if nuevo_msg.strip():
            st.session_state.mensajes.append({
                "usuario": usuario_actual,
                "texto": nuevo_msg,
                "fecha": datetime.now().strftime("%H:%M - %Y-%m-%d")
            })
            st.rerun()

    st.write("---")
    for msg in reversed(st.session_state.mensajes):
        st.markdown(f"**{msg['usuario']}** <small style='color:gray;'>{msg['fecha']}</small>", unsafe_allow_html=True)
        st.info(msg['texto'])

# --- APARTADO: FECHAS ---
with tab_fechas:
    st.header("Agenda del Rock")
    col1, col2 = st.columns(2)
    with col1:
        fecha_evento = st.date_input("Fecha del evento")
        tipo_evento = st.selectbox("Tipo de evento", ["Ensayo", "Concierto", "Grabación", "Reunión"])
    with col2:
        descripcion_evento = st.text_input("Detalles")
    
    if st.button("Agendar Fecha", key="btn_fecha"):
        if descripcion_evento:
            st.session_state.fechas.append({
                "Fecha": fecha_evento.strftime("%Y-%m-%d"),
                "Tipo": tipo_evento,
                "Detalles": descripcion_evento,
                "Creado por": usuario_actual
            })
            st.success("¡Fecha anotada!")
            st.rerun()
            
    st.write("---")
    st.subheader("Próximos Compromisos")
    if not st.session_state.fechas:
        st.info("No hay fechas programadas.")
    else:
        df_fechas = pd.DataFrame(st.session_state.fechas)
        st.dataframe(df_fechas.sort_values(by="Fecha"), use_container_width=True)

