import streamlit as st
import yaml
import os
import cohere
from datetime import datetime

# Inicializar Cohere
COHERE_API_KEY = st.secrets["hTRHKEoz2gRAe68ILa7SqCq6T82lZn1muCV619EX"]
co = cohere.Client(COHERE_API_KEY)

USERS_FILE = "usuarios.yaml"

# Funciones auxiliares para manejo de usuarios
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return yaml.safe_load(file) or {"usuarios": []}
    return {"usuarios": []}

def save_users(data):
    with open(USERS_FILE, "w") as file:
        yaml.dump(data, file)

def register_user():
    st.subheader("Registro de nuevo usuario")
    new_username = st.text_input("Nombre de usuario")
    new_name = st.text_input("Nombre completo")
    new_email = st.text_input("Correo electrónico")
    new_password = st.text_input("Contraseña", type="password")

    if st.button("Registrarme"):
        if not new_username or not new_name or not new_email or not new_password:
            st.warning("Por favor, completa todos los campos.")
            return

        data = load_users()

        if any(u['username'] == new_username for u in data["usuarios"]):
            st.error("El nombre de usuario ya existe. Elige otro.")
        else:
            data["usuarios"].append({
                "username": new_username,
                "name": new_name,
                "email": new_email,
                "password": new_password
            })
            save_users(data)
            st.success("¡Registro exitoso! Ahora puedes iniciar sesión.")

def forgot_password():
    st.subheader("Recuperar contraseña")
    email = st.text_input("Ingresa tu correo electrónico")
    if st.button("Recuperar"):
        data = load_users()
        user = next((u for u in data["usuarios"] if u["email"] == email), None)
        if user:
            st.info(f"Tu usuario es: {user['username']}, tu contraseña es: {user['password']}")
        else:
            st.error("Correo no registrado.")

def login():
    st.subheader("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        data = load_users()
        user = next((u for u in data["usuarios"] if u["username"] == username and u["password"] == password), None)
        if user:
            st.session_state["usuario"] = user
            st.success(f"Bienvenido, {user['name']}")
        else:
            st.error("Credenciales incorrectas")

def logout():
    if st.button("Cerrar sesión"):
        st.session_state.pop("usuario")
        st.experimental_rerun()

def reflexionar():
    st.title("🧘‍ Registro de Conciencia")

    col1, col2 = st.columns([2, 1])
    with col1:
        hoy = datetime.now().strftime("%Y-%m-%d")
        estado = st.text_area("¿Cómo te sientes hoy?")
        pensamientos = st.text_area("¿Qué ha estado ocupando tus pensamientos últimamente?")
        agradecimiento = st.text_area("¿Qué agradeces hoy?")
        metas = st.text_area("¿Qué te gustaría lograr o mejorar?")

        if st.button("Guardar y reflexionar"):
            prompt = f"Hoy es {hoy}. Me siento: {estado}. Pienso en: {pensamientos}. Agradezco: {agradecimiento}. Mis metas: {metas}. Genera una reflexión personal inspiradora y corta."
            try:
                response = co.generate(
                    model="command-r",
                    prompt=prompt,
                    max_tokens=100
                )
                reflexion = response.generations[0].text.strip()
                st.success("Entrada guardada y analizada por la IA.")
                st.markdown(f"**Reflexión del día:** _{reflexion}_")
            except Exception as e:
                st.error(f"Error generando la reflexión: {e}")

    with col2:
        st.markdown("---")
        st.markdown("**Usuario actual:**")
        st.write(st.session_state["usuario"]["name"])
        logout()

def main():
    st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘‍")
    st.markdown("""
        <style>
            textarea {
                height: 80px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    if "usuario" not in st.session_state:
        menu = st.sidebar.radio("Menú", ("Iniciar sesión", "Registrarme", "Recuperar contraseña"))

        if menu == "Iniciar sesión":
            login()
        elif menu == "Registrarme":
            register_user()
        elif menu == "Recuperar contraseña":
            forgot_password()
    else:
        reflexionar()

if __name__ == "__main__":
    main()
