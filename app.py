import streamlit as st
from datetime import datetime
from supabase import create_client
import cohere

# --- Configuración ---
DB_URL = "TU_SUPABASE_URL"
DB_KEY = "TU_SUPABASE_KEY"
COHERE_KEY = "TU_API_KEY_COHERE"

supabase = create_client(DB_URL, DB_KEY)
co = cohere.Client(COHERE_KEY)

# --- Funciones de autenticación ---
def registrar_usuario(usuario, clave):
    existe = supabase.table("usuarios").select("*").eq("usuario", usuario).execute()
    if existe.data:
        return False, "❌ Usuario ya existe."
    supabase.table("usuarios").insert({"usuario": usuario, "clave": clave}).execute()
    return True, "✅ Usuario registrado con éxito."

def autenticar_usuario(usuario, clave):
    data = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("clave", clave).execute()
    return len(data.data) > 0

# --- Funciones de registros ---
def guardar_registro(usuario, entrada):
    supabase.table("registros").insert({"usuario": usuario, "entrada": entrada}).execute()

def obtener_registros(usuario):
    data = supabase.table("registros").select("entrada").eq("usuario", usuario).order("id", desc=True).execute()
    return "\n\n".join([r["entrada"] for r in data.data])

def generar_reflexion(prompt):
    respuesta = co.generate(
        model="command-xlarge-nightly",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
    return respuesta.generations[0].text.strip()

# --- Interfaz ---
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘")

if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = None

if st.session_state.usuario_autenticado is None:
    tabs = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tabs[0]:
        st.subheader("🔐 Iniciar Sesión")
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if autenticar_usuario(usuario, clave):
                st.session_state.usuario_autenticado = usuario
                st.success("✅ Sesión iniciada.")
                st.experimental_rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")

    with tabs[1]:
        st.subheader("🆕 Registrarse")
        usuario = st.text_input("Nuevo usuario")
        clave = st.text_input("Nueva contraseña", type="password")
        if st.button("Registrar"):
            ok, msg = registrar_usuario(usuario, clave)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

else:
    # --- Registro de Conciencia ---
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
            entrada = f"""
Fecha: {fecha}
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

    # --- Mostrar reflexiones pasadas ---
    st.markdown("---")
    with st.expander("📜 Ver mis reflexiones pasadas"):
        registros = obtener_registros(st.session_state.usuario_autenticado)
        st.text_area("Historial de reflexiones", registros, height=300)

    if st.button("Cerrar sesión"):
        st.session_state.usuario_autenticado = None
        st.experimental_rerun()

