import streamlit as st
from supabase import create_client
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from werkzeug.security import generate_password_hash, check_password_hash

# ===== CONFIGURACIÓN SUPABASE =====
DB_URL = st.secrets["DB_URL"]
DB_KEY = st.secrets["DB_KEY"]
supabase = create_client(DB_URL, DB_KEY)

st.set_page_config(page_title="Registro de Conciencia - CRUD Supabase", layout="wide")

# ===== FUNCIONES DE USUARIO =====
def registrar_usuario(username, password):
    hashed_pw = generate_password_hash(password)
    data, _ = supabase.table("usuarios").insert({"username": username, "password": hashed_pw}).execute()
    return data

def verificar_usuario(username, password):
    result = supabase.table("usuarios").select("*").eq("username", username).execute()
    if result.data:
        stored_pw = result.data[0]["password"]
        return check_password_hash(stored_pw, password)
    return False

# ===== FUNCIONES CRUD PREGUNTAS =====
def insertar_pregunta(usuario, pregunta):
    supabase.table("preguntas").insert({"usuario": usuario, "pregunta": pregunta}).execute()

def obtener_preguntas(usuario):
    result = supabase.table("preguntas").select("*").eq("usuario", usuario).execute()
    return pd.DataFrame(result.data) if result.data else pd.DataFrame(columns=["id", "usuario", "pregunta"])

# ===== LOGIN / REGISTRO =====
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.subheader("Inicia sesión o regístrate")

    tab_login, tab_registro = st.tabs(["🔑 Iniciar Sesión", "🆕 Registrarse"])

    with tab_login:
        username = st.text_input("Usuario", key="login_user")
        password = st.text_input("Contraseña", type="password", key="login_pw")
        if st.button("Ingresar"):
            if verificar_usuario(username, password):
                st.session_state.usuario = username
                st.success("✅ Inicio de sesión exitoso")
                st.experimental_rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")

    with tab_registro:
        new_user = st.text_input("Nuevo usuario", key="reg_user")
        new_pw = st.text_input("Nueva contraseña", type="password", key="reg_pw")
        if st.button("Registrarme"):
            if new_user and new_pw:
                registrar_usuario(new_user, new_pw)
                st.success("✅ Usuario registrado, ahora inicia sesión")
            else:
                st.warning("Por favor llena todos los campos")

else:
    st.title(f"Registro de Conciencia - Bienvenido {st.session_state.usuario}")

    # Formulario para agregar preguntas
    pregunta = st.text_input("Escribe tu pregunta o reflexión")
    if st.button("Guardar"):
        if pregunta:
            insertar_pregunta(st.session_state.usuario, pregunta)
            st.success("✅ Pregunta guardada")
        else:
            st.warning("Por favor escribe algo antes de guardar")

    # Mostrar preguntas con tabla interactiva
    df = obtener_preguntas(st.session_state.usuario)

    if not df.empty:
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
        gb.configure_default_column(filter=True, sortable=True, resizable=True)
        grid_options = gb.build()
        AgGrid(df, gridOptions=grid_options, height=300)
    else:
        st.info("No hay preguntas registradas aún.")

    if st.button("Cerrar sesión"):
        st.session_state.usuario = None
        st.experimental_rerun()


