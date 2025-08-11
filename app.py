import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# -------------------------
# CONFIGURACIÓN APP
# -------------------------
st.set_page_config(page_title="Registro de Conciencia", layout="wide")
st.title("📜 Registro de Conciencia - CRUD Supabase")

# -------------------------
# CONEXIÓN A BASE DE DATOS
# -------------------------
DB_URL = st.secrets["DB_URL"]  # Guardado en secrets.toml
engine = create_engine(DB_URL)

# -------------------------
# FUNCIONES
# -------------------------
@st.cache_data(ttl=60)
def cargar_datos():
    query = "SELECT * FROM registros ORDER BY fecha DESC"
    return pd.read_sql(query, engine)

def agregar_registro(usuario, fecha, texto):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO registros (usuario, fecha, texto) VALUES (:u, :f, :t)"),
            {"u": usuario, "f": fecha, "t": texto}
        )

def eliminar_registro(id_registro):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM registros WHERE id = :id"), {"id": id_registro})

# -------------------------
# FORMULARIO PARA NUEVO REGISTRO
# -------------------------
st.subheader("➕ Agregar nuevo registro")
with st.form("nuevo_registro"):
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("👤 Usuario")
    with col2:
        fecha = st.date_input("📅 Fecha")
    texto = st.text_area("📝 Texto del registro")
    
    submitted = st.form_submit_button("Guardar")
    if submitted:
        if usuario and fecha and texto:
            agregar_registro(usuario, fecha, texto)
            st.success("Registro agregado correctamente ✅")
            st.cache_data.clear()
        else:
            st.error("⚠️ Todos los campos son obligatorios.")

# -------------------------
# MOSTRAR TABLA DE REGISTROS
# -------------------------
st.subheader("📂 Lista de registros")

df = cargar_datos()

# Búsqueda global
busqueda = st.text_input("🔍 Buscar", "")
if busqueda:
    busqueda_lower = busqueda.lower()
    df = df[df.apply(lambda fila: fila.astype(str).str.lower().str.contains(busqueda_lower).any(), axis=1)]

if df.empty:
    st.warning("No hay registros que coincidan.")
else:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gb.configure_side_bar()
    gb.configure_default_column(
        editable=False, groupable=True, filter=True, sortable=True, resizable=True
    )
    gb.configure_selection('single', use_checkbox=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        theme="alpine",
        height=500
    )

    # Eliminar registro seleccionado
    if grid_response["selected_rows"]:
        id_seleccionado = grid_response["selected_rows"][0]["id"]
        if st.button("🗑 Eliminar registro seleccionado"):
            eliminar_registro(id_seleccionado)
            st.success("Registro eliminado ✅")
            st.cache_data.clear()
