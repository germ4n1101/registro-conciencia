import streamlit as st
from sqlalchemy import create_engine, text
from datetime import datetime
import cohere

# --- CONEXIÓN BASE DE DATOS ---
engine = create_engine(st.secrets["postgresql://postgres:NQY5cSDBXhM2dQiJ@db.fploheqxhzpihgexlrkr.supabase.co:5432/postgres"])

# --- COHERE ---
co = cohere.Client(st.secrets["cohere"]["api_key"])

# --- CREAR TABLAS SI NO EXISTEN ---
def inicializar_bd():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS registros_conciencia (
                id SERIAL PRIMARY KEY,
                usuario VARCHAR(100) NOT NULL,
                fecha TIMESTAMP DEFAULT NOW(),
                reflexion TEXT
            );
        """))
        conn.commit()

inicializar_bd()

# --- FUNCIONES DE USUARIOS ---
def registrar_usuario(username, password):
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO usuarios (username, password) VALUES (:u, :p)"),
                     {"u": username, "p": password})
        conn.commit()

def validar_login(username, password):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM usuarios WHERE username=:u AND password=:p"),
                              {"u": username, "p": password}).fetchone()
        return result is not None

# --- FUNCIONES DE REFLEXIONES ---
def guardar_reflexion(usuario, reflexion):
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO registros_conciencia (usuario, fecha, reflexion) VALUES (:u, :f, :r)"),
            {"u": usuario, "f": datetime.now(), "r": reflexion}
        )
        conn.commit()

def obtener_reflexiones(usuario):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT fecha, reflexion FROM registros_conciencia WHERE usuario=:u ORDER BY fecha DESC"),
            {"u": usuario}
        ).fetchall()
    return result

# --- INTERFAZ STREAMLIT ---
st.title("🧠 Registro de Conciencia")

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    menu = st.sidebar.radio("Menú", ["Login", "Registro"])

    if menu == "Login":
        st.subheader("Iniciar Sesión")
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if validar_login(user, pwd):
                st.session_state.usuario = user
                st.success(f"Bienvenido {user}")
            else:
                st.error("Usuario o contraseña incorrectos")

    elif menu == "Registro":
        st.subheader("Crear Cuenta")
        user = st.text_input("Usuario nuevo")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Registrar"):
            try:
                registrar_usuario(user, pwd)
                st.success("Usuario registrado correctamente, ahora inicia sesión.")
            except:
                st.error("Ese usuario ya existe.")

else:
    st.sidebar.success(f"Usuario: {st.session_state.usuario}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.usuario = None
        st.experimental_rerun()

    st.subheader("Nueva Reflexión")
    reflexion = st.text_area("Escribe tu reflexión aquí")

    if st.button("Guardar Reflexión"):
        guardar_reflexion(st.session_state.usuario, reflexion)
        st.success("Reflexión guardada ✅")

    if st.button("Generar con Cohere"):
        prompt = "Escribe una breve reflexión positiva para el día de hoy."
        respuesta = co.generate(model="command", prompt=prompt, max_tokens=50)
        reflexion_auto = respuesta.generations[0].text.strip()
        guardar_reflexion(st.session_state.usuario, reflexion_auto)
        st.success("Reflexión generada y guardada ✅")
        st.write(reflexion_auto)

    st.subheader("Historial de Reflexiones")
    registros = obtener_reflexiones(st.session_state.usuario)
    for fecha, texto in registros:
        st.markdown(f"**{fecha.strftime('%Y-%m-%d %H:%M')}**: {texto}")
