import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Proyecto Cultivos", 
                   page_icon="", 
                   layout="wide")

st.markdown("<h1>Análisis de los Factores Determinantes en Ciclos Agrícolas</h1>", unsafe_allow_html=True)


@st.cache_data 
def datos_a_trabajar():
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
    'Yield': 'rendimiento'}
    df.rename(columns=columnas_es, inplace=True)

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df = df.drop_duplicates()
    
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].str.strip()

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

    # Filtrado por año 2010 al 2020
    df = df.query("año >= 2010 and año <= 2020")

    # Se prescinde de la temporada whole year y se renombran las demas temporadas
    df = df[df['temporada'] != 'Whole Year']
    df['temporada'] = df['temporada'].replace({'Summer': 'Zaid', 'Winter': 'Rabi', 'Autumn': 'Kharif'})


    return df

df_estudio = datos_a_trabajar()

# colores para las temporadas
tonos_verdes = ['#00441b', '#238b45', '#74c476']


with st.sidebar:
    st.header("Controles de Análisis")
    st.write("Filtra los datos para observar el comportamiento específico.")
    
    lista_temporadas = sorted(df_estudio["temporada"].unique()) if not df_estudio.empty else []
    filtro_temporada = st.multiselect("Selecciona la Temporada:", lista_temporadas, 
                                      help="Si dejas este espacio en blanco, se mostrarán los promedios generales.")

# codigo del flitrado
if filtro_temporada:
    df_filtrado = df_estudio[df_estudio["temporada"].isin(filtro_temporada)]
    titulo_vista = f"Datos para la(s) temporada(s): {', '.join(filtro_temporada)}"
else:
    df_filtrado = df_estudio
    titulo_vista = "Promedios Generales"


#linea de opciones de datos
tab_resumen, tab_media, tab_investigacion, tab_datos = st.tabs([
    "Resumen Estadístico",
    "Calculos Estadisticos", 
    "Análisis de Investigación", 
    "Base de Datos Limpia"
])


#promedios generales
with tab_resumen:
    st.subheader(titulo_vista)
    
    if not df_filtrado.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Promedio Precipitación", value=f"{df_filtrado['precipitacion_anual'].mean():.2f} mm")
            st.metric(label="Promedio Área", value=f"{df_filtrado['area'].mean():.2f}")
            
        with col2:
            st.metric(label="Promedio Fertilizante", value=f"{df_filtrado['fertilizante'].mean():.2f} kg")
            st.metric(label="Promedio Pesticida", value=f"{df_filtrado['pesticida'].mean():.2f} kg")
            
        with col3:
            st.metric(label="Promedio Producción", value=f"{df_filtrado['produccion'].mean():.2f}")
            st.metric(label="Promedio Rendimiento", value=f"{df_filtrado['rendimiento'].mean():.2f}")
            
        with col4:
            cultivo_freq = df_filtrado['cultivo'].mode()[0]
            estado_freq = df_filtrado['estado'].mode()[0]
            st.metric(label="Cultivo más frecuente", value=cultivo_freq)
            st.metric(label="Estado más frecuente", value=estado_freq)
            
        st.info("**Interpretación del Resumen:** Estos valores de tendencia central nos permiten establecer una línea base. Al observar los promedios de fertilizantes y precipitaciones, podemos comprender el punto de equilibrio estándar que requieren los cultivos. Variaciones significativas respecto a estos promedios al cambiar de temporada indicarán periodos de mayor o menor exigencia de recursos hidrícos y químicos, respondiendo directamente a la necesidad de optimizar la gestión de inversiones agrícolas.")
    else:
        st.warning("No hay datos disponibles para la selección actual.")

#calculos estaditicos
with tab_media:
    st.subheader("Tabla de Calculos Estadisticos")
    df_final = datos_a_trabajar()
    estadisticas = df_final.describe()
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
    st.dataframe(estadisticas.style.format("{:.2f}"))


