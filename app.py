import streamlit as st
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash
import cohere
from datetime import datetime

# --- Cargar secretos ---
DB_URL = st.secrets["DB_URL"]
DB_KEY = st.secrets["DB_KEY"]  # Debes agregarla en secrets.toml si no la tienes
COHERE_KEY = st.secrets["cohere"]["api_key"]

# --- Inicializar clientes ---
supabase = create_client(DB_URL, DB_KEY)
co = cohere.Client(COHERE_KEY)

st.set_page_config(page_title="Registro de Conciencia", layout="centered")

# --- Funciones ---
def registrar_usuario(username, password):
    hashed_pw = generate_password_hash(password)
    response = supabase.table("usuarios").insert({
        "username": username,
        "password": hashed_pw
    }).execute()
    return response

def verificar_usuario(username, password):
    data = supabase.table("usuarios").select("*").eq("username", username).execute()
    if data.data:
        hashed_pw = data.data[0]["password"]
        return check_password_hash(hashed_pw, password)
    return False

def guardar_entrada(username, texto):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    supabase.table("entradas").insert({
        "username": username,
        "fecha": fecha,
        "texto": texto
    }).execute()

def generar_reflexion(texto):
    prompt = f"Genera una reflexión inspiradora basada en el siguiente texto: {texto}"
    response = co.generate(
        model="command-xlarge",
        prompt=prompt,
        max_tokens=80
    )
    return response.generations[0].text.strip()

# --- UI ---
st.title("🧠 Registro de Conciencia")

menu = ["Iniciar sesión", "Registrarse"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Registrarse":
    st.subheader("Crear cuenta")
    new_user = st.text_input("Usuario")
    new_password = st.text_input("Contraseña", type="password")
    if st.button("Registrar"):
        registrar_usuario(new_user, new_password)
        st.success("Usuario registrado con éxito.")

elif choice == "Iniciar sesión":
    st.subheader("Acceder")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if verificar_usuario(username, password):
            st.success(f"Bienvenido, {username}")

            texto = st.text_area("Escribe tu entrada de conciencia")
            if st.button("Guardar entrada"):
                guardar_entrada(username, texto)
                st.success("Entrada guardada.")

            if st.button("Generar reflexión"):
                reflexion = generar_reflexion(texto)
                st.info(reflexion)
        else:
            st.error("Usuario o contraseña incorrectos")
