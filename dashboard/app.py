import streamlit as st
import plotly.express as px
import sys
import os

# Agregar path para importar db_utils
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.db_utils import get_all_properties, get_unique_zones, get_unique_cities

# Configuración de la página
st.set_page_config(page_title="Oikos Data Exploration", page_icon="🏠", layout="wide")


# Cargar datos con caching
@st.cache_data
def load_data():
    """Carga los datos de la base de datos"""
    return get_all_properties()


# Funciones helper para filtros
def get_cities_by_zone(zona):
    """Obtiene ciudades de una zona específica"""
    if zona == "Todas":
        return get_unique_cities()
    return df[df["zona"] == zona]["ciudad"].unique().tolist()


# Cargar datos
df = load_data()

# ===============================
# HEADER - Título y Métricas
# ===============================

st.title("Oikos Complete Data Exploration")
st.markdown(
    "Explore the complete dataset of properties with interactive filters."
)  # Descripción

# Separador
st.markdown("---")

# Métricas en 4 columnas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Properties", f"{len(df):,}")

with col2:
    st.metric("Average Price", f"${df['precio'].mean():,.0f}")

with col3:
    st.metric("Average Area", f"{df['area'].mean():.0f} m²")

with col4:
    st.metric("Precio/m²", f"${df['precio_por_m2'].mean():,.0f}")

# Separador
st.markdown("---")

# ============================================================
# EXPLORACIÓN DE DATOS - Filtros y Tabla
# ============================================================

st.markdown("")  # Espaciado

# Inicializar session_state si no existe
if "zona_filter" not in st.session_state:
    st.session_state.zona_filter = "Todas"
if "ciudad_filter" not in st.session_state:
    st.session_state.ciudad_filter = "Todas"

# Filtros en 4 columnas
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Lista de zonas
    zonas_list = ["Todas"] + get_unique_zones()

    # Índice actual basado en session_state
    zona_index = (
        zonas_list.index(st.session_state.zona_filter)
        if st.session_state.zona_filter in zonas_list
        else 0
    )

    # Selectbox de zona
    zona_seleccionada = st.selectbox(
        "Zone", zonas_list, index=zona_index, key="selectbox_zona"
    )

    # Actualizar session_state si cambió
    if zona_seleccionada != st.session_state.zona_filter:
        st.session_state.zona_filter = zona_seleccionada
        # Si cambió la zona, resetear ciudad a "Todas"
        st.session_state.ciudad_filter = "Todas"
        st.rerun()

with col2:
    # Solo habilitar si se seleccionó una zona específica
    ciudad_habilitada = st.session_state.zona_filter != "Todas"

    if ciudad_habilitada:
        # Obtener ciudades disponibles según la zona
        ciudades_disponibles = get_cities_by_zone(st.session_state.zona_filter)
        ciudades_list = ["Todas"] + sorted(ciudades_disponibles)

        # Índice actual
        ciudad_index = (
            ciudades_list.index(st.session_state.ciudad_filter)
            if st.session_state.ciudad_filter in ciudades_list
            else 0
        )

        # Selectbox habilitado
        ciudad_seleccionada = st.selectbox(
            "City", ciudades_list, index=ciudad_index, key="selectbox_ciudad"
        )

        # Actualizar session_state si cambió
        if ciudad_seleccionada != st.session_state.ciudad_filter:
            st.session_state.ciudad_filter = ciudad_seleccionada
            st.rerun()
    else:
        # Selectbox deshabilitado
        st.selectbox(
            "City",
            ["First select a zone"],
            disabled=True,
            key="selectbox_ciudad_disabled",
        )
        st.session_state.ciudad_filter = "Todas"

with col3:
    precio_min = st.number_input(
        "Minimum Price (USD)", min_value=0, max_value=2000000, value=0, step=10000
    )

with col4:
    precio_max = st.number_input(
        "Maximum Price (USD)", min_value=0, max_value=2000000, value=2000000, step=10000
    )

# Aplicar filtros al DataFrame usando session_state
df_filtrado = df.copy()

if st.session_state.zona_filter != "Todas":
    df_filtrado = df_filtrado[df_filtrado["zona"] == st.session_state.zona_filter]

if st.session_state.ciudad_filter != "Todas":
    df_filtrado = df_filtrado[df_filtrado["ciudad"] == st.session_state.ciudad_filter]

df_filtrado = df_filtrado[
    (df_filtrado["precio"] >= precio_min) & (df_filtrado["precio"] <= precio_max)
]

# Mostrar resultados
st.info(f"📊 Showing **{len(df_filtrado):,}** of **{len(df):,}** properties")

# Tabla interactiva
st.dataframe(
    df_filtrado[
        [
            "zona",
            "ciudad",
            "precio",
            "area",
            "ambientes",
            "bathrooms",
            "precio_por_m2",
            "url",
        ]
    ],
    use_container_width=True,
    height=400,
)
