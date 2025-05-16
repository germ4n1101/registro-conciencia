import streamlit as st
import json
import os

USERS_FILE = "usuarios.json"
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "admin"

# Función para cargar usuarios
def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

# Función para guardar usuarios
def guardar_usuarios(usuarios):
    with open(USERS_FILE, "w") as f:
        json.dump(usuarios, f)

# Interfaz principal
def main():
    st.title("🔐 Inicia sesión o regístrate")

    usuarios = cargar_usuarios()
    
    if "sesion_iniciada" not in st.session_state:
        st.session_state.sesion_iniciada = False
        st.session_state.usuario_actual = None

    tabs = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tabs[0]:
        email = st.text_input("Correo electrónico", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_password")

        if st.button("Iniciar sesión"):
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                st.session_state.sesion_iniciada = True
                st.session_state.usuario_actual = "admin"
                st.success("Sesión iniciada como administrador.")
                st.rerun()
            elif email in usuarios and usuarios[email] == password:
                st.session_state.sesion_iniciada = True
                st.session_state.usuario_actual = email
                st.success("Sesión iniciada con éxito.")
                st.rerun()
            else:
                st.error("❌ Credenciales inválidas.")

    with tabs[1]:
        new_email = st.text_input("Correo electrónico", key="register_email")
        new_password = st.text_input("Contraseña", type="password", key="register_password")

        if st.button("Registrarse"):
            if new_email in usuarios:
                st.warning("⚠️ Este correo ya está registrado.")
            else:
                usuarios[new_email] = new_password
                guardar_usuarios(usuarios)
                st.success("Usuario registrado con éxito. Ahora puedes iniciar sesión.")
                st.rerun()

    # Vista para usuarios logueados
    if st.session_state.sesion_iniciada:
        st.divider()
        st.write(f"👋 Bienvenido **{st.session_state.usuario_actual}**")

        if st.session_state.usuario_actual == "admin":
            st.subheader("👥 Usuarios registrados")
            for correo in usuarios:
                st.write(f"📧 {correo}")
        else:
            st.subheader("🔑 Cambiar contraseña")
            nueva_pass = st.text_input("Nueva contraseña", type="password")
            if st.button("Actualizar contraseña"):
                usuarios[st.session_state.usuario_actual] = nueva_pass
                guardar_usuarios(usuarios)
                st.success("Contraseña actualizada.")

        if st.button("Cerrar sesión"):
            st.session_state.sesion_iniciada = False
            st.session_state.usuario_actual = None
            st.success("Sesión cerrada.")
            st.rerun()

if __name__ == "__main__":
    main()

