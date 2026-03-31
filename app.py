import streamlit as st
import pandas as pd

# CONFIGURACIÓN
st.set_page_config(page_title="Valorización SRT - Oficial", page_icon="🪖", layout="wide")

st.title("Valorización de Costos Operativos")
st.caption("Orden de Valorización - Valores en ARS y USD (BNA)")

# --- DATOS TÉCNICOS INTEGRADOS---
db_vehiculos = {
    "Ford Ranger (Gasoil)": {"cons_100": 11.0, "mant_km": 150},
    "Hummvee / Hummer (Gasoil)": {"cons_100": 30.0, "mant_km": 450},
    "Jeep MB 230G (Nafta)": {"cons_100": 25.0, "mant_km": 300},
    "Unimog (Gasoil)": {"cons_100": 20.0, "mant_km": 400}
}

db_viaticos = {
    "JEMGE": 114644.60, "Oficial Superior": 94581.80,
    "Oficial Jefe": 74518.99, "Oficial Subalterno": 63054.53,
    "Suboficial Superior": 57322.30, "Suboficial Subalterno": 51590.07,
    "Cadete": 37259.50, "Soldado Voluntario / Aspirante": 34393.38
}

# Precios de Drones en USD
db_drones_usd = {
    "Mavic II Enterprise": 2800.0,
    "Mavic IV": 5500.0,
    "Phantom 4 Pro": 1100.0,
    "Phantom 4 RTK": 6800.0,
    "Matrice 200": 4800.0
}

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Variables de Mercado")
    tipo_cambio_bna = st.number_input("Tipo de Cambio BNA (Vendedor)", min_value=1.0, value=950.0, step=0.5)
    
    st.subheader("Combustible (Carga Manual)")
    precio_nafta = st.number_input("Precio Nafta ($)", min_value=0.0, value=1114.0)
    precio_gasoil = st.number_input("Precio Gasoil ($)", min_value=0.0, value=1414.0)

    st.divider()
    st.header("⚙️ Configuración Misión")
    vehiculo_sel = st.selectbox("Vehículo", list(db_vehiculos.keys()))
    km_despliegue = st.number_input("Distancia Despliegue/Repliegue (km)", value=100)
    
    st.subheader("Personal (100% Viático)")
    p1 = st.selectbox("Conductor", list(db_viaticos.keys()), index=5)
    p2 = st.selectbox("Operador 1", list(db_viaticos.keys()), index=3)
    p3 = st.selectbox("Operador 2", list(db_viaticos.keys()), index=4)
    p4 = st.selectbox("Auxiliar", list(db_viaticos.keys()), index=7)
    
    st.subheader("Equipo SRT")
    dron_sel = st.selectbox("Modelo de Dron", list(db_drones_usd.keys()))
    horas_op = st.slider("Horas Operación (Dogo 3500)", 0, 24, 8)

# --- LÓGICA DE CÁLCULO ---

# 1. Costo Despliegue/Repliegue (Pesos)
v_data = db_vehiculos[vehiculo_sel]
p_comb = precio_gasoil if "Gasoil" in vehiculo_sel else precio_nafta
comb_dr = (km_despliegue / 100) * v_data["cons_100"] * p_comb
mant_dr = km_despliegue * v_data["mant_km"]
total_dr_ars = comb_dr + mant_dr

# 2. Costo Operativo Diario (Pesos y Dólares)
# Viáticos en Pesos
viaticos_ars = db_viaticos[p1] + db_viaticos[p2] + db_viaticos[p3] + db_viaticos[p4]
# Energía y Starlink (Pesos)
comb_gen_ars = horas_op * 1.5 * precio_gasoil
conectividad_ars = 87500 / 30

# 3. Equipamiento (Dólares a Pesos BNA)
valor_dron_usd = db_drones_usd[dron_sel]
valor_dron_ars = valor_dron_usd * tipo_cambio_bna
# Amortización diaria (0.1% del valor del equipo en Pesos)
amortizacion_ars = valor_dron_ars * 0.001

total_op_ars = viaticos_ars + comb_gen_ars + conectividad_ars + amortizacion_ars

# --- PRESENTACIÓN DE RESULTADOS ---
st.markdown(f"### Tipo de Cambio Aplicado: $ {tipo_cambio_bna} (BNA Vendedor)")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("COSTO DESPLIEGUE (ARS)", f"$ {total_dr_ars:,.2f}")
with c2:
    st.metric("COSTO DÍA OPERATIVO (ARS)", f"$ {total_op_ars:,.2f}")
with c3:
    st.metric(f"VALOR EQUIPO ({dron_sel})", f"USD {valor_dron_usd:,.2f}", delta=f"ARS {valor_dron_ars:,.2f}")

st.divider()
st.subheader("Planilla de Valorización Detallada")

resumen = pd.DataFrame({
    "Concepto": ["Movilidad (Combustible)", "Mantenimiento Programado", "Viáticos Personal (100%)", "Energía (Generador)", "Conectividad", "Amortización Equipo SRT"],
    "Moneda Origen": ["ARS", "ARS", "ARS", "ARS", "ARS", "USD"],
    "Valor Origen": [f"$ {comb_dr:,.2f}", f"$ {mant_dr:,.2f}", f"$ {viaticos_ars:,.2f}", f"$ {comb_gen_ars:,.2f}", f"$ {conectividad_ars:,.2f}", f"USD {valor_dron_usd:,.2f}"],
    "Subtotal en Pesos ($)": [comb_dr, mant_dr, viaticos_ars, comb_gen_ars, conectividad_ars, amortizacion_ars]
})

st.table(resumen)

# TOTAL FINAL
total_mision_ars = total_dr_ars + total_op_ars
st.sidebar.success(f"TOTAL MISION: $ {total_mision_ars:,.2f}")

# Botón descarga
csv = resumen.to_csv(index=False).encode('utf-8')
st.download_button("Descargar Valorización Oficial", csv, "valorizacion_srt_oficial.csv", "text/csv")
