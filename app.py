import streamlit as st
import psycopg2
import hashlib
import datetime

# Configuración de la conexión a PostgreSQL en Supabase
DB_HOST = "db.fploheqxhzpihgexlrkr.supabase.co"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "NQY5cSDBXhM2dQiJ"
DB_PORT = "5432"

# Conexión
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

# Crear tablas si no existen
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historiales (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            fecha TIMESTAMP NOT NULL,
            consulta TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES usuarios(username) ON DELETE CASCADE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# Hash de contraseñas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Registrar usuario
def register_user(username, password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)",
                    (username, hash_password(password)))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        cur.close()
        conn.close()
        return False

# Verificar usuario
def verify_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM usuarios WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row and row[0] == hash_password(password):
        return True
    return False

# Guardar histórico
def save_history(username, consulta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO historiales (username, fecha, consulta) VALUES (%s, %s, %s)",
                (username, datetime.datetime.now(), consulta))
    conn.commit()
    cur.close()
    conn.close()

# Obtener histórico
def get_history(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT fecha, consulta FROM historiales WHERE username = %s ORDER BY fecha DESC", (username,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

# Interfaz de Streamlit
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧠", layout="centered")

st.title("🧠 Registro de Conciencia")

menu = ["Login", "Registro"]
choice = st.sidebar.selectbox("Menú", menu)

init_db()

if choice == "Registro":
    st.subheader("Crear nueva cuenta")
    new_user = st.text_input("Usuario")
    new_pass = st.text_input("Contraseña", type="password")
    if st.button("Registrar"):
        if register_user(new_user, new_pass):
            st.success("Usuario registrado con éxito. Ahora inicia sesión.")
        else:
            st.error("El usuario ya existe. Elige otro nombre.")

elif choice == "Login":
    st.subheader("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if verify_user(username, password):
            st.success(f"Bienvenido {username}")
            consulta = st.text_area("Escribe tu reflexión o evaluación del día")
            if st.button("Guardar reflexión"):
                if consulta.strip():
                    save_history(username, consulta)
                    st.success("Reflexión guardada.")
                else:
                    st.warning("Escribe algo antes de guardar.")
            st.subheader("📜 Historial")
            history = get_history(username)
            if history:
                for fecha, texto in history:
                    st.write(f"**{fecha.strftime('%Y-%m-%d %H:%M')}** - {texto}")
            else:
                st.info("Aún no tienes registros.")
        else:
            st.error("Usuario o contraseña incorrectos.")
