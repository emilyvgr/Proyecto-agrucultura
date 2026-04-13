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

estadisticas = df.describe()
estadisticas = estadisticas.rename(index={
    'count': 'Total (N)',
    'mean': 'Promedio',
    'std': 'Des. Tipica',
    'min': 'Mínimo',
    '25%': '25%',
    '50%': 'Mediana',
    '75%': '75%',
    'max': 'Máximo'
})

st.markdown("""
        <style>
        /* Aplicamos el diseño a los contenedores de tablas */
        [data-testid="stDataFrame"],.stPlotlyChart {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 15px;
        border: 2px solid #E0E0E0;
        box-shadow: 2px 2px 15px rgba(0,0,0,0.05);
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
    estadisticas.style.format("{:.2f}"), 
    use_container_width=True)

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
        'rendimiento': 'Rendimiento',
        'temporada': 'Temporada'
    }, opacity=0.6)
st.plotly_chart(fig_a, use_container_width=True)


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
st.plotly_chart(fig_b, use_container_width=True)


#pregunta 3
st.markdown("""
        <h1 style='text-align: center; color: #444444; font-size: 18px; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;'>
        Distribución de Precipitaciones en Cultivos de Alto Rendimiento
        </h1>
        """, unsafe_allow_html=True)
alto_rendimiento = df_estudio[df_estudio['rendimiento'] >= df_estudio['rendimiento'].quantile(0.75)]
lluvia_ideal = alto_rendimiento.groupby('temporada')['precipitacion_anual'].median()
fig_c = px.histogram(alto_rendimiento, x='precipitacion_anual', color='temporada', barmode='overlay')
fig_c.update_layout(
    margin=dict(l=20, r=20, t=50, b=20),
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(0,0,0,0)",
    autosize=True)
st.plotly_chart(fig_c, use_container_width=True)


#pregunta 4
st.markdown("""
        <h1 style='text-align: center; color: #444444; font-size: 18px; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;'>
        Correlación entre Precipitaciones y Agroquímicos
        </h1>
        """, unsafe_allow_html=True)
vars_d = df_estudio[['precipitacion_anual', 'fertilizante', 'pesticida']]
matriz_corr = vars_d.corr()
fig_d = px.imshow(matriz_corr, text_auto=True, aspect="auto", color_continuous_scale='Blues')
st.plotly_chart(fig_d, use_container_width=True)



#objetivo 1
st.markdown("""
        <h1 style='text-align: center; color: #444444; font-size: 18px; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;'>
        Variabilidad Pluviométrica por Temporada
        </h1>
        """, unsafe_allow_html=True)
variabilidad_lluvia = df_estudio.groupby('temporada')['precipitacion_anual'].agg([
    ('media', 'mean'), 
    ('Desviacion', 'std'), 
    ('min', 'min'), 
    ('max', 'max')])
fig_obj1 = px.box(df_estudio, x="temporada", y="precipitacion_anual",
                  labels={"precipitacion_anual": "Precipitación Anual (mm)", "temporada": "Temporada"},
                  color="temporada")
st.plotly_chart(fig_obj1, use_container_width=True)


#objetivo 2
st.markdown("""
        <h1 style='text-align: center; color: #444444; font-size: 18px; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;'>
        Distribución Promedio de Factores por Temporada
        </h1>
        """, unsafe_allow_html=True)



#objetivo 3
st.markdown("""
        <h1 style='text-align: center; color: #444444; font-size: 18px; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;'>
        Demanda Total de Agroquímicos por Temporada
        </h1>
        """, unsafe_allow_html=True)
demanda_total = df_estudio.groupby('temporada')[['fertilizante', 'pesticida']].sum().reset_index()
fig_obj3 = px.bar(demanda_total, 
                  x='temporada', 
                  y=['fertilizante', 'pesticida'],
                  labels={'value':'Cantidad Total (Kg)', 'variable':'Tipo de Agroquímico', 'season':'Temporada'})
st.plotly_chart(fig_obj3, use_container_width=True)



