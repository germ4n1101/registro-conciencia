import streamlit as st
from supabase import create_client
import bcrypt
import cohere
from datetime import datetime

# ============================
# Conexión a Supabase
# ============================
DB_URL = st.secrets["DB_URL"]  # "https://xxxx.supabase.co"
DB_KEY = st.secrets["DB_KEY"]  # anon public key
supabase = create_client(DB_URL, DB_KEY)

# Conexión a Cohere
COHERE_KEY = st.secrets["COHERE_KEY"]
co = cohere.Client(COHERE_KEY)

# ============================
# Funciones de Base de Datos
# ============================
def registrar_usuario(username, password):
    existe = supabase.table("usuarios").select("username").eq("username", username).execute()
    if existe.data:
        return False, "El usuario ya existe."
    
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    supabase.table("usuarios").insert({"username": username, "password": hashed_pw}).execute()
    return True, "Registro exitoso."

def login_usuario(username, password):
    user_data = supabase.table("usuarios").select("*").eq("username", username).execute()
    if not user_data.data:
        return False
    hashed_pw = user_data.data[0]["password"]
    return bcrypt.checkpw(password.encode("utf-8"), hashed_pw.encode("utf-8"))

def guardar_reflexion(username, texto):
    supabase.table("reflexiones").insert({
        "username": username,
        "texto": texto,
        "fecha": datetime.now().isoformat()
    }).execute()

def obtener_reflexiones(username):
    data = supabase.table("reflexiones").select("*").eq("username", username).order("fecha", desc=True).execute()
    return data.data

# ============================
# Manejo de Sesión
# ============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def cerrar_sesion():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("Sesión cerrada.")

# ============================
# Interfaz Streamlit
# ============================
st.title("🧠 Registro de Conciencia")

if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menú", ["Iniciar Sesión", "Registrarse"])

    if menu == "Registrarse":
        st.subheader("Crear cuenta")
        new_user = st.text_input("Usuario")
        new_password = st.text_input("Contraseña", type="password")
        if st.button("Registrar"):
            if new_user and new_password:
                ok, msg = registrar_usuario(new_user, new_password)
                st.success(msg) if ok else st.error(msg)
            else:
                st.warning("Por favor complete todos los campos.")

    elif menu == "Iniciar Sesión":
        st.subheader("Iniciar sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if login_usuario(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Bienvenido {username}")
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

else:
    st.sidebar.success(f"Conectado como: {st.session_state.username}")
    if st.sidebar.button("Cerrar Sesión"):
        cerrar_sesion()
        st.experimental_rerun()

    st.subheader("✨ Generar Reflexión")
    prompt = st.text_area("Escribe un tema, pensamiento o situación:")
    if st.button("Generar Reflexión"):
        if prompt.strip():
            with st.spinner("Pensando..."):
                resp = co.generate(
                    model="command-xlarge-nightly",
                    prompt=f"Genera una reflexión breve, positiva y profunda sobre: {prompt}",
                    max_tokens=100,
                    temperature=0.8
                )
                texto_generado = resp.generations[0].text.strip()
                st.success(texto_generado)
                guardar_reflexion(st.session_state.username, texto_generado)
        else:
            st.warning("Por favor escribe algo para reflexionar.")

    st.subheader("📜 Historial de Reflexiones")
    reflexiones = obtener_reflexiones(st.session_state.username)
    if reflexiones:
        for r in reflexiones:
            st.write(f"**{r['fecha'][:19]}** — {r['texto']}")
    else:
        st.info("No has registrado reflexiones aún.")

