import streamlit as st
import pandas as pd

st.set_page_config(page_title="Valorización de Costos Militares", page_icon="🛡️", layout="wide")

st.title("🛡️ Sistema de Valorización de Costos Operativos")
st.markdown("### Módulo: Sistemas Remotamente Tripulados (SRT)")

# --- 1. BASE DE DATOS TÉCNICA (Punto d - Cuotas cada 100km) ---
db_medios = {
    "Ford Ranger": {"cons_100": 12, "mant_km": 150.0}, # Costo de repuesto/mant por km
    "Hummvee": {"cons_100": 28, "mant_km": 450.0},
    "Jeep 230G": {"cons_100": 18, "mant_km": 300.0}
}

# --- 2. ENTRADA DE DATOS (Punto a y b) ---
with st.sidebar:
    st.header("⚙️ Configuración del Módulo")
    
    st.subheader("🚚 Medios de Despliegue")
    vehiculo = st.selectbox("Seleccione Vehículo", list(db_medios.keys()))
    distancia_dr = st.number_input("Distancia Despliegue/Repliegue (km)", value=100)
    
    st.subheader("👥 Personal (Categorías 100%)")
    cant_pax = st.number_input("Cantidad de Personal", value=4)
    viatico_diario = st.number_input("Viático según Escala Vigente ($)", value=25000)
    
    st.subheader("🔋 Insumos y Equipos")
    horas_op = st.number_input("Horas de Operación Diaria (Máx)", value=8)
    precio_comb = st.number_input("Precio Combustible / Litro ($)", value=1100)
    seguro_equipo = st.number_input("Seguro/Amortización Diaria ($)", value=5000)

st.markdown("---")

# --- 3. CÁLCULOS SEGÚN ORDEN (Punto c y d) ---

# A. COSTO DE DESPLIEGUE / REPLIEGUE (Punto c y d)
# Se valoriza en cuotas de combustible cada 100km + mantenimiento proporcional
litros_dr = (distancia_dr / 100) * db_medios[vehiculo]["cons_100"]
costo_comb_dr = litros_dr * precio_comb
mantenimiento_dr = distancia_dr * db_medios[vehiculo]["mant_km"]
total_despliegue = costo_comb_dr + mantenimiento_dr

# B. COSTO OPERATIVO DIARIO (Punto a)
# Incluye personal, combustible de generador, starlink y seguros
viaticos_total = cant_pax * viatico_diario
consumo_gen = horas_op * 1.1 * precio_comb # Dogo 3500
conectividad = 2000 # Starlink prorrateado
total_operativo = viaticos_total + consumo_gen + conectividad + seguro_equipo

# --- 4. PRESENTACIÓN DE RESULTADOS ---
col1, col2 = st.columns(2)

with col1:
    st.error(f"🚚 Costo Despliegue/Repliegue\n\n$ {total_despliegue:,.2f}")
    st.caption(f"Incluye {litros_dr:.1f} lts de combustible y mantenimiento programado por {distancia_dr} km.")

with col2:
    st.success(f"⏱️ Costo Día Operativo\n\n$ {total_operativo:,.2f}")
    st.caption(f"Incluye viáticos al 100%, operación de {horas_op}hs y seguros.")

st.markdown("---")

# TABLA DETALLADA PARA RENDICIÓN
st.subheader("📋 Detalle de Valorización")
detalle = pd.DataFrame({
    "Concepto": ["Combustible (Movilidad)", "Mantenimiento/Repuestos", "Viáticos Personal", "Insumos Energía", "Seguros/Custodia", "Conectividad Satelital"],
    "Despliegue/Repliegue": [costo_comb_dr, mantenimiento_dr, 0, 0, 0, 0],
    "Día Operativo": [0, 0, viaticos_total, consumo_gen, seguro_equipo, conectividad]
})
st.table(detalle)

# Total Final
st.info(f"**VALOR TOTAL DEL MÓDULO (1er Día): $ {(total_despliegue + total_operativo):,.2f}**")

# Botón de Descarga
csv = detalle.to_csv(index=False).encode('utf-8')
st.download_button("📥 Exportar Valorización (CSV)", csv, "valorizacion_srt.csv", "text/csv")
