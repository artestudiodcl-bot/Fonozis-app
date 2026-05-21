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

# Estilo personalizado general (Fondo oscuro de estudio)
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    h1, h2, h3 { color: #FF4B4B !important; }
    
    /* Estilos del chat tipo teléfono */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding: 10px;
        margin-bottom: 20px;
    }
    .msg-row {
        display: flex;
        width: 100%;
        margin-bottom: 4px;
    }
    .msg-row.derecha {
        justify-content: flex-end;
    }
    .msg-row.izquierda {
        justify-content: flex-start;
    }
    .burbuja {
        max-width: 75%;
        padding: 12px 16px;
        border-radius: 18px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 14px;
        line-height: 1.4;
        position: relative;
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    .derecha .burbuja {
        background-color: #007AFF;
        color: white;
        border-bottom-right-radius: 4px;
    }
    .izquierda .burbuja {
        background-color: #26262b;
        color: #e4e6eb;
        border-bottom-left-radius: 4px;
    }
    .msg-meta {
        font-size: 11px;
        margin-bottom: 4px;
        display: block;
        opacity: 0.7;
    }
    .derecha .msg-meta {
        text-align: right;
        color: #a1caff;
    }
    .izquierda .msg-meta {
        text-align: left;
        color: #b0b3b8;
    }
    </style>
    """, unsafe_allow_html=True)

# INICIALIZACIÓN DEL ESTADO
if 'audios' not in st.session_state:
    st.session_state.audios = []
if 'mensajes' not in st.session_state:
    st.session_state.mensajes = [
        {"usuario": "Sistema", "texto": "¡Bienvenidos al Muro de Control de la banda!", "fecha": "20:26"}
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
        st.write("Presiona para grabar. Recuerda aceptar los permisos de micrófono si el navegador los pide:")
        
        # Grabador optimizado para compatibilidad móvil
        grabacion = mic_recorder(
            start_prompt="🔴 Iniciar Grabación",
            stop_prompt="⏹️ Detener y Procesar",
            just_once=False,
            use_container_width=True,
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
                # Autodetecta el contenedor nativo
                st.audio(aud['archivo'])

# --- APARTADO: MENSAJES ---
with tab_mensajes:
    st.header("Muro de Control")
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.mensajes:
        if msg['usuario'] == usuario_actual:
            clase_lado = "derecha"
            nombre_mostrar = "Tú"
        else:
            clase_lado = "izquierda"
            nombre_mostrar = msg['usuario']
            
        html_burbuja = f"""
        <div class="msg-row {clase_lado}">
            <div class="burbuja">
                <span class="msg-meta">{nombre_mostrar} • {msg['fecha']}</span>
                {msg['texto']}
            </div>
        </div>
        """
        st.markdown(html_burbuja, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("---")
    
    def enviar_y_limpiar():
        texto_ingresado = st.session_state.caja_chat.strip()
        if texto_ingresado:
            st.session_state.mensajes.append({
                "usuario": usuario_actual,
                "texto": texto_ingresado,
                "fecha": datetime.now().strftime("%H:%M")
            })
        st.session_state.caja_chat = ""

    st.text_area(
        "Escribe un mensaje para la banda...", 
        placeholder="Introduce tu idea o propuesta aquí...",
        key="caja_chat"
    )
    st.button("Enviar Mensaje 🚀", on_click=enviar_y_limpiar)

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
