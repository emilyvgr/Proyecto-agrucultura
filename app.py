import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


st.set_page_config(page_title="Proyecto Cultivos", page_icon="logo solo.svg")

df = pd.read_csv("agricultura.csv")

columnas_es = {
    'Crop': 'cultivo',
    'Crop_Year': 'año',
    'Season': 'temporada',
    'State': 'estado',
    'Area': 'area',
    'Production': 'produccion',
    'Annual_Rainfall': 'precipitacion_anual',
    'Fertilizer': 'fertilizante',
    'Pesticide': 'pesticida',
    'Yield': 'rendimiento'
}
df.rename(columns=columnas_es, inplace=True)

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

df = df.drop_duplicates()

for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].str.strip()

df = df.infer_objects()

q1_produccion = df["produccion"].quantile(0.25)
q3_produccion = df["produccion"].quantile(0.75)
iqr_produccion = q3_produccion - q1_produccion
lower_bound_produccion = q1_produccion - 1.5 * iqr_produccion
upper_bound_produccion = q3_produccion + 1.5 * iqr_produccion
df = df.query("produccion >= @lower_bound_produccion and produccion <= @upper_bound_produccion")

q1_fertilizante = df["fertilizante"].quantile(0.25)
q3_fertilizante = df["fertilizante"].quantile(0.75)
iqr_fertilizante = q3_fertilizante - q1_fertilizante
lower_bound_fertilizante = q1_fertilizante - 1.5 * iqr_fertilizante
upper_bound_fertilizante = q3_fertilizante + 1.5 * iqr_fertilizante
df = df.query("fertilizante >= @lower_bound_fertilizante and fertilizante <= @upper_bound_fertilizante")

q1_area = df["area"].quantile(0.25)
q3_area = df["area"].quantile(0.75)
iqr_area = q3_area - q1_area
lower_bound_area = q1_area - 1.5 * iqr_area
upper_bound_area = q3_area + 1.5 * iqr_area
df = df.query("area >= @lower_bound_area and area <= @upper_bound_area")
 
df = df.query("año >= 2010 and año <= 2020")

df = df[df['temporada'] != 'Whole Year']
df['temporada'] = df['temporada'].replace('Summer', 'Zaid')
df['temporada'] = df['temporada'].replace('Winter', 'Rabi')
df['temporada'] = df['temporada'].replace('Autumn', 'Kharif')

st.markdown("""
    <style>
    /* Estilo para los contenedores de datos y tablas */
    [data-testid="stDataFrame"], .stPlotlyChart {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 10px;
        border: 2px solid #E0E0E0;
        box-shadow: 2px 2px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)


#tabla de calculos basicos
st.markdown("""
        <h1 style='text-align: center; color: #444444; font-size: 18px; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;'>
        Tabla de Calculos Estadisticos para los Factores Determinantes en Ciclos Agrícola
        </h1>
        """, unsafe_allow_html=True)   
st.dataframe(
        df.describe().style.format("{:.2f}"), 
        use_container_width=True )


#Pregunta 1
st.markdown("""
        <h1 style='text-align: center; color: #444444; font-size: 18px; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;'>
        Influencia del Fertilizante en el Rendimiento por Temporada
        </h1>
        """, unsafe_allow_html=True) 
df_estudio = df.copy()
columnas_interes = ['fertilizante', 'pesticida', 'rendimiento']
correlacion = df_estudio.groupby('temporada')[columnas_interes].corr().unstack()
fig_a = px.scatter(df_estudio, x='fertilizante', y='rendimiento', color='temporada', 
    labels={
        'fertilizante': 'Fertilizante Aplicado',
        'rendimiento': 'Rendimiento (Yield)',
        'temporada': 'Temporada del Año'
    }, opacity=0.6)
st.plotly_chart(fig_a)


#pregunta 2
st.markdown("""
        <h1 style='text-align: center; color: #444444; font-size: 18px; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;'>
        Rendimiento según Nivel de Fertilizante
        </h1>
        """, unsafe_allow_html=True) 
mediana_fert = df_estudio['fertilizante'].median()
df_estudio['nivel_fertilizante'] = df_estudio['fertilizante'].apply(lambda x: 'Alto' if x > mediana_fert else 'Bajo')
resumen_b = df_estudio.groupby('nivel_fertilizante')['rendimiento'].describe()
fig_b = px.box(df_estudio, x='nivel_fertilizante', y='rendimiento', color='temporada')
st.plotly_chart(fig_b)


#pregunta 3
st.markdown("""
        <h1 style='text-align: center; color: #444444; font-size: 18px; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;'>
        Distribución de Precipitaciones en Cultivos de Alto Rendimiento
        </h1>
        """, unsafe_allow_html=True)
alto_rendimiento = df_estudio[df_estudio['rendimiento'] >= df_estudio['rendimiento'].quantile(0.75)]
lluvia_ideal = alto_rendimiento.groupby('temporada')['precipitacion_anual'].median()
fig_c = px.histogram(alto_rendimiento, x='precipitacion_anual', color='temporada', barmode='overlay')
st.plotly_chart(fig_c)
