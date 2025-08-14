# --- Registro de Conciencia ---
st.title("🧘 Registro de Conciencia")
st.markdown("Responde las siguientes preguntas para registrar tu estado y generar una reflexión.")

# Preguntas originales
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
        
        # Guardar en Supabase
        supabase.table("registros").insert({
            "usuario": st.session_state.usuario_autenticado,
            "fecha": fecha,
            "estado_animo": estado_animo,
            "situacion": situacion,
            "agradecimiento": agradecimiento,
            "meta": meta
        }).execute()

        st.success("✅ Entrada guardada y analizada por la IA.")

        # Generar reflexión con IA
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

# Mostrar reflexiones pasadas
st.markdown("---")
with st.expander("📜 Ver mis reflexiones pasadas"):
    registros = supabase.table("registros").select("*").eq("usuario", st.session_state.usuario_autenticado).order("fecha", desc=True).execute()
    if registros.data:
        texto_registros = "\n\n".join(
            f"{r['fecha']} - Estado: {r['estado_animo']} - Reflexión: {r.get('reflexion', '')}"
            for r in registros.data
        )
        st.text_area("Historial de reflexiones", texto_registros, height=300)
    else:
        st.info("Aún no tienes reflexiones guardadas.")
