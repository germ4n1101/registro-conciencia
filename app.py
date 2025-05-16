import streamlit as st
import yaml
import os
import cohere
from datetime import datetime
from yaml.loader import SafeLoader

# Leer usuarios
def load_users():
    if os.path.exists("usuarios.yaml"):
        with open("usuarios.yaml", "r") as file:
            return yaml.load(file, Loader=SafeLoader) or {"usuarios": []}
    return {"usuarios": []}

# Guardar usuarios
def save_users(data):
    with open("usuarios.yaml", "w") as file:
        yaml.dump(data, file)

# Registrar usuario
def register_user():
    st.subheader("Crear una cuenta nueva")
    new_username = st.text_input("Nombre de usuario")
    new_email = st.text_input("Correo electrónico")
    new_password = st.text_input("Contraseña", type="password")
    if st.button("Registrarme"):
        data = load_users()
        if any(u['username'] == new_username for u in data['usuarios']):
            st.warning("Este usuario ya existe.")
        else:
            data['usuarios'].append({
                'username': new_username,
                'email': new_email,
                'password': new_password
            })
            save_users(data)
            st.success("Registro exitoso. Ya puedes iniciar sesión.")

# Recuperación de contraseña
def recover_password():
    st.subheader("Recuperar contraseña")
    email = st.text_input("Ingresa tu correo electrónico")
    if st.button("Recuperar"):
        data = load_users()
        user = next((u for u in data['usuarios'] if u['email'] == email), None)
        if user:
            st.info(f"Tu nombre de usuario es '{user['username']}' y tu contraseña es '{user['password']}'")
        else:
            st.warning("No se encontró un usuario con ese correo.")

# Login
def login():
    st.subheader("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        data = load_users()
        user = next((u for u in data['usuarios'] if u['username'] == username and u['password'] == password), None)
        if user:
            st.session_state["authenticated"] = True
            st.session_state["user"] = username
            st.success("Inicio de sesión exitoso.")
        else:
            st.error("Usuario o contraseña incorrectos.")

# Área principal con Cohere
@st.cache_resource
def load_cohere():
    api_key = st.secrets["cohere"]["api_key"]
    return cohere.Client(api_key)

cohere_client = load_cohere()

def main_app():
    st.title("🧘 Registro de Conciencia")
    st.write("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

    q1 = st.text_input("¿Cómo te sientes hoy?")
    q2 = st.text_input("¿Qué ha estado ocupando tus pensamientos últimamente?")
    q3 = st.text_input("¿Qué agradeces hoy?")
    q4 = st.text_input("¿Qué te gustaría lograr o mejorar?")

    if st.button("Guardar y reflexionar"):
        texto = f"Hoy me siento: {q1}. Últimamente pienso en: {q2}. Agradezco: {q3}. Deseo mejorar o lograr: {q4}."
        response = cohere_client.generate(
            model='command-r',
            prompt=f"Reflexiona sobre este registro personal: {texto}",
            max_tokens=100
        )
        st.success("✅ Entrada guardada y analizada por la IA.")
        st.info(response.generations[0].text)

# Control de flujo
st.sidebar.title("Menú")
menu = st.sidebar.selectbox("Opciones", ["Login", "Registro", "Recuperar clave", "App"])

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if menu == "Login":
    login()

elif menu == "Registro":
    register_user()

elif menu == "Recuperar clave":
    recover_password()

elif menu == "App":
    if st.session_state["authenticated"]:
        main_app()
    else:
        st.warning("Por favor, inicia sesión primero.")
