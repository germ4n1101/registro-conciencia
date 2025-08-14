import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Conexión a Supabase usando secrets
DB_URL = st.secrets["DB_URL"]
DB_KEY = st.secrets["DB_KEY"]

supabase: Client = create_client(DB_URL, DB_KEY)

# ------------------ Funciones ------------------
def registrar_usuario(usuario, clave):
    existe = supabase.table("usuarios").select("*").eq("usuario", usuario).execute()
    if existe.data:
        return False, "❌ El usuario ya existe."
    supabase.table("usuarios").insert({"usuario": usuario, "clave": clave}).execute()
    return True, "✅ Usuario registrado con éxito."

def login_usuario(usuario, clave):
    datos = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("clave", clave).execute()
    if datos.data:
        return True
    return False

def guardar_pregunta(usuario, pregunta):
    supabase.table("preguntas").insert({"usuario": usuario, "pregunta": pregunta}).execute()

def obtener_preguntas():
    datos = supabase.table("preguntas").select("*").execute()
    return pd.DataFrame(datos.data)

# ------------------ UI ------------------
st.title("📋 Registro y Preguntas con Supabase")

# Sesión de usuario
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario:
    st.success(f"Has iniciado sesión como **{st.session_state.usuario}**")

    pregunta = st.text_input("Escribe tu pregunta:")
    if st.button("Guardar pregunta"):
        if pregunta.strip():
            guardar_pregunta(st.session_state.usuario, pregunta)
            st.success("Pregunta guardada ✅")
        else:
            st.warning("Escribe algo antes de guardar.")

    # Mostrar preguntas en tabla con paginación y búsqueda
    st.subheader("📜 Lista de preguntas")
    df = obtener_preguntas()
    if not df.empty:
        busqueda = st.text_input("🔍 Buscar en las preguntas:")
        if busqueda:
            df = df[df["pregunta"].str.contains(busqueda, case=False)]
        st.dataframe(df)
    else:
        st.info("No hay preguntas registradas.")

    if st.button("Cerrar sesión"):
        st.session_state.usuario = None

else:
    tab1, tab2 = st.tabs(["🔑 Iniciar sesión", "📝 Registrarse"])

    with tab1:
        usuario = st.text_input("Usuario", key="login_usuario")
        clave = st.text_input("Clave", type="password", key="login_clave")
        if st.button("Entrar"):
            if login_usuario(usuario, clave):
                st.session_state.usuario = usuario
                st.experimental_rerun()
            else:
                st.error("Usuario o clave incorrectos ❌")

    with tab2:
        usuario = st.text_input("Nuevo usuario", key="reg_usuario")
        clave = st.text_input("Nueva clave", type="password", key="reg_clave")
        if st.button("Registrar"):
            ok, msg = registrar_usuario(usuario, clave)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
