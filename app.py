import streamlit as st
import datetime
import cohere
import os

# Inicializar Cohere
co = cohere.Client(os.getenv("api_key"))  # Usa variable de entorno

# Configuración de la página
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘")

# -------------------------
# Funciones de autenticación
# -------------------------
def cargar_usuarios():
    usuarios = {}
    if os.path.exists("usuarios.txt"):
        with open("usuarios.txt", "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if linea:
                    user, pwd = linea.split(":", 1)
                    usuarios[user] = pwd
    return usuarios

def guardar_usuario(usuario, clave):
    with open("usuarios.txt", "a", encoding="utf-8") as f:
        f.write(f"{usuario}:{clave}\n")

# -------------------------
# Pantalla de autenticación
# -------------------------
st.title("🔑 Acceso a Registro de Conciencia")

opcion = st.radio("Selecciona una opción:", ["Iniciar Sesión", "Registrarse"])

usuarios = cargar_usuarios()

usuario = st.text_input("Usuario")
clave = st.text_input("Contraseña", type="password")

if opcion == "Registrarse":
    if st.button("Crear cuenta"):
        if usuario in usuarios:
            st.error("⚠️ El usuario ya existe.")
        elif not usuario or not clave:
            st.warning("Por favor, completa todos los campos.")
        else:
            guardar_usuario(usuario, clave)
            st.success("✅ Usuario registrado. Ahora puedes iniciar sesión.")

elif opcion == "Iniciar Sesión":
    if st.button("Entrar"):
        if usuario in usuarios and usuarios[usuario] == clave:
            st.session_state["autenticado"] = usuario
            st.success(f"Bienvenido, {usuario}")
        else:
            st.error("⚠️ Usuario o contraseña incorrectos.")

# -------------------------
# Formulario de preguntas
# -------------------------
if "autenticado" in st.session_state:
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
            fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entrada = f"""
Fecha: {fecha}
Usuario: {st.session_state['autenticado']}
Estado de ánimo: {estado_animo}
Situación actual: {situacion}
Agradecimiento: {agradecimiento}
Meta: {meta}
"""
            with open("registro_conciencia.txt", "a", encoding="utf-8") as archivo:
                archivo.write(entrada + "\n" + "-"*40 + "\n")

            st.success("✅ Entrada guardada y analizada por la IA.")

            try:
                prompt_ia = (
                    f"Soy una persona reflexiva. Hoy escribí:\n\n"
                    f"Estado de ánimo: {estado_animo}\n"
                    f"Situación actual: {situacion}\n"
                    f"Agradecimiento: {agradecimiento}\n"
                    f"Meta: {meta}\n\n"
                    f"Por favor genera una reflexión amable, positiva y consciente basada en esta información."
                )

                respuesta = co.chat(
                    model="command-nightly",
                    message=prompt_ia
                )

                st.subheader("🧠 Reflexión de la IA")
                st.write(respuesta.text)

            except Exception as e:
                st.error(f"⚠️ Error con la IA: {e}")


