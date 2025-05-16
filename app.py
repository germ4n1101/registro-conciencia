import streamlit as st
import yaml
import os
import cohere
from datetime import datetime

# Leer la clave API de Cohere desde secrets.toml
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
            model="command",  # Usa un modelo disponible en el plan gratuito
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except cohere.CohereError as e:
        st.error(f"❌ Error al generar reflexión: {str(e)}")
        return "Ocurrió un error al generar la reflexión con la IA."

USERS_FILE = "usuarios.yaml"

# Función para cargar usuarios desde archivo YAML
def load_users():
    if not os.path.exists(USERS_FILE):
        return {"usuarios": []}
    with open(USERS_FILE, "r") as f:
        try:
            data = yaml.safe_load(f) or {}
        except yaml.YAMLError:
            data = {}
        if "usuarios" not in data:
            data["usuarios"] = []
        return data

# Función para guardar usuarios en archivo YAML
def save_users(data):
    with open(USERS_FILE, "w") as f:
        yaml.dump(data, f)

# Interfaz de registro de usuario
def register():
    st.subheader("Registro de usuario")
    username = st.text_input("Nombre de usuario")
    full_name = st.text_input("Nombre completo")
    email = st.text_input("Correo electrónico")
    password = st.text_input("Contraseña", type="password")

    if st.button("Registrarse"):
        if username and full_name and email and password:
            data = load_users()
            if any(u['username'] == username for u in data['usuarios']):
                st.warning("El nombre de usuario ya existe.")
            else:
                new_user = {
                    "username": username,
                    "nombre": full_name,
                    "email": email,
                    "password": password
                }
                data['usuarios'].append(new_user)
                save_users(data)
                st.success("Usuario registrado con éxito. Ahora puedes iniciar sesión.")
        else:
            st.warning("Por favor, completa todos los campos.")

# Interfaz de recuperación de contraseña
def recover_password():
    st.subheader("Recuperar contraseña")
    username = st.text_input("Ingresa tu nombre de usuario")
    if st.button("Recuperar"):
        data = load_users()
        user = next((u for u in data['usuarios'] if u['username'] == username), None)
        if user:
            st.info(f"Recordatorio: Tu correo registrado es {user['email']}. Puedes usarlo para contactarte si olvidas tu clave.")
        else:
            st.warning("Usuario no encontrado.")

# Interfaz de inicio de sesión
def login():
    st.subheader("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        data = load_users()
        user = next((u for u in data['usuarios'] if u['username'] == username and u['password'] == password), None)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success(f"Bienvenido, {user['nombre']}!")
        else:
            st.error("Credenciales incorrectas")

# App principal después de iniciar sesión
def main_app():
    st.title("🧘 Registro de Conciencia")
    st.write("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

    estado = st.text_input("¿Cómo te sientes hoy?")
    pensamiento = st.text_input("¿Qué ha estado ocupando tus pensamientos últimamente?")
    gratitud = st.text_input("¿Qué agradeces hoy?")
    meta = st.text_input("¿Qué te gustaría lograr o mejorar?")

    if st.button("Guardar y reflexionar"):
        texto = f"Hoy me siento {estado}. He estado pensando en {pensamiento}. Agradezco {gratitud}. Me gustaría lograr {meta}."
        

        prompt = (
            "Actúa como una mente sabia y reflexiva que guía con compasión. "
            "A partir del siguiente registro personal, escribe una reflexión motivadora, clara y positiva:"
            f"\n\n{entrada_usuario}\n\nReflexión:"
        )

        try:
            respuesta = co.chat(
                model="command-r-plus",
                message=prompt
            )
            reflexion = respuesta.text
            st.success("✅ Entrada guardada y analizada por la IA.")
            st.markdown("## 🧠 Reflexión de la IA")
            st.write("**Reflexión:**")
            st.write(reflexion)
        except Exception as e:
            st.error(f"⚠️ Error con la IA: {e}")
        
        #try:
            #response = cohere_client.generate(
                #model="command-r-plus",
                #prompt=f"Genera una reflexión positiva y motivadora basada en este texto: '{texto}'",
               # max_tokens=100
           # )
            #reflexion = response.generations[0].text.strip()
            #st.success("Entrada guardada y analizada por la IA.")
           # st.markdown(f"**Reflexión generada:** {reflexion}")
        #except Exception as e:
            #st.error("Error al generar la reflexión con Cohere. Por favor, intenta más tarde.")
#
# Control principal
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.sidebar.title("Bienvenido")
        options = ["Iniciar sesión", "Registrarse", "Recuperar contraseña"]
        choice = st.sidebar.radio("Seleccione una opción", options)

        if choice == "Iniciar sesión":
            login()
        elif choice == "Registrarse":
            register()
        elif choice == "Recuperar contraseña":
            recover_password()
    else:
        st.sidebar.title("Menú")
        choice = st.sidebar.radio("Seleccione una opción", ["Registro diario", "Cerrar sesión"])

        if choice == "Registro diario":
            main_app()
        elif choice == "Cerrar sesión":
            st.session_state['logged_in'] = False
            st.success("Sesión cerrada con éxito. Puedes iniciar sesión nuevamente.")
if __name__ == "__main__":
    main()

