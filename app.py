import streamlit as st
import yaml
import os
import cohere
from datetime import datetime
from yaml.loader import SafeLoader
from pathlib import Path

# Configuración inicial
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘", layout="centered")

# Archivo de usuarios
USERS_FILE = "usuarios.yaml"

# Inicializar usuarios si no existe
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        yaml.dump({'usuarios': []}, f)

# Función para cargar usuarios
def load_users():
    with open(USERS_FILE, 'r') as f:
        return yaml.load(f, Loader=SafeLoader)

# Función para guardar usuarios
def save_users(users_data):
    with open(USERS_FILE, 'w') as f:
        yaml.dump(users_data, f)

# Función de registro de usuario
def register_user():
    st.subheader("📋 Registro de nuevo usuario")
    new_username = st.text_input("Nombre de usuario")
    new_name = st.text_input("Nombre completo")
    new_email = st.text_input("Correo electrónico")
    new_password = st.text_input("Contraseña", type="password")
    if st.button("Registrarme"):
        data = load_users()
        if any(u['username'] == new_username for u in data['usuarios']):
            st.warning("El nombre de usuario ya existe")
        else:
            data['usuarios'].append({
                'username': new_username,
                'name': new_name,
                'email': new_email,
                'password': new_password
            })
            save_users(data)
            st.success("Usuario registrado exitosamente. Ya puedes iniciar sesión.")

# Función de recuperación de contraseña
def recover_password():
    st.subheader("🔑 Recuperación de contraseña")
    email = st.text_input("Ingresa tu correo electrónico")
    if st.button("Recuperar contraseña"):
        data = load_users()
        user = next((u for u in data['usuarios'] if u['email'] == email), None)
        if user:
            st.info(f"Tu contraseña registrada es: {user['password']}")
        else:
            st.error("Correo no encontrado")

# Página principal
def main():
    menu = ["Iniciar sesión", "Registrarse", "Recuperar contraseña"]
    choice = st.sidebar.selectbox("Menú", menu)

    if choice == "Registrarse":
        register_user()

    elif choice == "Recuperar contraseña":
        recover_password()

    elif choice == "Iniciar sesión":
        st.subheader("🔐 Inicio de sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Iniciar sesión"):
            data = load_users()
            user = next((u for u in data['usuarios'] if u['username'] == username and u['password'] == password), None)
            if user:
                st.success(f"Bienvenido/a {user['name']}")
                run_reflection(user['username'])
            else:
                st.error("Credenciales inválidas")

# Función de reflexión con Cohere
def run_reflection(username):
    st.title("🧘 Registro de Conciencia")

    hoy = datetime.now().strftime("%Y-%m-%d")
    filepath = Path(f"registros/{username}_{hoy}.txt")
    os.makedirs(filepath.parent, exist_ok=True)

    st.write("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

    q1 = st.text_input("¿Cómo te sientes hoy?")
    q2 = st.text_input("¿Qué ha estado ocupando tus pensamientos últimamente?")
    q3 = st.text_input("¿Qué agradeces hoy?")
    q4 = st.text_input("¿Qué te gustaría lograr o mejorar?")

    if st.button("Guardar y reflexionar"):
        entrada = f"Fecha: {hoy}\nUsuario: {username}\n\nCómo te sientes: {q1}\nPensamientos: {q2}\nGratitud: {q3}\nMetas: {q4}\n"
        with open(filepath, "w") as f:
            f.write(entrada)

        st.success("✅ Entrada guardada y analizada por la IA.")

        # Análisis con Cohere
        co = cohere.Client(st.secrets["hTRHKEoz2gRAe68ILa7SqCq6T82lZn1muCV619EX"])
        prompt = f"Hoy el usuario se siente así: {q1}. Ha estado pensando en: {q2}. Agradece: {q3}. Quiere mejorar: {q4}. Genera una reflexión personalizada y empática con tono motivador."

        response = co.generate(
            model='command-r',
            prompt=prompt,
            max_tokens=150
        )

        st.markdown("### ✨ Reflexión generada por IA")
        st.info(response.generations[0].text.strip())

if __name__ == '__main__':
    main()
