import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página de Streamlit
st.set_page_config(page_title="Gemelo Digital: Aula Inteligente", layout="wide")

st.title("🏫 Prototipo de Gemelo Digital: Temperatura del Aula")
st.markdown("""
Simula el comportamiento térmico de un aula en tiempo real. 
Modifica los parámetros en la barra lateral para ver cómo influyen los alumnos y el aire acondicionado.
""")

# --- BARRA LATERAL: Parámetros del Entorno ---
st.sidebar.header("🎛️ Parámetros de Control")

# Variables del Aula
temp_inicial = st.sidebar.slider("Temperatura inicial del aula (°C)", 15.0, 40.0, 28.0, 0.5)
temp_exterior = st.sidebar.slider("Temperatura exterior (°C)", 10.0, 45.0, 32.0, 0.5)
num_alumnos = st.sidebar.slider("Número de alumnos", 0, 40, 25, 1)

# Variables del Aire Acondicionado
aire_encendido = st.sidebar.toggle("Encender Aire Acondicionado", value=True)
temp_objetivo = st.sidebar.slider("Temperatura del Aire (°C)", 16.0, 26.0, 22.0, 1.0)
potencia_ac = st.sidebar.slider("Potencia del AC (Frigorías/BTU aprox)", 2000, 6000, 3500, 500)

# --- MODELO MATEMÁTICO (Simulación) ---
# Constantes físicas aproximadas para el aula
minutos = 60
dt = 1 # intervalos de 1 minuto
calor_por_alumno = 0.05 # Elevación de temperatura estimada por alumno por hora (°C/min total ponderado)
aislamiento = 0.03 # Coeficiente de transferencia con el exterior

# Inicializar variables para la simulación
tiempo = np.arange(0, minutos + 1, dt)
temperaturas = [temp_inicial]

current_temp = temp_inicial

for t in tiempo[1:]:
    # 1. Efecto del exterior (Conducción térmica)
    cambio_exterior = aislamiento * (temp_exterior - current_temp)
    
    # 2. Efecto de los alumnos (Generación de calor metabólico)
    cambio_alumnos = num_alumnos * (calor_por_alumno / 60)
    
    # 3. Efecto del Aire Acondicionado (si está encendido)
    cambio_ac = 0.0
    if aire_encendido and current_temp > temp_objetivo:
        # El enfriamiento es proporcional a la potencia y a la diferencia de temperatura
        factor_enfriamiento = (potencia_ac / 3500) * 0.15 
        cambio_ac = -factor_enfriamiento * (current_temp - temp_objetivo)
    
    # Calcular nueva temperatura para el siguiente minuto
    current_temp += cambio_exterior + cambio_alumnos + cambio_ac
    # Limitar físicamente la temperatura para que no baje más que la del aire
    if aire_encendido and current_temp < temp_objetivo:
        current_temp = temp_objetivo
        
    temperaturas.append(current_temp)

# --- VISUALIZACIÓN Y MÉTRICAS ---
df_simulacion = pd.DataFrame({"Minuto": tiempo, "Temperatura (°C)": temperaturas})

# KPIs principales en pantalla
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Temperatura Actual", value=f"{temperaturas[-1]:.1f} °C", delta=f"{temperaturas[-1] - temp_inicial:.1f} °C desde el inicio")
with col2:
    estado_ac = "🟢 Encendido" if aire_encendido else "🔴 Apagado"
    st.metric(label="Estado del AC", value=estado_ac)
with col3:
    st.metric(label="Carga Térmica (Alumnos)", value=f"{num_alumnos} personas")

st.markdown("---")

# Gráfica del comportamiento temporal
st.subheader("📈 Evolución de la Temperatura en 60 Minutos")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df_simulacion["Minuto"], df_simulacion["Temperatura (°C)"], label="Temperatura Aula", color="#FF4B4B", linewidth=2.5)
ax.axhline(y=temp_exterior, color="orange", linestyle="--", label="Temp. Exterior")
if aire_encendido:
    ax.axhline(y=temp_objetivo, color="green", linestyle="--", label="Set Point AC")

ax.set_xlabel("Tiempo (Minutos)")
ax.set_ylabel("Temperatura (°C)")
ax.set_ylim(15, 45)
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend()

st.pyplot(fig)

# Tabla de datos (opcional para el usuario)
with st.expander("📊 Ver tabla de datos simulados"):
    st.dataframe(df_simulacion.style.format({"Temperatura (°C)": "{:.2f}"}))
