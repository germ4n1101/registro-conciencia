import streamlit as st
import yaml
import os
import cohere
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# ==== Configuración inicial ====
# Configuración de cookies
cookies = EncryptedCookieManager(
    prefix="registro_conciencia/",
    password="clave-super-secreta"
)

if not cookies.ready():
    st.stop()

# Configuración de la página
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘")
st.title("🧘 Registro de Conciencia")

# Directorio para guardar registros
REGISTROS_DIR = "registros"
os.makedirs(REGISTROS_DIR, exist_ok=True)

# Cargar clave Cohere desde secrets
try:
    cohere_api_key = st.secrets["cohere"]["api_key"]
    cohere_client = cohere.Client(cohere_api_key)
except KeyError:
    st.error("❌ No se encontró la clave API de Cohere en .streamlit/secrets.toml.")
    st.stop()

# ==== Funciones ====
def cargar_usuarios():
    if not os.path.exists("usuarios.yaml"):
        return {}
    with open("usuarios.yaml", "r") as file:
        return yaml.safe_load(file) or {}

def guardar_usuarios(usuarios):
    with open("usuarios.yaml", "w") as file:
        yaml.dump(usuarios, file)

def guardar_registro(email, entrada):
    filename = os.path.join(REGISTROS_DIR, f"{email.replace('@', '_')}.txt")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(entrada + "\n" + "-" * 40 + "\n")

def obtener_registros(email):
    filename = os.path.join(REGISTROS_DIR, f"{email.replace('@', '_')}.txt")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    return "Aún no tienes reflexiones registradas."

def generar_reflexion(prompt):
    if not prompt or prompt.strip() == "":
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
        return f"Error al generar reflexión: {str(e)}"

# ==== Sesión persistente ====
if "usuario_autenticado" not in st.session_state:
    if cookies.get("usuario"):
        st.session_state.usuario_autenticado = cookies.get("usuario")

# ==== Autenticación ====
usuarios = cargar_usuarios()

if "usuario_autenticado" not in st.session_state:
    opcion = st.radio("Elige una opción", ["Iniciar sesión", "Registrarse"])

    email = st.text_input("Correo electrónico")
    password = st.text_input("Contraseña", type="password")

    if opcion == "Registrarse":
        if st.button("Crear cuenta"):
            if email in usuarios:
                st.error("❌ El usuario ya existe.")
            else:
                usuarios[email] = password
                guardar_usuarios(usuarios)
                cookies["usuario"] = email
                cookies.save()
                st.session_state.usuario_autenticado = email
                st.success("✅ Usuario creado e ingresado correctamente.")
                st.experimental_rerun()

    elif opcion == "Iniciar sesión":
        if st.button("Ingresar"):
            if usuarios.get(email) == password:
                cookies["usuario"] = email
                cookies.save()
                st.session_state.usuario_autenticado = email
                st.success("✅ Inicio de sesión exitoso. Puedes comenzar abajo.")
                st.experimental_rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")
else:
    email = st.session_state.usuario_autenticado
    st.markdown(f"👤 Sesión iniciada como: **{email}**")

    if st.button("Cerrar sesión"):
        st.session_state.usuario_autenticado = None
        cookies["usuario"] = ""
        cookies.save()
        st.success("Sesión cerrada.")
        st.experimental_rerun()

    # ==== Preguntas de entrada ====
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
            guardar_registro(email, entrada)
            st.success("✅ Entrada guardada y analizada por la IA.")

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

            st.subheader("🧠 Reflexión de German para ti")
            st.write(respuesta.text)

    # ==== Ver reflexiones anteriores ====
    st.markdown("---")
    st.subheader("📜 Tus reflexiones anteriores")
    st.text(obtener_registros(email))
