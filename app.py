# --- PARTE PARA VERIFICAR LA CONEXIÓN ---
st.subheader("Diagnóstico de Conexión")
try:
    res_test = requests.get(f"{BASE_URL}/rest/v1/mensajes", headers=headers_api)
    st.write(f"Código de respuesta: {res_test.status_code}")
    if res_test.status_code == 200:
        st.success("¡Conexión con Supabase OK!")
    else:
        st.error(f"Error: {res_test.text}")
except Exception as e:
    st.error(f"Fallo de red: {e}")
