import streamlit as st
import yaml
import os
import hashlib
import cohere
from datetime import datetime

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘")

# ---------- FUNCIONES DE AUTENTICACIÓN ----------
USERS_FILE = "usuarios.yaml"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        yaml.dump(users, f)

def login_or_register():
    st.sidebar.title("🔐 Autenticación")
    menu = st.sidebar.radio("Elige una opción:", ["Iniciar sesión", "Registrarse"])

    users = load_users()

    if menu == "Registrarse":
        email = st.sidebar.text_input("Correo electrónico")
        password = st.sidebar.text_input("Contraseña", type="password")
        if st.sidebar.button("Crear cuenta"):
            if email in users:
                st.sidebar.warning("⚠️ El correo ya está registrado.")
            else:
                users[email] = {"password": hash_password(password)}
                save_users(users)
                st.sidebar.success("✅ Usuario registrado. Ahora inicia sesión.")

    if menu == "Iniciar sesión":
        email = st.sidebar.text_input("Correo electrónico")
        password = st.sidebar.text_input("Contraseña", type="password")
        if st.sidebar.button("Iniciar sesión"):
            if email in users and users[email]["password"] == hash_password(password):
                st.session_state["usuario_autenticado"] = email
                st.sidebar.success(f"¡Bienvenido, {email}!")
            else:
                st.sidebar.error("❌ Credenciales incorrectas")

# ---------- VALIDAR AUTENTICACIÓN ----------
if "usuario_autenticado" not in st.session_state:
    login_or_register()
    st.stop()

usuario_actual = st.session_state["usuario_autenticado"]

# ---------- COHERE API ----------
try:
    cohere_api_key = st.secrets["cohere"]["api_key"]
    cohere_client = cohere.Client(cohere_api_key)
except KeyError:
    st.error("❌ No se encontró la clave API de Cohere en .streamlit/secrets.toml.")
    st.stop()

def generar_reflexion(prompt):
    if not prompt or prompt.strip() == "":
        st.warning("⚠️ El contenido del prompt está vacío. Por favor completa tus respuestas.")
        return "No se puede generar una reflexión sin contenido."

    try:
        response = cohere_client.generate(
            model="command",
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except cohere.CohereError as e:
        st.error(f"❌ Error al generar reflexión: {str(e)}")
        return "Ocurrió un error al generar la reflexión con la IA."

# ---------- INTERFAZ PRINCIPAL ----------
st.title("🧘 Registro de Conciencia")
st.markdown("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

estado_animo = st.text_input("1. ¿Cómo te sientes hoy?")
situacion = st.text_input("2. ¿Qué ha estado ocupando tus pensamientos últimamente?")
agradecimiento = st.text_input("3. ¿Qué agradeces hoy?")
meta = st.text_input("4. ¿Qué te gustaría lograr o mejorar?")

# ---------- PROCESO AL GUARDAR ----------
if st.button("Guardar y reflexionar"):
    if not any([estado_animo, situacion, agradecimiento, meta]):
        st.warning("Por favor responde al menos una pregunta.")
    else:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada = f"""
Fecha: {fecha}
Usuario: {usuario_actual}
Estado de ánimo: {estado_animo}
Situación actual: {situacion}
Agradecimiento: {agradecimiento}
Meta: {meta}
"""

        os.makedirs("registros", exist_ok=True)
        filename = f"registros/{usuario_actual.replace('@', '_at_')}.txt"
        with open(filename, "a", encoding="utf-8") as archivo:
            archivo.write(entrada + "\n" + "-"*40 + "\n")

        st.success("✅ Entrada guardada y analizada por la IA.")

        try:
            prompt_ia = (
                f"Soy una persona reflexiva. Hoy escribí:\n\n"
                f"Estado de ánimo: {estado_animo}\n"
                f"Situación actual: {situacion}\n"
                f"Agradecimiento: {agradecimiento}\n"
                f"Meta: {meta}\n\n"
                f"Por favor genera una reflexión amable, positiva y consciente basada en esta información."
            )

            respuesta = cohere_client.chat(
                model="command-nightly",
                message=prompt_ia
            )

            st.subheader("🧠 Reflexión de German para ti, captura pantalla si te gusta y espero que tu vida sea la mejor desde esta reflexion")
            st.write(respuesta.text)

        except Exception as e:
            st.error(f"⚠️ Error con la IA: {e}")
