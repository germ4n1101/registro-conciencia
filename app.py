import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- Configuración de página ---
st.set_page_config(page_title="Registro de Conciencia", layout="wide")

# --- Validar credenciales de Supabase ---
try:
    DB_URL = st.secrets["DB_URL"]
    DB_KEY = st.secrets["DB_KEY"]
except KeyError as e:
    st.error(f"❌ Falta la variable {e} en secrets.toml")
    st.stop()

if not DB_URL.startswith("https://") or ".supabase.co" not in DB_URL:
    st.error("❌ La URL de Supabase no es válida. Ejemplo: https://xxxxxx.supabase.co")
    st.stop()

if not DB_KEY or len(DB_KEY) < 40:
    st.error("❌ La API Key de Supabase no es válida.")
    st.stop()

try:
    supabase = create_client(DB_URL, DB_KEY)
except Exception as e:
    st.error(f"❌ Error al conectar con Supabase: {e}")
    st.stop()

# --- Funciones de autenticación ---
def registrar_usuario(usuario, clave):
    data = supabase.table("usuarios").select("*").eq("usuario", usuario).execute()
    if data.data:
        return False, "Usuario ya registrado."
    supabase.table("usuarios").insert({"usuario": usuario, "clave": clave}).execute()
    return True, "Registro exitoso."

def login_usuario(usuario, clave):
    data = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("clave", clave).execute()
    return bool(data.data)

def guardar_respuesta(usuario, pregunta, respuesta):
    supabase.table("respuestas").insert({
        "usuario": usuario,
        "pregunta": pregunta,
        "respuesta": respuesta,
        "fecha": datetime.now().isoformat()
    }).execute()

def obtener_respuestas(usuario):
    data = supabase.table("respuestas").select("*").eq("usuario", usuario).order("fecha", desc=True).execute()
    return pd.DataFrame(data.data)

# --- Estado de sesión ---
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# --- Login o registro ---
if not st.session_state.usuario:
    tabs = st.tabs(["🔑 Iniciar Sesión", "🆕 Registrarse"])

    with tabs[0]:
        usuario = st.text_input("Usuario", key="login_usuario")
        clave = st.text_input("Contraseña", type="password", key="login_clave")
        if st.button("Iniciar sesión"):
            if login_usuario(usuario, clave):
                st.session_state.usuario = usuario
                st.success("✅ Sesión iniciada")
                st.experimental_rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")

    with tabs[1]:
        nuevo_usuario = st.text_input("Nuevo usuario", key="reg_usuario")
        nueva_clave = st.text_input("Nueva contraseña", type="password", key="reg_clave")
        if st.button("Registrarse"):
            ok, msg = registrar_usuario(nuevo_usuario, nueva_clave)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

# --- Pantalla principal ---
else:
    st.sidebar.write(f"👋 Bienvenido, **{st.session_state.usuario}**")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.usuario = None
        st.experimental_rerun()

    st.title("🧠 Registro de Conciencia")
    st.write("Responde las preguntas para reflexionar y llevar un historial.")

    preguntas = [
        "¿Qué fue lo mejor que pasó hoy?",
        "¿Qué aprendiste hoy?",
        "¿Qué podrías mejorar mañana?"
    ]

    with st.form("form_preguntas"):
        respuestas = {}
        for p in preguntas:
            respuestas[p] = st.text_area(p, "")
        enviar = st.form_submit_button("Guardar respuestas")

        if enviar:
            for pregunta, respuesta in respuestas.items():
                if respuesta.strip():
                    guardar_respuesta(st.session_state.usuario, pregunta, respuesta)
            st.success("✅ Respuestas guardadas con éxito.")

    st.subheader("📜 Historial de respuestas")
    df = obtener_respuestas(st.session_state.usuario)

    if not df.empty:
        busqueda = st.text_input("Buscar en respuestas")
        if busqueda:
            df = df[df["respuesta"].str.contains(busqueda, case=False, na=False)]

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay respuestas registradas aún.")



