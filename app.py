import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# -------------------------
# CONFIGURACIÓN DE LA APP
# -------------------------
st.set_page_config(page_title="Registro de Conciencia", layout="wide")
st.title("📜 Registro de Conciencia")

# -------------------------
# CONEXIÓN A BASE DE DATOS
# -------------------------
DB_URL = st.secrets["DB_URL"]  # Guardado en secrets.toml
engine = create_engine(DB_URL)

# -------------------------
# FUNCIÓN PARA CARGAR DATOS
# -------------------------
@st.cache_data
def cargar_datos():
    query = "SELECT * FROM registros ORDER BY fecha DESC"
    return pd.read_sql(query, engine)

# -------------------------
# CARGAR DATOS
# -------------------------
df = cargar_datos()

if df.empty:
    st.warning("No hay registros en la base de datos.")
else:
    # -------------------------
    # BÚSQUEDA GLOBAL
    # -------------------------
    busqueda = st.text_input("🔍 Buscar en todos los campos", "")
    if busqueda:
        busqueda_lower = busqueda.lower()
        df = df[df.apply(lambda fila: fila.astype(str).str.lower().str.contains(busqueda_lower).any(), axis=1)]

    # -------------------------
    # CONFIGURAR TABLA AGGRID
    # -------------------------
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gb.configure_side_bar()  # Barra lateral de filtros y columnas
    gb.configure_default_column(
        editable=False,
        groupable=True,
        filter=True,
        sortable=True,
        resizable=True
    )
    gb.configure_selection('single', use_checkbox=True)
    grid_options = gb.build()

    # -------------------------
    # MOSTRAR TABLA
    # -------------------------
    AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        theme="alpine",  # Temas: "alpine", "balham", "material"
        height=500
    )
