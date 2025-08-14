import os
from datetime import datetime
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import cohere

# --- Cargar variables de entorno ---
load_dotenv()

DB_URL = os.getenv("DB_URL")
DB_KEY = os.getenv("DB_KEY")
COHERE_KEY = os.getenv("COHERE_KEY")

# --- Verificar conexión a Supabase ---
if not DB_URL or not DB_KEY:
    st.error("❌ Error de configuración: Faltan credenciales de Supabase.\n"
             "Verifica que DB_URL y DB_KEY estén en tu archivo .env o en los Secrets de Streamlit.")
    st.stop()

try:
    supabase = create_client(DB_URL, DB_KEY)
except Exception as e:
    st.error(f"❌ No se pudo conectar a Supabase: {str(e)}")
    st.stop()

# --- Inicializar Cohere ---
if not COHERE_KEY:
    st.error("❌ Falta la clave de API de Cohere (COHERE_KEY).")
    st.stop()

co = cohere.Client(COHERE_KEY)

# --- Funciones de la app ---
def registrar_usuario(usuario, contrasena):
    existe = supabase.table("usuarios").select("*").eq("usuario", usuario).execute()
    if existe.data:
        return False, "El usuario ya existe."
    supabase.table("usuarios").insert({"usuario": usuario, "contrasena": contrasena}).execute()
    return True, "Usuario registrado con éxito."

def autenticar_usuario(usuario, contrasena):
    res = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("contrasena", contrasena).execute()
    return bool(res.data)

def guardar_registro(usuario, entrada):
    supabase.table("registros").insert({"usuario": usuario, "contenido": entrada}).execute()

def obtener_registros(usuario):
    res = supabase.table("registros").select("contenido").eq("usuario", usuario).order("id", desc=True).execute()
    return "\n\n".join([r["contenido"] for r in res.data]) if res.data else "No tienes registros aún."

def generar_reflexion(prompt):
    response = co.generate(
        model="command-xlarge-nightly",
        prompt=prompt,
        max_tokens=200
    )
    return response.generations[0].text.strip()

# --- UI ---
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘")

if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = None

menu = ["Login", "Registro"] if not st.session_state.usuario_autenticado else ["Registro de Conciencia", "Salir"]
opcion = st.sidebar.selectbox("Menú", menu)

if opcion == "Registro":
    st.title("📝 Registro de Usuario")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Registrar"):
        ok, msg = registrar_usuario(user, pwd)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

elif opcion == "Login":
    st.title("🔑 Iniciar Sesión")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if autenticar_usuario(user, pwd):
            st.session_state.usuario_autenticado = user
            st.success("✅ Sesión iniciada.")
            st.experimental_rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

elif opcion == "Registro de Conciencia":
    st.title("🧘 Registro de Conciencia")
    st.markdown("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

    estado_animo = st.text_input("1. ¿Cómo te sientes hoy?")
    situacion = st.text_input("2. ¿Qué ha estado ocupando tus pensamientos últimamente?")
    agradecimiento = st.text_input("3. ¿Qué agradeces hoy?")
    meta = st.text_input("4. ¿Qué te gustaría lograr o mejorar?")

    if st.button("Guardar y reflexionar"):
        if not any([estado_animo, situacion, agradecimiento, meta]):
            st.warning("Por favor responde al menos una pregunta.")
        else:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entrada = f"""Fecha: {fecha}
Estado de ánimo: {estado_animo}
Situación actual: {situacion}
Agradecimiento: {agradecimiento}
Meta: {meta}
"""
            guardar_registro(st.session_state.usuario_autenticado, entrada)
            st.success("✅ Entrada guardada y analizada por la IA.")

            prompt_ia = (
                f"Soy una persona reflexiva. Hoy escribí:\n\n"
                f"Estado de ánimo: {estado_animo}\n"
                f"Situación actual: {situacion}\n"
                f"Agradecimiento: {agradecimiento}\n"
                f"Meta: {meta}\n\n"
                f"Por favor genera una reflexión amable, positiva y consciente basada en esta información."
            )
            reflexion = generar_reflexion(prompt_ia)
            st.subheader("🧠 Reflexión para ti")
            st.write(reflexion)

    st.markdown("---")
    with st.expander("📜 Ver mis reflexiones pasadas"):
        registros = obtener_registros(st.session_state.usuario_autenticado)
        st.text_area("Historial de reflexiones", registros, height=300)

elif opcion == "Salir":
    st.session_state.usuario_autenticado = None
    st.success("Has cerrado sesión.")
    st.experimental_rerun()


