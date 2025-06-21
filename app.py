# Versión actualizada de tu app con persistencia real usando SQLite
import streamlit as st
import sqlite3
import cohere
from datetime import datetime
import os

st.set_page_config(page_title="Encuentra claridad con solo 4 preguntas", page_icon="🧘")

# --- Estilos ---
st.markdown("""
    <style>
    .main { background-color: #f4f6f8; }
    .stButton>button {
        background-color: #6c63ff;
        color: white;
        border-radius: 8px;
        font-size: 18px;
        padding: 10px 24px;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #6c63ff;
    }
    </style>
""", unsafe_allow_html=True)

# --- API Cohere ---
try:
    cohere_api_key = st.secrets["cohere"]["api_key"]
    co = cohere.Client(cohere_api_key)
except KeyError:
    st.error("❌ No se encontró la clave API de Cohere en .streamlit/secrets.toml.")
    st.stop()

# --- Base de datos SQLite ---
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        fecha TEXT NOT NULL,
        entrada TEXT NOT NULL
    )
''')

conn.commit()

# --- Funciones auxiliares ---
def registrar_usuario(email, password):
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def validar_usuario(email, password):
    c.execute("SELECT password FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    return result and result[0] == password

def cambiar_contrasena(email, nueva_pass):
    c.execute("UPDATE users SET password = ? WHERE email = ?", (nueva_pass, email))
    conn.commit()
    return c.rowcount > 0

def guardar_registro(email, entrada):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO registros (email, fecha, entrada) VALUES (?, ?, ?)", (email, fecha, entrada))
    conn.commit()

def obtener_registros(email):
    c.execute("SELECT fecha, entrada FROM registros WHERE email = ? ORDER BY fecha DESC", (email,))
    rows = c.fetchall()
    return "\n\n---\n\n".join([f"Fecha: {f}\n{e}" for f, e in rows]) or "No tienes registros previos."

def generar_reflexion(prompt):
    if not prompt.strip():
        return "No se puede generar una reflexión sin contenido."
    try:
        response = co.chat(model="command-nightly", message=prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error al generar reflexión: {e}"

# --- Estado de sesión ---
if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = None
if "es_admin" not in st.session_state:
    st.session_state.es_admin = False

# --- Login y registro ---
if not st.session_state.usuario_autenticado:
    st.subheader("🔐 Inicia sesión o regístrate")
    tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tab_login:
        email = st.text_input("Correo electrónico", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Iniciar sesión"):
            if validar_usuario(email, password):
                st.session_state.usuario_autenticado = email
                st.session_state.es_admin = email == "admin@admin.com"
                st.rerun()
            else:
                st.error("❌ Credenciales inválidas.")

    with tab_registro:
        new_email = st.text_input("Correo electrónico", key="reg_email")
        new_password = st.text_input("Contraseña", type="password", key="reg_pass")
        if st.button("Registrarse"):
            if registrar_usuario(new_email, new_password):
                st.success("✅ Usuario registrado exitosamente.")
                st.session_state.usuario_autenticado = new_email
                st.session_state.es_admin = new_email == "admin@admin.com"
                st.rerun()
            else:
                st.warning("⚠️ El correo ya está registrado.")

# --- App principal ---
else:
    st.sidebar.title("Menú de navegación")
    seccion = st.sidebar.radio("Ir a:", ("Registro", "Historial", "Configuración"))

    if seccion == "Registro":
        st.title("🧘 Encuentra claridad con solo 4 preguntas")
        estado_animo = st.text_input("1. ¿Cómo te sientes hoy?")
        situacion = st.text_input("2. ¿Qué ha estado ocupando tus pensamientos últimamente?")
        agradecimiento = st.text_input("3. ¿Qué agradeces hoy?")
        meta = st.text_input("4. ¿Qué te gustaría lograr o mejorar?")

        if st.button("Guardar y reflexionar"):
            if not any([estado_animo, situacion, agradecimiento, meta]):
                st.warning("Por favor responde al menos una pregunta.")
            else:
                entrada = f"""
Estado de ánimo: {estado_animo}
Situación actual: {situacion}
Agradecimiento: {agradecimiento}
Meta: {meta}"
"""
                guardar_registro(st.session_state.usuario_autenticado, entrada)
                st.success("✅ Entrada guardada y analizada por la IA.")

                prompt_ia = (
                    f"Soy una persona reflexiva. Hoy escribí:\n\n"
                    f"Estado de ánimo: {estado_animo}\n"
                    f"Situación actual: {situacion}\n"
                    f"Agradecimiento: {agradecimiento}\n"
                    f"Meta: {meta}\n\n"
                    f"Por favor genera una reflexión amable, positiva y consciente basada en esta información."
                )
                reflexion = generar_reflexion(prompt_ia)

                st.subheader("🧠 Reflexión para ti inspirado por Germán")
                st.write(reflexion)

    elif seccion == "Historial":
        st.title("📜 Historial de Reflexiones")
        registros = obtener_registros(st.session_state.usuario_autenticado)
        st.text_area("Historial de reflexiones", registros, height=300)

    elif seccion == "Configuración":
        st.title("⚙️ Configuración")
        if st.button("Cerrar sesión"):
            st.session_state.usuario_autenticado = None
            st.session_state.es_admin = False
            st.rerun()

        with st.expander("🔐 Cambiar contraseña"):
            nueva = st.text_input("Nueva contraseña", type="password")
            if st.button("Actualizar contraseña"):
                if cambiar_contrasena(st.session_state.usuario_autenticado, nueva):
                    st.success("✅ Contraseña actualizada.")
                else:
                    st.error("❌ Error al actualizar contraseña.")

        if st.session_state.es_admin:
            st.subheader("👤 Usuarios registrados (Admin)")
            c.execute("SELECT email FROM users")
            users = c.fetchall()
            for u in users:
                st.markdown(f"- {u[0]}")

