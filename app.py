import streamlit as st
import yaml
import os
import cohere
from datetime import datetime
import hashlib

# --- CONFIGURACIÓN DE COHERE ---
try:
    cohere_api_key = st.secrets["cohere"]["api_key"]
    cohere_client = cohere.Client(cohere_api_key)
except KeyError:
    st.error("❌ No se encontró la clave API de Cohere en .streamlit/secrets.toml.")
    st.stop()

# --- FUNCIONES AUXILIARES ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def cargar_usuarios():
    if os.path.exists("usuarios.yaml"):
        with open("usuarios.yaml", "r") as file:
            return yaml.safe_load(file) or {}
    return {}

def guardar_usuarios(usuarios):
    with open("usuarios.yaml", "w") as file:
        yaml.dump(usuarios, file)

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

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘")

# --- AUTENTICACIÓN ---
if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = None

usuarios = cargar_usuarios()

if st.session_state.usuario_autenticado is None:
    st.sidebar.title("🔐 Iniciar sesión / Registro")

    email = st.sidebar.text_input("Correo electrónico")
    password = st.sidebar.text_input("Contraseña", type="password")

    if st.sidebar.button("Iniciar sesión"):
        if email in usuarios and usuarios[email]["password"] == hash_password(password):
            st.session_state.usuario_autenticado = email
            st.success("✅ Inicio de sesión exitoso. Cargando...")
            st.stop()
        else:
            st.sidebar.error("❌ Credenciales incorrectas.")

    if st.sidebar.button("Registrarse"):
        if email in usuarios:
            st.sidebar.error("⚠️ El correo ya está registrado.")
        else:
            usuarios[email] = {"password": hash_password(password)}
            guardar_usuarios(usuarios)
            st.sidebar.success("✅ Usuario registrado correctamente.")
else:
    # --- PANTALLA PRINCIPAL ---
    st.title("🧘 Registro de Conciencia")
    st.markdown("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

    # Preguntas de entrada
    estado_animo = st.text_input("1. ¿Cómo te sientes hoy?")
    situacion = st.text_input("2. ¿Qué ha estado ocupando tus pensamientos últimamente?")
    agradecimiento = st.text_input("3. ¿Qué agradeces hoy?")
    meta = st.text_input("4. ¿Qué te gustaría lograr o mejorar?")

    # Botón de guardar y reflexionar
    if st.button("Guardar y reflexionar"):
        if not any([estado_animo, situacion, agradecimiento, meta]):
            st.warning("Por favor responde al menos una pregunta.")
        else:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entrada = f"""
            Fecha: {fecha}
            Usuario: {st.session_state.usuario_autenticado}
            Estado de ánimo: {estado_animo}
            Situación actual: {situacion}
            Agradecimiento: {agradecimiento}
            Meta: {meta}
            """
            with open("registro_conciencia.txt", "a", encoding="utf-8") as archivo:
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

                st.subheader("🧠 Reflexión de German para ti")
                st.write(respuesta.text)

            except Exception as e:
                st.error(f"⚠️ Error con la IA: {e}")

    # Opción para cerrar sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.usuario_autenticado = None
        st.success("🔒 Sesión cerrada. Recarga para volver al inicio.")
        st.stop()
