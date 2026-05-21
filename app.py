# --- LISTAR ARCHIVOS (Actualizado) ---
st.subheader("Audios Disponibles")

# Consultamos los objetos en el bucket 'audios'
# Nota: La API REST de Supabase no lista archivos directamente desde Storage,
# pero podemos intentar listar los nombres si los guardamos en una pequeña lista
# o simplemente usamos este método para mostrar la respuesta:

url_listado = f"{BASE_URL}/storage/v1/object/list/audios"
headers = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "apikey": SUPABASE_KEY
}

res_list = requests.post(url_listado, headers=headers, json={"prefix": ""})

if res_list.status_code == 200:
    archivos = res_list.json()
    if archivos:
        for f in archivos:
            st.audio(f"{BASE_URL}/storage/v1/object/public/audios/{f['name']}")
            st.caption(f"Archivo: {f['name']}")
    else:
        st.info("La caja está vacía. ¡Sube el primer audio!")
else:
    st.warning("No pude cargar la lista de audios, pero la conexión está activa.")
