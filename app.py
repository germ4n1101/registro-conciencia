import streamlit as st
import cohere
import datetime
import os

st.set_page_config(page_title="Registro de Conciencia", page_icon="🧘‍♂️")

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

st.title("🧘‍♂️ Registro de Conciencia")
st.markdown("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

hoy = datetime.date.today().strftime("%d/%m/%Y")

# Preguntas
q1 = st.text_input("¿Cómo te sientes hoy?")
q2 = st.text_input("¿Qué ha estado ocupando tus pensamientos últimamente?")
q3 = st.text_input("¿Qué agradeces hoy?")
q4 = st.text_input("¿Qué te gustaría lograr o mejorar?")

if st.button("Guardar y reflexionar"):
    if not all([q1, q2, q3, q4]):
        st.warning("Por favor responde todas las preguntas antes de continuar.")
    else:
        entrada_usuario = (
            f"Fecha: {hoy}\n"
            f"Estado emocional: {q1}\n"
            f"Pensamientos: {q2}\n"
            f"Agradecimiento: {q3}\n"
            f"Meta: {q4}"
        )

        prompt = (
            "Actúa como una mente sabia y reflexiva que guía con compasión. "
            "A partir del siguiente registro personal, escribe una reflexión motivadora, clara y positiva:"
            f"\n\n{entrada_usuario}\n\nReflexión:"
        )

        try:
            respuesta = co.chat(
                model="command-r-plus",
                message=prompt
            )
            reflexion = respuesta.text
            st.success("✅ Entrada guardada y analizada por la IA.")
            st.markdown("## 🧠 Reflexión de la IA")
            st.write("**Reflexión:**")
            st.write(reflexion)
        except Exception as e:
            st.error(f"⚠️ Error con la IA: {e}")
