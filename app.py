import streamlit as st
import yaml
import os

USERS_FILE = "usuarios.yaml"
ADMIN_EMAIL = "admin@admin.com"

# ------------------------
# Funciones de autenticación
# ------------------------

def cargar_usuarios():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def guardar_usuarios(usuarios):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(usuarios, f)

def login(email, password):
    usuarios = cargar_usuarios()
    return usuarios.get(email) == password

def registrar(email, password):
    usuarios = cargar_usuarios()
    if not isinstance(usuarios, dict):
        usuarios = {}
    if email in usuarios:
        return False
    usuarios[email] = password
    guardar_usuarios(usuarios)
    return True

def cambiar_contraseña(email, nueva_contra):
    usuarios = cargar_usuarios()
    if email not in usuarios:
        return False
    usuarios[email] = nueva_contra
    guardar_usuarios(usuarios)
    return True

# ------------------------
# Interfaz Streamlit
# ------------------------

st.set_page_config(page_title="Registro Conciencia", page_icon="🔐")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "email" not in st.session_state:
    st.session_state.email = ""

st.title("🔐 Inicia sesión o regístrate")

tabs = st.tabs(["Iniciar Sesión", "Registrarse"])

# ---------------- TAB LOGIN ----------------
with tabs[0]:
    login_email = st.text_input("Correo electrónico", key="login_email")
    login_password = st.text_input("Contraseña", type="password", key="login_password")
    if st.button("Iniciar sesión"):
        if login(login_email, login_password):
            st.session_state.autenticado = True
            st.session_state.email = login_email
            st.rerun()
            
        else:
            st.error("❌ Credenciales inválidas.")

# ---------------- TAB REGISTRO ----------------
with tabs[1]:
    new_email = st.text_input("Correo electrónico", key="reg_email")
    new_password = st.text_input("Contraseña", type="password", key="reg_password")
    if st.button("Registrarse"):
        if registrar(new_email, new_password):
            st.success("✅ Registro exitoso. Ahora puedes iniciar sesión.")
        else:
            st.error("❌ El correo ya está registrado.")

# ---------------- SESIÓN ACTIVA ----------------
if st.session_state.autenticado:
    st.success(f"Sesión iniciada como: {st.session_state.email}")
    
    st.markdown("### ⚙️ Opciones de cuenta")

    # ---- CAMBIAR CONTRASEÑA ----
    with st.expander("🔒 Cambiar contraseña"):
        nueva_contraseña = st.text_input("Nueva contraseña", type="password")
        if st.button("Actualizar contraseña"):
            if cambiar_contraseña(st.session_state.email, nueva_contraseña):
                st.success("Contraseña actualizada exitosamente.")
            else:
                st.error("No se pudo actualizar la contraseña.")

    # ---- MODO ADMIN ----
    if st.session_state.email == ADMIN_EMAIL:
        with st.expander("👥 Ver todos los usuarios registrados (Admin)"):
            usuarios = cargar_usuarios()
            for user, pwd in usuarios.items():
                st.write(f"📧 {user}")

    # ---- CERRAR SESIÓN ----
    if st.button("Cerrar sesión"):
    st.session_state.usuario_autenticado = None
    st.success("Sesión cerrada.")
    st.rerun()

    # Aquí va tu contenido principal
    st.write("🎯 Contenido principal de tu app...")
