import streamlit as st
import yaml
import cohere
import datetime
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

# Leer configuración desde config.yaml
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"].get("name"),
    config["cookie"].get("key"),
    config["cookie"].get("expiry_days"),
)

# Login
name, authentication_status, username = authenticator.login("Iniciar sesión")

if authentication_status is False:
    st.error("Usuario o contraseña incorrectos")
elif authentication_status is None:
    st.warning("Por favor ingresa tus credenciales")
elif authentication_status:
    authenticator.logout("Cerrar sesión", "sidebar")
    st.sidebar.success(f"Bienvenido, {name} \U0001F44B")

    st.title("🧘 Registro de Conciencia")
    st.write("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

    # Formulario
    with st.form("diario_form"):
        estado = st.text_input("¿Cómo te sientes hoy?")
        pensamientos = st.text_input("¿Qué ha estado ocupando tus pensamientos últimamente?")
        gratitud = st.text_input("¿Qué agradeces hoy?")
        meta = st.text_input("¿Qué te gustaría lograr o mejorar?")
        submit = st.form_submit_button("Guardar y reflexionar")

    if submit and all([estado, pensamientos, gratitud, meta]):
        # Generar reflexión con Cohere
        co = cohere.Client(st.secrets["hTRHKEoz2gRAe68ILa7SqCq6T82lZn1muCV619EX"])

        entrada = f"Hoy me siento {estado}. He estado pensando en {pensamientos}. Agradezco {gratitud}. Me gustaría mejorar o lograr {meta}."
        prompt = (
            "Actúa como un coach de bienestar que da reflexiones sabias y empáticas basadas en entradas de diario.\n"
            f"Entrada: {entrada}\n"
            "Reflexión:"
        )

        respuesta = co.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=200,
            temperature=0.7,
        )

        reflexion = respuesta.generations[0].text.strip()

        st.success("✅ Entrada guardada y analizada por la IA.")
        st.markdown("### 🌈 Reflexión del día")
        st.write(reflexion)

        # Opcional: Guardar en archivo local
        with open("registros.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat()} | {username} | {entrada} | {reflexion}\n")

