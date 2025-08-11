import streamlit as st
import sqlite3
import cohere
import os
from datetime import datetime

# -------------------------------
# Configuración página
# -------------------------------
st.set_page_config(page_title="Registro de Conciencia", layout="wide")

# -------------------------------
# Inicializar base de datos
# -------------------------------
def init_db():
    conn = sqlite3.connect("registro_conciencia.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entradas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            contenido TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------------------
# Conectar a Cohere (manejo seguro)
# -------------------------------
cohere_api_key = None
if "cohere" in st.secrets and "api_key" in st.secrets["cohere"]:
    cohere_api_key = st.secrets["cohere"]["api_key"]
elif os.getenv("COHERE_API_KEY"):
    cohere_api_key = os.getenv("COHERE_API_KEY")

if cohere_api_key:
    co = cohere.Client(cohere_api_key)
else:
    st.warning("⚠️ No se encontró la clave API de Cohere. La IA no estará disponible.")
    co = None

# -------------------------------
# Funciones CRUD
# -------------------------------
def agregar_entrada(contenido):
    conn = sqlite3.connect("registro_conciencia.db")
    c = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO entradas (fecha, contenido) VALUES (?, ?)", (fecha, contenido))
    conn.commit()
    conn.close()

def obtener_entradas():
    conn = sqlite3.connect("registro_conciencia.db")
    c = conn.cursor()
    c.execute("SELECT * FROM entradas ORDER BY fecha DESC")
    data = c.fetchall()
    conn.close()
    return data

def actualizar_entrada(id, nuevo_contenido):
    conn = sqlite3.connect("registro_conciencia.db")
    c = conn.cursor()
    c.execute("UPDATE entradas SET contenido = ? WHERE id = ?", (nuevo_contenido, id))
    conn.commit()
    conn.close()

def eliminar_entrada(id):
    conn = sqlite3.connect("registro_conciencia.db")
    c = conn.cursor()
    c.execute("DELETE FROM entradas WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# -------------------------------
# Función para generar reflexión
# -------------------------------
def generar_reflexion(prompt):
    if not prompt.strip():
        return "No se puede generar una reflexión sin contenido."
    if not co:
        return "⚠️ IA no disponible. Falta clave API de Cohere."
    try:
        response = co.chat(model="command-nightly", message=prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error al generar reflexión: {e}"

# -------------------------------
# Interfaz
# -------------------------------
st.title("📖 Registro de Conciencia")

tab1, tab2 = st.tabs(["➕ Nueva entrada", "📜 Historial"])

# --- Nueva entrada ---
with tab1:
    contenido = st.text_area("Escribe tu entrada de conciencia", height=200)

    if st.button("Guardar entrada"):
        if contenido.strip():
            agregar_entrada(contenido)
            st.success("✅ Entrada guardada correctamente.")
        else:
            st.warning("⚠️ El contenido no puede estar vacío.")

    if st.button("Generar reflexión con IA"):
        if contenido.strip():
            reflexion = generar_reflexion(contenido)
            st.text_area("Reflexión generada", reflexion, height=200)
        else:
            st.warning("⚠️ Escribe algo para que la IA pueda generar una reflexión.")

# --- Historial ---
with tab2:
    entradas = obtener_entradas()
    
    search_term = st.text_input("🔍 Buscar en historial")
    if search_term:
        entradas = [e for e in entradas if search_term.lower() in e[2].lower()]

    items_per_page = 5
    total_pages = (len(entradas) - 1) // items_per_page + 1
    page = st.number_input("Página", min_value=1, max_value=total_pages, step=1)

    start = (page - 1) * items_per_page
    end = start + items_per_page

    for id, fecha, contenido in entradas[start:end]:
        with st.expander(f"{fecha} - {contenido[:50]}..."):
            nuevo_texto = st.text_area(f"Editar entrada {id}", contenido, key=f"edit_{id}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Guardar cambios", key=f"save_{id}"):
                    actualizar_entrada(id, nuevo_texto)
                    st.success("✅ Entrada actualizada.")
            with col2:
                if st.button("🗑 Eliminar", key=f"delete_{id}"):
                    eliminar_entrada(id)
                    st.warning("❌ Entrada eliminada.")


