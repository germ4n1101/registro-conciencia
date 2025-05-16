import streamlit as st
import cohere
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from datetime import date

# Cargar configuración de autenticación
def load_auth_config():
    with open("config.yaml") as file:
        return yaml.load(file, Loader=SafeLoader)

config = load_auth_config()

# Autenticación
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, auth_status, username = authenticator.login("Iniciar sesión", "main")

if auth_status:
    st.sidebar.success(f"Bienvenido, {name}")
    authenticator.logout("Cerrar sesión", "sidebar")

    st.title("🧘 Registro de Conciencia")
    st.write("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

    co = cohere.Client(st.secrets["hTRHKEoz2gRAe68ILa7SqCq6T82lZn1muCV619EX"])

    hoy = date.today().strftime("%Y-%m-%d")
    st.subheader(f"📅 Entrada del día {hoy}")

    estado = st.text_input("¿Cómo te sientes hoy?")
    pensamientos = st.text_input("¿Qué ha estado ocupando tus pensamientos últimamente?")
    gratitud = st.text_input("¿Qué agradeces hoy?")
    mejora = st.text_input("¿Qué te gustaría lograr o mejorar?")

    if st.button("Guardar y reflexionar"):
        respuesta = co.generate(
            model="command-r-plus",
            prompt=f"Hoy me siento {estado}. Últimamente he pensado mucho en {pensamientos}. Estoy agradecido por {gratitud}. Me gustaría mejorar o lograr {mejora}. Por favor, genera una breve reflexión personalizada.",
            max_tokens=150
        )
        with open("entradas.txt", "a") as f:
            f.write(f"{hoy} - {username}\nEstado: {estado}\nPensamientos: {pensamientos}\nGratitud: {gratitud}\nMeta: {mejora}\n\n")
        st.success("✅ Entrada guardada y analizada por la IA.")
        st.markdown("---")
        st.subheader("🧠 Reflexión generada:")
        st.write(respuesta.generations[0].text.strip())

elif auth_status is False:
    st.error("Usuario o contraseña incorrectos.")

elif auth_status is None:
    st.warning("Por favor, ingresa tus credenciales para continuar.")

