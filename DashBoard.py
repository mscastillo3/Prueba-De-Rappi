import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go





# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard Disponibilidad Tiendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILO VISUAL
# =========================
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: white;
    }
    .block-container {
        padding-top: 2rem;
    }
    .metric-card {
        background: #1c1f26;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def load_data():
    
    df = pd.read_excel("Data/Consolidado.xlsx")
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    
    return (df)
    



df = load_data()

from collections import defaultdict



# =========================
# SIDEBAR (FILTROS)
# =========================


st.sidebar.image("Imagenes\image.png", use_container_width=True)

st.sidebar.title("🔎 Filtros")

if "Fecha" in df.columns:
    min_date = df["Fecha"].min()
    max_date = df["Fecha"].max()

    fechas_disponibles = sorted(df["Fecha"].dt.date.unique())
    rango_fechas = st.sidebar.date_input(
        "Rango de fechas",
        value=(fechas_disponibles[0], fechas_disponibles[-1]),
        min_value=fechas_disponibles[0],
        max_value=fechas_disponibles[-1]
    )


    if len(rango_fechas) == 2:
        fecha_inicio, fecha_fin = rango_fechas
        df = df[
            (df["Fecha"].dt.date >= fecha_inicio) &
            (df["Fecha"].dt.date <= fecha_fin)
        ]
    else:
        st.stop()

nivel  = st.sidebar.radio(
    "Unidad de tiempo",
    ["Segundos", "Minutos", "Horas"]
)

grupos = defaultdict(list)
time_cols = df.columns.drop("Fecha")
if nivel == "Horas" or nivel == "Minutos":
    for col in time_cols:
        partes = col.split(":")   # hh:mm:ss
        if nivel == "Horas":
            clave = partes[0]                 # 00

        elif nivel == "Minutos":
            clave = f"{partes[0]}:{partes[1]}"   # 00:05

      # segundo exacto

        grupos[clave].append(col)
    resultado = df.copy()

    for grupo, columnas in grupos.items():
        resultado[grupo] = df[columnas].mean(axis=1)

    columnas_base = [c for c in df.columns if ":" not in c]

    df = resultado[columnas_base + list(grupos.keys())]
else:
    df = df





# =========================
# HEADER
# =========================



st.title("📊 Dashboard de Disponibilidad de Tiendas")
st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# =========================
# KPIs PRINCIPALES
# =========================
col1, col2= st.columns(2)

avg_disp = round(df[df.columns.drop("Fecha")].mean().mean(), 2)


col1.metric("📦 Disponibilidad Promedio", f"{avg_disp}")

col2.metric("📊 Dias Registrados", len(df))

st.divider()

# =========================
# GRÁFICOS PRINCIPALES
# =========================

# ---- Evolución temporal

st.subheader("Promedio de disponibilidad por tiempo")

df_numeric = df.drop(columns=["Fecha"]).select_dtypes(include="number")

y = df_numeric.mean()
x = y.index

print(y)
fig = px.line(
    x=x,
    y=y,
    labels={"x": "Tiempo", "y": "Promedio de disponibilidad"},
    color_discrete_sequence=["rgb(245, 73, 39)"]
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Promedio de disponibilidad por Fecha")

df_numeric = df.drop(columns=["Fecha"]).select_dtypes(include="number")

y = df_numeric.mean(axis=1)
x = df["Fecha"]


fig2 = px.bar(
    x= df["Fecha"],
    y=y,
    labels={"x": "Fecha", "y": "Promedio de disponibilidad"},
    color_discrete_sequence=["rgb(245, 73, 39)"]
)

fig2.update_xaxes(
    tickformat="%b %d",
    tickmode="linear"
)
st.plotly_chart(fig2, use_container_width=True)



# Head MAP
# =========================

st.subheader("Mapa de Calor por dias de la semana")
df["DiaSemana"] = df["Fecha"].dt.day_name(locale="es_ES")
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
heatmap_data = df.groupby("DiaSemana").mean(numeric_only=True)
heatmap_data = heatmap_data.reindex(dias)
fig3 = go.Figure(
    data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale="RdYlGn_r"
    )
)


st.plotly_chart(fig3, use_container_width=True)
# =========================
# TABLA FINAL
# =========================
st.subheader("📋 Datos Detallados")

st.dataframe(df, use_container_width=True)

# =========================


