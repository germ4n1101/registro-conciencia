import streamlit as st
from supabase import create_client
from datetime import datetime
import os

# Variables de entorno (asegúrate de configurarlas en Streamlit Cloud o localmente)
DB_URL = os.getenv("SUPABASE_URL")
DB_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(DB_URL, DB_KEY)

# --- Función de registro ---
def registrar_usuario(email, password):
    auth_response = supabase.auth.sign_up({"email": email, "password": password})
    if auth_response.user:
        st.session_state.usuario_uid = auth_response.user.id  # Guardar UID
        st.success("✅ Registro exitoso. Ahora inicia sesión.")
    else:
        st.error("❌ No se pudo registrar el usuario.")

# --- Función de login ---
def iniciar_sesion(email, password):
    auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
    if auth_response.user:
        st.session_state.usuario_uid = auth_response.user.id  # Guardar UID
        st.success("✅ Sesión iniciada.")
        return True
    else:
        st.error("❌ Usuario o contraseña incorrectos.")
        return False

# --- Guardar registro ---
def guardar_registro(uid, entrada):
    supabase.table("registros").insert({
        "usuario": uid,  # Guardar UID real
        "contenido": entrada
    }).execute()

# --- Obtener registros del usuario ---
def obtener_registros(uid):
    data = supabase.table("registros").select("*").eq("usuario", uid).execute()
    if data.data:
        return "\n\n".join([r["contenido"] for r in data.data])
    return "No tienes reflexiones guardadas."

# --- Interfaz principal ---
if "usuario_uid" not in st.session_state:
    st.session_state.usuario_uid = None

st.title("🧘 Registro de Conciencia")

if not st.session_state.usuario_uid:
    menu = st.radio("Selecciona una opción:", ["Iniciar Sesión", "Registrarse"])
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")

    if menu == "Registrarse":
        if st.button("Registrar"):
            registrar_usuario(email, password)

    elif menu == "Iniciar Sesión":
        if st.button("Iniciar Sesión"):
            iniciar_sesion(email, password)
else:
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
            entrada = f"""
Fecha: {fecha}
Estado de ánimo: {estado_animo}
Situación actual: {situacion}
Agradecimiento: {agradecimiento}
Meta: {meta}
"""
            guardar_registro(st.session_state.usuario_uid, entrada)
            st.success("✅ Entrada guardada.")

    st.markdown("---")
    with st.expander("📜 Ver mis reflexiones pasadas"):
        registros = obtener_registros(st.session_state.usuario_uid)
        st.text_area("Historial de reflexiones", registros, height=300)
