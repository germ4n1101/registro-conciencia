import streamlit as st
from supabase import create_client, Client
import bcrypt

# Configuración de conexión a Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ---------- Funciones ----------
def registrar_usuario(username, password):
    # Verificar si el usuario ya existe
    existente = supabase.table("usuarios").select("*").eq("username", username).execute()
    if existente.data:
        return False, "El usuario ya existe."
    
    # Hashear la contraseña
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    # Insertar en la base de datos
    supabase.table("usuarios").insert({"username": username, "password": hashed}).execute()
    return True, "Usuario registrado correctamente."

def verificar_usuario(username, password):
    usuario = supabase.table("usuarios").select("*").eq("username", username).execute()
    if not usuario.data:
        return False
    
    # Comparar contraseña ingresada con la guardada
    stored_hash = usuario.data[0]["password"]
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))

# ---------- Interfaz ----------
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧠")

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if not st.session_state.usuario:
    tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

    with tab1:
        st.subheader("Inicia Sesión")
        usuario = st.text_input("Usuario", key="login_user")
        clave = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Entrar"):
            if verificar_usuario(usuario, clave):
                st.session_state.usuario = usuario
                st.success(f"Bienvenido, {usuario} 👋")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

    with tab2:
        st.subheader("Registro")
        nuevo_usuario = st.text_input("Nuevo usuario", key="reg_user")
        nueva_clave = st.text_input("Nueva contraseña", type="password", key="reg_pass")
        if st.button("Registrar"):
            ok, msg = registrar_usuario(nuevo_usuario, nueva_clave)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

else:
    st.title("Registro de Conciencia 🧠")
    st.write(f"Usuario: **{st.session_state.usuario}**")
    
    pregunta1 = st.text_area("¿Qué fue lo más importante que aprendiste hoy?")
    pregunta2 = st.text_area("¿Qué podrías haber hecho diferente?")
    pregunta3 = st.text_area("Describe un momento que te hizo sentir bien.")
    
    if st.button("Guardar Reflexión"):
        with open(f"{st.session_state.usuario}_reflexiones.txt", "a", encoding="utf-8") as f:
            f.write(f"---\nUsuario: {st.session_state.usuario}\n")
            f.write(f"1. {pregunta1}\n2. {pregunta2}\n3. {pregunta3}\n\n")
        st.success("Reflexión guardada correctamente.")
    
    if st.button("Cerrar Sesión"):
        st.session_state.usuario = None
        st.rerun()

