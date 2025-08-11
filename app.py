import streamlit as st
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import re

# Conexión a Supabase
url = st.secrets["DB_URL"]
key = st.secrets["DB_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Registro de Conciencia", layout="wide")

# ====================
# Funciones auxiliares
# ====================
def email_valido(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def registrar_usuario(username, password, email):
    if not email_valido(email):
        st.error("Correo electrónico inválido.")
        return False
    hashed_password = generate_password_hash(password)
    data, error = supabase.table("usuarios").insert({
        "username": username,
        "password": hashed_password,
        "email": email
    }).execute()
    if error:
        st.error("Usuario o email ya registrado.")
        return False
    return True

def autenticar_usuario(username, password):
    user = supabase.table("usuarios").select("*").eq("username", username).execute()
    if user.data and check_password_hash(user.data[0]["password"], password):
        return True
    return False

def cambiar_contraseña(email, nueva_pass):
    if not email_valido(email):
        st.error("Correo inválido.")
        return False
    hashed_password = generate_password_hash(nueva_pass)
    resp = supabase.table("usuarios").update({"password": hashed_password}).eq("email", email).execute()
    return bool(resp.data)

def guardar_pregunta(usuario, pregunta):
    supabase.table("preguntas").insert({"usuario": usuario, "pregunta": pregunta}).execute()

def obtener_preguntas(usuario):
    data = supabase.table("preguntas").select("*").eq("usuario", usuario).order("created_at", desc=True).execute()
    return pd.DataFrame(data.data)

# ====================
# Interfaz de usuario
# ====================
menu = ["Login", "Registro", "Recuperar contraseña", "Preguntas"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Registro":
    st.subheader("Crear cuenta")
    username = st.text_input("Usuario")
    email = st.text_input("Correo")
    password = st.text_input("Contraseña", type="password")
    if st.button("Registrar"):
        if registrar_usuario(username, password, email):
            st.success("Registro exitoso. Ya puedes iniciar sesión.")

elif choice == "Login":
    st.subheader("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if autenticar_usuario(username, password):
            st.session_state["usuario"] = username
            st.success(f"Bienvenido {username}")
        else:
            st.error("Usuario o contraseña incorrectos.")

elif choice == "Recuperar contraseña":
    st.subheader("Recuperar contraseña")
    email = st.text_input("Correo")
    nueva_pass = st.text_input("Nueva contraseña", type="password")
    if st.button("Cambiar"):
        if cambiar_contraseña(email, nueva_pass):
            st.success("Contraseña cambiada con éxito.")
        else:
            st.error("No se pudo cambiar la contraseña.")

elif choice == "Preguntas":
    if "usuario" not in st.session_state:
        st.warning("Debes iniciar sesión para continuar.")
    else:
        st.subheader("Registrar pregunta/reflexión")
        pregunta = st.text_area("Escribe tu pregunta")
        if st.button("Guardar"):
            guardar_pregunta(st.session_state["usuario"], pregunta)
            st.success("Pregunta guardada.")

        st.subheader("Historial de preguntas")
        df = obtener_preguntas(st.session_state["usuario"])
        if not df.empty:
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_side_bar()
            gb.configure_default_column(filter=True, sortable=True, resizable=True)
            gridOptions = gb.build()
            AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True, theme="streamlit")
        else:
            st.info("Aún no has registrado preguntas.")