# Graficos planteados al informe
with tab_investigacion:
    st.subheader("Respuestas a Preguntas de Investigación")
    
    if not df_filtrado.empty:
        st.markdown("#### 1. ¿De qué manera influyen y por qué son necesarios los agroquímicos?")
        c1, c2, = st.columns(2)
        with c1:
        # G1: Influencia Fertilizante vs Rendimiento
            fig1 = px.scatter(df_estudio, x='fertilizante', y='rendimiento', color='temporada',
                          title="G1: Influencia del Fertilizante en el Rendimiento",
                          color_discrete_sequence=px.colors.qualitative.Dark24)
            st.plotly_chart(fig1, use_container_width=True)
            st.info("**Interpretación G1:** Responde a la Pregunta 1. Se observa una correlación positiva; a mayor uso de fertilizantes, el rendimiento tiende a estabilizarse en niveles altos, lo que confirma su peso como factor determinante.")

        with c2:
        # G2: Rendimiento según Nivel (Categorización por Boxplot)
        # Creamos bins para el nivel de fertilizante
            df_estudio['nivel_fert'] = pd.qcut(df_estudio['fertilizante'], q=3, labels=['Bajo', 'Medio', 'Alto'])
            fig2 = px.box(df_estudio, x='nivel_fert', y='rendimiento', color='nivel_fert',
                     title="G2: Rendimiento según Nivel de Fertilizante",
                     color_discrete_map={'Bajo':'#a5d6a7', 'Medio':'#66bb6a', 'Alto':'#2e7d32'})
            st.plotly_chart(fig2, use_container_width=True)
            st.info("**Interpretación G2:** Responde a la Pregunta 2. El desplazamiento de la mediana hacia arriba en niveles 'Altos' demuestra que los agroquímicos son necesarios para desplazar el umbral de productividad mínima.")
    
        c3, c4 = st.columns(2)
        with c3:
            # G3: Demanda Total de Agroquímicos
            demanda = df_estudio.groupby('temporada')[['fertilizante', 'pesticida']].sum().reset_index()
            fig3 = px.bar(demanda, x='temporada', y=['fertilizante', 'pesticida'], barmode='group',
                     title="G3: Demanda Total de Agroquímicos por Temporada",
                     color_discrete_map={'fertilizante':'#2e7d32', 'pesticida':'#a5d6a7'})
            st.plotly_chart(fig3, use_container_width=True)
            st.info("**Interpretación G3:** Categoriza claramente qué ciclos agrícolas son más intensivos en insumos, guiando la toma de decisiones presupuestarias.")
        
        with c4:
            # G4: Mapa de Calor Correlación
            corr_matrix = df_estudio[['precipitacion_anual', 'fertilizante', 'pesticida', 'rendimiento']].corr().round(3)
            fig4 = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='Greens',
                        title="G4: Correlación entre Precipitación y Agroquímicos")
            st.plotly_chart(fig4, use_container_width=True)
            st.info("**Interpretación G4:** Identifica si existe una dependencia lineal. Un color oscuro entre precipitación y fertilizante sugeriría que el clima condiciona la cantidad de insumos aplicados.")
        st.markdown("---")


        st.markdown("#### 2. Precipitaciones favorables y su efecto en la cantidad de agroquímicos")
        c5, c6 = st.columns(2)
        with c5:
            # G5: Variabilidad Pluviométrica por Temporada
            fig5 = px.box(df_estudio, x='temporada', y='precipitacion_anual', color='temporada',
                     title="G5: Variabilidad Pluviométrica por Temporada",
                     color_discrete_sequence=['#43a047', '#2e7d32', '#1b5e20'])
            st.plotly_chart(fig5, use_container_width=True)
            st.info("**Interpretación G5:** Cumple el Objetivo Específico A. Permite visualizar qué temporada tiene mayor riesgo hídrico (mayor dispersión) para gestionar mejor el riego.")

        with c6:
            # G6: Distribución Precipitaciones (Alto Rendimiento)
            alto_rend = df_estudio[df_estudio['rendimiento'] > df_estudio['rendimiento'].median()]
            fig6 = px.histogram(alto_rend, x='precipitacion_anual', title="G6: Precipitaciones en Cultivos de Alto Rendimiento",
                           nbins=30, color_discrete_sequence=['#1b5e20'])
            st.plotly_chart(fig6, use_container_width=True)
            st.info("**Interpretación G6:** Responde a la Pregunta 3. La mayor concentración de frecuencia indica el rango pluviométrico ideal (mm) donde la tierra alcanza su máximo potencial sin riesgo de inundación o sequía.")
        st.markdown("---")
        

#Dataset limpio
with tab_datos:
    st.subheader("Base de Datos Estructurada (Post-Limpieza)")
    st.write(f"Total de registros actuales: **{len(df_filtrado)}**")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

