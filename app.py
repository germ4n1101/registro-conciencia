import streamlit as st
from sqlalchemy import create_engine, text

# Crear conexión usando Secrets
engine = create_engine(st.secrets["DB_URL"])

# Funciones para la base
def create_user(username, password):
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO users (username, password) VALUES (:u, :p)"),
            {"u": username, "p": password}
        )

def check_user(username, password):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE username = :u AND password = :p"),
            {"u": username, "p": password}
        )
        return result.first() is not None

def save_reflection(username, reflection):
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO reflections (username, reflection) VALUES (:u, :r)"),
            {"u": username, "r": reflection}
        )

# Ejemplo de uso
st.title("Registro de Conciencia")

menu = st.sidebar.selectbox("Menú", ["Registrar", "Login", "Nueva reflexión"])

if menu == "Registrar":
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Crear cuenta"):
        create_user(user, pwd)
        st.success("Usuario creado con éxito")

elif menu == "Login":
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if check_user(user, pwd):
            st.session_state["usuario"] = user
            st.success("Login exitoso")
        else:
            st.error("Usuario o contraseña incorrectos")

elif menu == "Nueva reflexión":
    if "usuario" in st.session_state:
        refl = st.text_area("Escribe tu reflexión")
        if st.button("Guardar"):
            save_reflection(st.session_state["usuario"], refl)
            st.success("Reflexión guardada")
    else:
        st.warning("Debes iniciar sesión primero")

