import streamlit as st
import yaml
import os
import cohere
from datetime import datetime

# API Key de Cohere (reemplaza con la tuya)
#COHERE_API_KEY = "hTRHKEoz2gRAe68ILa7SqCq6T82lZn1muCV619EX"
#co = cohere.Client(COHERE_API_KEY)
try:
    cohere_api_key = st.secrets["cohere"]["api_key"]
    co = cohere.Client(COHERE_API_KEY)
except KeyError:
    st.error("❌ No se encontró la clave API de Cohere en .streamlit/secrets.toml.")
    st.stop()

def generar_reflexion(prompt):
    if not prompt or prompt.strip() == "":
        st.warning("⚠️ El contenido del prompt está vacío. Por favor completa tus respuestas.")
        return "No se puede generar una reflexión sin contenido."

    try:
        response = cohere_client.generate(
            model="command",  # Usa un modelo disponible en el plan gratuito
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except cohere.CohereError as e:
        st.error(f"❌ Error al generar reflexión: {str(e)}")
        return "Ocurrió un error al generar la reflexión con la IA."

USERS_FILE = "usuarios.yaml"
# Configuración de la página
st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘")
st.title("🧘 Registro de Conciencia")
st.markdown("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

# Preguntas de entrada
estado_animo = st.text_input("1. ¿Cómo te sientes hoy?")
situacion = st.text_input("2. ¿Qué ha estado ocupando tus pensamientos últimamente?")
agradecimiento = st.text_input("3. ¿Qué agradeces hoy?")
meta = st.text_input("4. ¿Qué te gustaría lograr o mejorar?")

# Botón de guardar y reflexionar
if st.button("Guardar y reflexionar"):
    if not any([estado_animo, situacion, agradecimiento, meta]):
        st.warning("Por favor responde al menos una pregunta.")
    else:
        # Guardar entrada
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada = f"""
        Fecha: {fecha}
        Estado de ánimo: {estado_animo}
        Situación actual: {situacion}
        Agradecimiento: {agradecimiento}
        Meta: {meta}
        """
        with open("registro_conciencia.txt", "a", encoding="utf-8") as archivo:
            archivo.write(entrada + "\n" + "-"*40 + "\n")

        st.success("✅ Entrada guardada y analizada por la IA.")

        try:
            # Generar reflexión con Cohere
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
