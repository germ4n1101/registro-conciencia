import streamlit as st
import cohere
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
from datetime import datetime

# ---------------------------
# Autenticación de usuarios
# ---------------------------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login("Iniciar sesión", location="main")


if authentication_status is False:
    st.error('Usuario o contraseña incorrectos')
elif authentication_status is None:
    st.warning('Por favor, introduce tus credenciales')
elif authentication_status:

    authenticator.logout('Cerrar sesión', 'sidebar')
    st.sidebar.success(f'Bienvenido, {name}')

    # ---------------------------
    # App Registro de Conciencia
    # ---------------------------
    st.markdown("<h1 style='text-align: center;'>🧘 Registro de Conciencia</h1>", unsafe_allow_html=True)
    st.write("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

    # Inputs
    estado = st.text_input("¿Cómo te sientes hoy?")
    pensamiento = st.text_input("¿Qué ha estado ocupando tus pensamientos últimamente?")
    gratitud = st.text_input("¿Qué agradeces hoy?")
    mejora = st.text_input("¿Qué te gustaría lograr o mejorar?")

    # Procesar y generar reflexión
    if st.button("Guardar y reflexionar"):
        if not all([estado, pensamiento, gratitud, mejora]):
            st.warning("Por favor completa todos los campos.")
        else:
            # Conexión con Cohere
            co = cohere.Client("hTRHKEoz2gRAe68ILa7SqCq6T82lZn1muCV619EX")

            entrada = f"""Hoy me siento {estado}. He estado pensando mucho en {pensamiento}. 
            Agradezco {gratitud}. Me gustaría mejorar o alcanzar: {mejora}.
            Por favor, genera una breve reflexión positiva y personalizada basada en este estado."""

            respuesta = co.generate(
                model='command',
                prompt=entrada,
                max_tokens=100
            )

            reflexion = respuesta.generations[0].text.strip()

            # Guardar entrada localmente (opcional)
            with open("registros.csv", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()},{name},{estado},{pensamiento},{gratitud},{mejora},{reflexion}\n")

            # Mostrar resultado
            st.success("✅ Entrada guardada y analizada por la IA.")
            st.markdown("### ✨ Reflexión generada:")
            st.info(reflexion)


