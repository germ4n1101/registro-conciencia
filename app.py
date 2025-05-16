import streamlit as st
import yaml
import os
import hashlib
import cohere
from datetime import datetime

# ------------------ CONFIGURACION INICIAL ------------------
st.set_page_config(page_title="Registro de Conciencia", layout="centered")

# Obtener clave de Cohere desde secrets
try:
    cohere_api_key = st.secrets["cohere"]["api_key"]
    cohere_client = cohere.Client(cohere_api_key)
except KeyError:
    st.error("❌ No se encontró la clave API de Cohere en .streamlit/secrets.toml.")
    st.stop()

USERS_FILE = "usuarios.yaml"

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            yaml.dump({"usuarios": []}, f)
    with open(USERS_FILE, 'r') as f:
        return yaml.safe_load(f)

def save_users(data):
    with open(USERS_FILE, 'w') as f:
        yaml.dump(data, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------ AUTENTICACION ------------------
def login():
    st.subheader("🔐 Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        data = load_users()
        for user in data['usuarios']:
            if user['username'] == username and user['password'] == hash_password(password):
                st.session_state.usuario = user
                return True
        st.error("Credenciales inválidas")
    return False

def register():
    st.subheader("📝 Registro")
    name = st.text_input("Nombre completo")
    username = st.text_input("Usuario nuevo")
    email = st.text_input("Correo electrónico")
    password = st.text_input("Contraseña nueva", type="password")
    if st.button("Registrar"):
        data = load_users()
        if any(u['username'] == username for u in data['usuarios']):
            st.error("Este usuario ya existe")
        else:
            data['usuarios'].append({
                "name": name,
                "username": username,
                "email": email,
                "password": hash_password(password)
            })
            save_users(data)
            st.success("Usuario registrado correctamente. Ahora puedes iniciar sesión.")

# ------------------ RECUPERAR CLAVE (simulada) ------------------
def recuperar():
    st.subheader("🔑 Recuperar contraseña")
    email = st.text_input("Ingresa tu correo registrado")
    if st.button("Recuperar"):
        data = load_users()
        for u in data['usuarios']:
            if u['email'] == email:
                st.info("Se enviaría un recordatorio al correo: {} (función simulada)".format(email))
                return
        st.warning("Correo no encontrado")

# ------------------ REFLEXIÓN CON COHERE ------------------
def generar_reflexion(prompt):
    if not prompt.strip():
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

# ------------------ PANTALLA PRINCIPAL ------------------
def main_app():
    st.title("🧘 Registro de Conciencia")
    st.markdown("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

    sentimiento = st.text_input("¿Cómo te sientes hoy?")
    pensamientos = st.text_input("¿Qué ha estado ocupando tus pensamientos últimamente?")
    agradecimiento = st.text_input("¿Qué agradeces hoy?")
    meta = st.text_input("¿Qué te gustaría lograr o mejorar?")

    if st.button("Guardar y reflexionar"):
        prompt = f"""
        ¿Cómo te sientes hoy?: {sentimiento}
        ¿Qué ha estado ocupando tus pensamientos?: {pensamientos}
        ¿Qué agradeces hoy?: {agradecimiento}
        ¿Qué te gustaría lograr?: {meta}
        """
        reflexion = generar_reflexion(prompt)
        st.success("Entrada guardada y analizada por la IA.")
        st.markdown("### 🤖 Reflexión generada:")
        st.info(reflexion)

# ------------------ NAVEGACION ------------------
def main():
    menu = ["Iniciar sesión", "Registrarse", "Recuperar contraseña"]
    choice = st.sidebar.selectbox("Navegación", menu)

    if choice == "Iniciar sesión":
        if "usuario" in st.session_state:
            main_app()
        elif login():
            st.experimental_rerun()
    elif choice == "Registrarse":
        register()
    elif choice == "Recuperar contraseña":
        recuperar()

if __name__ == "__main__":
    main()

