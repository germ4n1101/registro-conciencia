import streamlit as st
import cohere
import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

# =========================
# Conexión a la base de datos
# =========================
DB_URL = st.secrets["DB_URL"]
engine = create_engine(DB_URL)
metadata = MetaData()

# Tabla de usuarios
users_table = Table(
    "usuarios", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("password", String, nullable=False)
)

# Tabla de reflexiones
reflexiones_table = Table(
    "reflexiones", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False),
    Column("fecha", DateTime, default=datetime.datetime.utcnow),
    Column("texto", Text, nullable=False)
)

# Crear tablas si no existen
metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session_db = Session()

# =========================
# Funciones de base de datos
# =========================
def registrar_usuario(username, password):
    hashed_password = generate_password_hash(password)
    try:
        ins = users_table.insert().values(username=username, password=hashed_password)
        engine.execute(ins)
        return True
    except SQLAlchemyError:
        return False

def verificar_usuario(username, password):
    sel = users_table.select().where(users_table.c.username == username)
    result = engine.execute(sel).fetchone()
    if result and check_password_hash(result["password"], password):
        return True
    return False

def guardar_reflexion(username, texto):
    ins = reflexiones_table.insert().values(username=username, texto=texto, fecha=datetime.datetime.now())
    engine.execute(ins)

def obtener_reflexiones(username):
    sel = reflexiones_table.select().where(reflexiones_table.c.username == username).order_by(reflexiones_table.c.fecha.desc())
    return engine.execute(sel).fetchall()

# =========================
# Cohere Config
# =========================
co = cohere.Client(st.secrets["COHERE_API_KEY"])

def generar_reflexion(texto_usuario):
    response = co.generate(
        model="command",
        prompt=f"Genera una reflexión breve y motivadora basada en: {texto_usuario}",
        max_tokens=100
    )
    return response.generations[0].text.strip()

# =========================
# Interfaz Streamlit
# =========================
st.title("🧠 Registro de Conciencia")

menu = ["Login", "Registro"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Registro":
    st.subheader("Crear nueva cuenta")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Registrar"):
        if registrar_usuario(username, password):
            st.success("Usuario registrado exitosamente")
        else:
            st.error("El usuario ya existe o hubo un error")

elif choice == "Login":
    st.subheader("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Login"):
        if verificar_usuario(username, password):
            st.success(f"Bienvenido {username}")

            texto_usuario = st.text_area("Escribe algo para reflexionar")
            if st.button("Generar reflexión"):
                reflexion = generar_reflexion(texto_usuario)
                guardar_reflexion(username, reflexion)
                st.success(f"Reflexión generada: {reflexion}")

            st.subheader("📜 Historial de Reflexiones")
            for r in obtener_reflexiones(username):
                st.write(f"{r['fecha'].strftime('%Y-%m-%d %H:%M:%S')} - {r['texto']}")

        else:
            st.error("Usuario o contraseña incorrectos")

