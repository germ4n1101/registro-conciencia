import streamlit as st
import yaml
import os
import cohere
from datetime import datetime
import hashlib

# Configuración de la página
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘", layout="centered")

# --- Inicialización ---
USERS_FILE = "usuarios.yaml"
ENTRADAS_DIR = "entradas"
os.makedirs(ENTRADAS_DIR, exist_ok=True)

# Cohere API
try:
    cohere_api_key = st.secrets["cohere"]["api_key"]
    cohere_client = cohere.Client(cohere_api_key)
except KeyError:
    st.error("❌ No se encontró la clave API de Cohere en .streamlit/secrets.toml.")
    st.stop()

# --- Funciones auxiliares ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    return {}

def guardar_usuarios(usuarios):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        yaml.dump(usuarios, file)

def generar_reflexion(prompt):
    try:
        response = cohere_client.generate(
            model="command",
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"Error al generar la reflexión: {e}"

# Estado de sesión
if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = None

# --- Login / Registro ---
if not st.session_state.usuario_autenticado:
    with st.sidebar:
        st.header("🔐 Iniciar sesión / Registrarse")
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")

        usuarios = cargar_usuarios()

        col1, col2 = st.columns(2)

        if col1.button("Iniciar sesión"):
            if email in usuarios and usuarios[email]["password"] == hash_password(password):
                st.session_state.usuario_autenticado = email
                st.success("✅ Inicio de sesión exitoso. Puedes comenzar abajo.")
            else:
                st.error("❌ Correo o contraseña incorrectos.")

        if col2.button("Registrarse"):
            if email in usuarios:
                st.warning("⚠️ Este correo ya está registrado.")
            else:
                usuarios[email] = {"password": hash_password(password)}
                guardar_usuarios(usuarios)
                st.success("✅ Registro exitoso. Ahora puedes iniciar sesión.")

    st.stop()

# --- Pantalla principal ---
st.title("🧘 Registro de Conciencia")
st.markdown("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

estado_animo = st.text_input("1. ¿Cómo te sientes hoy?")
situacion = st.text_input("2. ¿Qué ha estado ocupando tus pensamientos últimamente?")
agradecimiento = st.text_input("3. ¿Qué agradeces hoy?")
meta = st.text_input("4. ¿Qué te gustaría lograr o mejorar?")

archivo_usuario = os.path.join(ENTRADAS_DIR, f"{st.session_state.usuario_autenticado}.txt")

if st.button("Guardar y reflexionar"):
    if not any([estado_animo, situacion, agradecimiento, meta]):
        st.warning("⚠️ Por favor responde al menos una pregunta.")
    else:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada = f"""Fecha: {fecha}
Estado de ánimo: {estado_animo}
Situación actual: {situacion}
Agradecimiento: {agradecimiento}
Meta: {meta}
{'-'*40}
"""

        with open(archivo_usuario, "a", encoding="utf-8") as f:
            f.write(entrada)

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
            respuesta = cohere_client.chat(
                model="command-nightly",
                message=prompt_ia
            )
            st.subheader("🧠 Reflexión generada")
            st.write(respuesta.text)
        except Exception as e:
            st.error(f"⚠️ Error con la IA: {e}")

# --- Mostrar historial del usuario ---
st.divider()
st.subheader("📜 Mis registros anteriores")

if os.path.exists(archivo_usuario):
    with open(archivo_usuario, "r", encoding="utf-8") as f:
        contenido = f.read()
        if contenido.strip():
            st.text_area("🗂️ Historial personal", contenido, height=300)
        else:
            st.info("No tienes registros aún.")
else:
    st.info("No se ha creado tu archivo de registro.")
