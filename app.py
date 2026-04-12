import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

df = pd.read_csv("./27. Agricultura.csv")

# Normalizar nombres de columnas
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Eliminar duplicados
df = df.drop_duplicates()

# Convertir tipos según tus columnas
for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].str.strip()

df = df.infer_objects()

# Eliminar filas con valores faltantes en columnas críticas
# Cambia ["columna_critica1", "columna_critica2"] por tus columnas importantes
# df = df.dropna(subset=["columna_critica1", "columna_critica2"])

q1_production = df["production"].quantile(0.25)
q3_production = df["production"].quantile(0.75)
iqr_production = q3_production - q1_production
lower_bound_production = q1_production - 1.5 * iqr_production
upper_bound_production = q3_production + 1.5 * iqr_production
df = df.query("production >= @lower_bound_production and production <= @upper_bound_production")

q1_fertilizer = df["fertilizer"].quantile(0.25)
q3_fertilizer = df["fertilizer"].quantile(0.75)
iqr_fertilizer = q3_fertilizer - q1_fertilizer
lower_bound_fertilizer = q1_fertilizer - 1.5 * iqr_fertilizer
upper_bound_fertilizer = q3_fertilizer + 1.5 * iqr_fertilizer
df = df.query("fertilizer >= @lower_bound_fertilizer and fertilizer <= @upper_bound_fertilizer")

q1_area = df["area"].quantile(0.25)
q3_area = df["area"].quantile(0.75)
iqr_area = q3_area - q1_area
lower_bound_area = q1_area - 1.5 * iqr_area
upper_bound_area = q3_area + 1.5 * iqr_area
df = df.query("area >= @lower_bound_area and area <= @upper_bound_area")
 
df = df.query("crop_year >= 2010 and crop_year <= 2020")

df = df[df['season'] != 'Whole Year']
df['season'] = df['season'].replace('Summer', 'Zaid')
df['season'] = df['season'].replace('Winter', 'Rabi')
df['season'] = df['season'].replace('Autumn', 'Kharif')
"Info después de filtrar por temporada:"
st.write(df.describe())

# Gráfico de torta: Frecuencia de cultivos por temporada
st.subheader("Frecuencia de los Cultivos por Temporada")
freq_by_season_crop = df.groupby(['season', 'crop']).size().reset_index(name='count')
# Usar solo los cultivos más frecuentes para no saturar el gráfico
top_crops = (freq_by_season_crop.groupby('crop')['count']
             .sum()
             .nlargest(10)
             .index)
freq_top = freq_by_season_crop[freq_by_season_crop['crop'].isin(top_crops)]
fig2 = px.pie(freq_top, values='count', names='crop',
              title='Frecuencia de los cultivos más comunes')
st.plotly_chart(fig2)

# Gráfico de torta: Fertilizante por temporada de cultivo
st.subheader("Gráfico de Torta: Fertilizante por Temporada de Cultivo")
fertilizer_by_season = df.groupby('season')['fertilizer'].mean().reset_index()
fig3 = px.pie(fertilizer_by_season, values='fertilizer', names='season',
              title='Promedio de Fertilizante por Temporada')
st.plotly_chart(fig3)

# Gráfico de torta: Pesticida por temporada de cultivo
st.subheader("Gráfico de Torta: Pesticida por Temporada de Cultivo")
pesticide_by_season = df.groupby('season')['pesticide'].mean().reset_index()
fig4 = px.pie(pesticide_by_season, values='pesticide', names='season',
              title='Promedio de Pesticida por Temporada')
st.plotly_chart(fig4)

# Gráfico de torta: Rendimiento por temporada
st.subheader("Gráfico de Torta: Rendimiento por Temporada")
yield_by_season = df.groupby('season')['yield'].mean().reset_index()
colores = ["#9378E7", "#52A1F7", '#00CC96', "#FD78B0"] 
fig5 = px.pie(yield_by_season, values='yield', names='season', title='Rendimiento Promedio por Temporada', color_discrete_sequence=colores) 
st.plotly_chart(fig5)

# Scatter plots: Fertilizante vs Rendimiento por Temporada
st.subheader("Scatter Plot: Fertilizante vs Rendimiento por Temporada")
fig6 = px.scatter(df, x='fertilizer', y='yield', color='season',
                  title='Relación entre Fertilizante y Rendimiento por Temporada',
                  labels={'fertilizer': 'Fertilizante', 'yield': 'Rendimiento', 'season': 'Temporada'})
st.plotly_chart(fig6)

# Scatter plots: Pesticida vs Rendimiento por Temporada
st.subheader("Scatter Plot: Pesticida vs Rendimiento por Temporada")
fig7 = px.scatter(df, x='pesticide', y='yield', color='season',
                  title='Relación entre Pesticida y Rendimiento por Temporada',
                  labels={'pesticide': 'Pesticida', 'yield': 'Rendimiento', 'season': 'Temporada'})
st.plotly_chart(fig7)

# Gráfico de campana de Gauss: Precipitación por temporada y por años
st.subheader("Gráfico de Campana de Gauss: Precipitación por Temporada y por Años")
# Calcular precipitación promedio por año y temporada
rain_by_year_season = df.groupby(['crop_year', 'season'])['annual_rainfall'].mean().reset_index()
fig8 = px.line(rain_by_year_season, x='crop_year', y='annual_rainfall', color='season',
              title='Precipitación Promedio por Temporada a lo Largo de los Años',
              labels={'crop_year': 'Año', 'annual_rainfall': 'Precipitación Anual Promedio (mm)'})
st.plotly_chart(fig8)

# Scatter plot: Fertilizante vs Precipitación por Temporada
st.subheader("Scatter Plot: Fertilizante vs Precipitación por Temporada")
fig9 = px.scatter(df, x='annual_rainfall', y='fertilizer', color='season',
                   title='Relación Fertilizantes vs. Precipitación',
                   labels={'annual_rainfall': 'Precipitación Anual (mm)', 'fertilizer': 'Fertilizante'})
st.plotly_chart(fig9)

# Diagrama de dispersión: Precipitación vs Rendimiento por temporada
st.subheader("Diagrama de Dispersión: Precipitación vs Rendimiento por Temporada")
fig10 = px.scatter(df, x='annual_rainfall', y='yield', color='season',
                   title='Relación entre Precipitación y Rendimiento por Temporada',
                   labels={'annual_rainfall': 'Precipitación Anual (mm)', 'yield': 'Rendimiento', 'season': 'Temporada'})
st.plotly_chart(fig10)



