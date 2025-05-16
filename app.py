import streamlit as st
import yaml
import os
import cohere
import hashlib
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘")

# Leer usuarios desde archivo YAML
USERS_FILE = "usuarios.yaml"

def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

def guardar_usuarios(usuarios):
    with open(USERS_FILE, "w") as f:
        yaml.dump(usuarios, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Autenticación
usuarios = cargar_usuarios()

if "usuario_autenticado" not in st.session_state:
    st.session_state["usuario_autenticado"] = None

st.sidebar.title("🔐 Autenticación")
modo = st.sidebar.radio("¿Tienes una cuenta?", ("Iniciar sesión", "Registrarse"))

if modo == "Registrarse":
    email = st.sidebar.text_input("Correo electrónico")
    password = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Crear cuenta"):
        if email in usuarios:
            st.sidebar.warning("⚠️ El usuario ya existe.")
        else:
            usuarios[email] = {"password": hash_password(password)}
            guardar_usuarios(usuarios)
            st.sidebar.success("✅ Usuario registrado. Ahora inicia sesión.")

else:
    email = st.sidebar.text_input("Correo electrónico")
    password = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Iniciar sesión"):
        if email in usuarios and usuarios[email]["password"] == hash_password(password):
            st.session_state["usuario_autenticado"] = email
            st.experimental_rerun()  # 🔁 Redirecciona a las preguntas
        else:
            st.sidebar.error("❌ Credenciales incorrectas.")

# Si no está autenticado, se detiene aquí
if not st.session_state["usuario_autenticado"]:
    st.stop()

# Conexión a Cohere
try:
    cohere_api_key = st.secrets["cohere"]["api_key"]
    co = cohere.Client(cohere_api_key)
except KeyError:
    st.error("❌ No se encontró la clave API de Cohere en .streamlit/secrets.toml.")
    st.stop()

# Título
st.title("🧘 Registro de Conciencia")
st.markdown("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

# Preguntas
estado_animo = st.text_input("1. ¿Cómo te sientes hoy?")
situacion = st.text_input("2. ¿Qué ha estado ocupando tus pensamientos últimamente?")
agradecimiento = st.text_input("3. ¿Qué agradeces hoy?")
meta = st.text_input("4. ¿Qué te gustaría lograr o mejorar?")

# Guardar y generar reflexión
if st.button("Guardar y reflexionar"):
    if not any([estado_animo, situacion, agradecimiento, meta]):
        st.warning("⚠️ Por favor responde al menos una pregunta.")
    else:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada = f"""
        Fecha: {fecha}
        Usuario: {st.session_state["usuario_autenticado"]}
        Estado de ánimo: {estado_animo}
        Situación actual: {situacion}
        Agradecimiento: {agradecimiento}
        Meta: {meta}
        """
        with open("registro_conciencia.txt", "a", encoding="utf-8") as f:
            f.write(entrada + "\n" + "-"*40 + "\n")

        st.success("✅ Entrada guardada y analizada por la IA.")

        prompt_ia = (
            f"Soy una persona reflexiva. Hoy escribí:\n\n"
            f"Estado de ánimo: {estado_animo}\n"
            f"Situación actual: {situacion}\n"
            f"Agradecimiento: {agradecimiento}\n"
            f"Meta: {meta}\n\n"
            f"Por favor genera una reflexión amable, positiva y consciente basada en esta información."
        )

        try:
            respuesta = co.chat(
                model="command-nightly",
                message=prompt_ia
            )
            st.subheader("🧠 Reflexión de German para ti")
            st.write(respuesta.text)
        except Exception as e:
            st.error(f"⚠️ Error al generar reflexión: {e}")
