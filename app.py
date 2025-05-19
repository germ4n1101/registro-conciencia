import streamlit as st
import yaml
import os
import cohere
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘")

# Branding: Logo
st.image("images/logo.png", use_container_width=True)
st.image("images/portada.jpg", use_column_width=True)

# Branding: CSS personalizado
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
    </style>
""", unsafe_allow_html=True)

# Imagen de portada (opcional)
# ... Resto de tu código ...

st.sidebar.title("Menú de navegación")
seccion = st.sidebar.radio(
    "Ir a:",
    ("Registro", "Historial", "Configuración")
)
if seccion == "Registro":
    # Aquí va el código para el registro de conciencia (las preguntas y reflexión)
    # Ejemplo:
    st.title("🧘 Registro de Conciencia")
    # ... resto del código del registro ...

elif seccion == "Historial":
    # Aquí va el código para mostrar el historial
    st.title("📜 Historial de Reflexiones")
    # ... resto del código del historial ...

elif seccion == "Configuración":
    # Aquí va el código para la configuración
    st.title("⚙️ Configuración")
    if st.button("Cerrar sesión"):
        st.session_state.usuario_autenticado = None
        st.session_state.login_exitoso = False
        st.session_state.es_admin = False
        st.rerun()  # Recuerda reemplazar st.experimental_rerun() por st.rerun()
    # ... resto del código de configuración ...


# 👇 Agrega aquí tu CSS personalizado
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f8;
    }
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

# --- API de Cohere ---
try:
    cohere_api_key = st.secrets["cohere"]["api_key"]
    co = cohere.Client(cohere_api_key)
except KeyError:
    st.error("❌ No se encontró la clave API de Cohere en .streamlit/secrets.toml.")
    st.stop()

# --- Archivos de usuarios y registros ---
USERS_FILE = "usuarios.yaml"
REGISTROS_DIR = "registros"
os.makedirs(REGISTROS_DIR, exist_ok=True)

# --- Funciones auxiliares ---
def cargar_usuarios():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def guardar_usuarios(usuarios):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(usuarios, f, allow_unicode=True)

def guardar_registro(email, texto):
    filename = os.path.join(REGISTROS_DIR, f"{email.replace('@', '_')}.txt")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(texto + "\n" + "-"*40 + "\n")

def obtener_registros(email):
    filename = os.path.join(REGISTROS_DIR, f"{email.replace('@', '_')}.txt")
    if not os.path.exists(filename):
        return "No tienes registros previos."
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def generar_reflexion(prompt):
    if not prompt.strip():
        return "No se puede generar una reflexión sin contenido."
    try:
        response = co.chat(
            model="command-nightly",
            message=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error al generar reflexión: {e}"

def cambiar_contrasena(email, nueva_contrasena):
    usuarios = cargar_usuarios()
    if email in usuarios:
        usuarios[email] = nueva_contrasena
        guardar_usuarios(usuarios)
        return True
    return False

# --- Estado de sesión ---
if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = None
if "login_exitoso" not in st.session_state:
    st.session_state.login_exitoso = False
if "es_admin" not in st.session_state:
    st.session_state.es_admin = False

# --- Interfaz de Login y Registro ---
if not st.session_state.usuario_autenticado:
    st.subheader("🔐 Inicia sesión o regístrate")
    tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tab_login:
        email = st.text_input("Correo electrónico", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Iniciar sesión"):
            usuarios = cargar_usuarios()
            if email in usuarios and usuarios[email] == password:
                st.session_state.usuario_autenticado = email
                st.session_state.login_exitoso = True
                st.session_state.es_admin = email == "admin@admin.com"
                st.rerun()
            else:
                st.error("❌ Credenciales inválidas.")

    with tab_registro:
        new_email = st.text_input("Correo electrónico", key="reg_email")
        new_password = st.text_input("Contraseña", type="password", key="reg_pass")
        if st.button("Registrarse"):
            usuarios = cargar_usuarios()
            if new_email in usuarios:
                st.warning("⚠️ El correo ya está registrado.")
            else:
                usuarios[new_email] = new_password
                guardar_usuarios(usuarios)
                st.session_state.usuario_autenticado = new_email
                st.session_state.login_exitoso = True
                st.success("✅ Usuario registrado exitosamente.")
                st.rerun()

# --- Interfaz Principal Post Login ---
else:
    st.title("🧘 Registro de Conciencia")
    st.markdown("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

    estado_animo = st.text_input("1. ¿Cómo te sientes hoy?")
    situacion = st.text_input("2. ¿Qué ha estado ocupando tus pensamientos últimamente?")
    agradecimiento = st.text_input("3. ¿Qué agradeces hoy?")
    meta = st.text_input("4. ¿Qué te gustaría lograr o mejorar?")

    if st.button("Guardar y reflexionar"):
        if not any([estado_animo, situacion, agradecimiento, meta]):
            st.warning("Por favor responde al menos una pregunta.")
        else:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entrada = f"""
Fecha: {fecha}
Estado de ánimo: {estado_animo}
Situación actual: {situacion}
Agradecimiento: {agradecimiento}
Meta: {meta}
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

            st.subheader("🧠 Reflexión para ti")
            st.write(reflexion)

    st.markdown("---")
    with st.expander("📜 Ver mis reflexiones pasadas"):
        registros = obtener_registros(st.session_state.usuario_autenticado)
        st.text_area("Historial de reflexiones", registros, height=300)

    st.markdown("---")
    st.subheader("🔧 Configuración")
    if st.button("Cerrar sesión"):
        st.session_state.usuario_autenticado = None
        st.session_state.login_exitoso = False
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
        st.markdown("---")
        st.subheader("👤 Usuarios registrados (Admin)")
        usuarios = cargar_usuarios()
        st.write("Total usuarios:", len(usuarios))
        for correo in usuarios:
            st.markdown(f"- {correo}")
