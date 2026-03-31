import streamlit as st
import pandas as pd

st.set_page_config(page_title="MIL-OPS Cost", page_icon="🪖")

st.title("🪖 Monitor de Costo Operativo Diario")
st.markdown("---")

# 1. ENTRADA DE DATOS
with st.sidebar:
    st.header("Configuración de Unidad")
    
    # Vehículo
    vehiculo = st.selectbox("Vehículo 4x4", ["Ford Ranger", "Hummvee", "Jeep 230G", "Otro"])
    km_dia = st.number_input("Kilómetros a recorrer hoy", min_value=0, value=100)
    precio_litro = st.number_input("Precio Litro Combustible ($)", min_value=0, value=1100)
    
    # Personal (Fijo 4 personas)
    st.markdown("---")
    viatico_pax = st.number_input("Viático por Persona ($/día)", min_value=0, value=25000)
    
    # Energía y Antena
    st.markdown("---")
    horas_gen = st.slider("Horas de Generador (Dogo 3500)", 0, 24, 8)
    costo_starlink = st.number_input("Costo Diario Starlink ($)", min_value=0, value=2000)

# 2. LÓGICA DE CÁLCULO
# Consumos estimados lts/100km
consumos = {"Ford Ranger": 12, "Hummvee": 28, "Jeep 230G": 18, "Otro": 15}
gasto_v = (km_dia / 100) * consumos[vehiculo] * precio_litro

# Generador Dogo 3500 consume aprox 1.1 lts/hora
gasto_gen = horas_gen * 1.1 * precio_litro

# Personal (4 personas)
gasto_pers = viatico_pax * 4

total = gasto_v + gasto_gen + gasto_pers + costo_starlink

# 3. RESULTADOS
c1, c2 = st.columns(2)
with c1:
    st.metric("COSTO TOTAL DÍA", f"$ {total:,.2f}")
    st.metric("Gasto Combustible", f"$ {(gasto_v + gasto_gen):,.2f}")

with c2:
    st.write("### Desglose:")
    tabla = pd.DataFrame({
        "Concepto": ["Vehículo", "Generador", "Personal (4)", "Starlink"],
        "Costo": [gasto_v, gasto_gen, gasto_pers, costo_starlink]
    })
    st.table(tabla)

# Botón de Descarga
csv = tabla.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descargar Planilla", csv, "costo_mision.csv", "text/csv")
