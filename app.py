import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA (Emoji cambiado para evitar errores de codificación)
st.set_page_config(
    page_title="Valorización Día Operativo - Oficial",
    page_icon="🛡️",
    layout="wide"
)

# 2. TÍTULOS E INFORMACIÓN
st.title("🛡️ Sistema de Valorización de Costos Operativos (SRT)")
st.info("Cómputo basado en Orden de Valorización de Medios y Personal - Datos Oficiales")

# --- BASE DE DATOS TÉCNICA (Datos de tus archivos Excel) ---
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

# Precios en USD (Internacional)
db_drones_usd = {
    "Mavic II Enterprise": 3150.0,
    "Mavic IV": 6950.0,
    "Phantom 4 Pro": 1260.0,
    "Phantom 4 RTK": 7890.0,
    "Matrice 200": 5700.0
}

# --- 3. BARRA LATERAL: CARGA MANUAL ---
with st.sidebar:
    st.header("📊 Mercado y Divisas")
    tc_bna = st.number_input("Tipo de Cambio BNA (Vendedor)", min_value=1.0, value=950.0)
    
    st.header("⛽ Combustible (Manual)")
    p_nafta = st.number_input("Precio Litro Nafta ($)", min_value=0.0, value=1114.0)
    p_gasoil = st.number_input("Precio Litro Gasoil ($)", min_value=0.0, value=1414.0)

    st.divider()
    st.header("⚙️ Configuración Misión")
    vehiculo_sel = st.selectbox("Vehículo 4x4", list(db_vehiculos.keys()))
    km_despliegue = st.number_input("Distancia Despliegue/Repliegue (km)", value=100)
    
    st.subheader("👥 Personal (4 integrantes)")
    p1 = st.selectbox("Conductor", list(db_viaticos.keys()), index=5)
    p2 = st.selectbox("Operador 1", list(db_viaticos.keys()), index=3)
    p3 = st.selectbox("Operador 2", list(db_viaticos.keys()), index=4)
    p4 = st.selectbox("Auxiliar", list(db_viaticos.keys()), index=7)
    
    st.subheader("🚁 Equipo SRT")
    dron_sel = st.selectbox("Modelo de Dron (USD)", list(db_drones_usd.keys()))
    horas_gen = st.slider("Horas Generador (Dogo 3500)", 0, 24, 8)

# --- 4. LÓGICA DE CÁLCULO ---

# Costo Despliegue (ARS)
v_data = db_vehiculos[vehiculo_sel]
p_uso = p_gasoil if "Gasoil" in vehiculo_sel else p_nafta
costo_comb_dr = (km_despliegue / 100) * v_data["cons_100"] * p_uso
costo_mant_dr = km_despliegue * v_data["mant_km"]
total_dr_ars = costo_comb_dr + costo_mant_dr

# Día Operativo (ARS + USD converted to ARS BNA)
viaticos_ars = db_viaticos[p1] + db_viaticos[p2] + db_viaticos[p3] + db_viaticos[p4]
comb_gen_ars = horas_gen * 1.5 * p_gasoil
conectividad_ars = 87500 / 30

# Conversión del Dron (Dólar BNA Vendedor)
valor_usd = db_drones_usd[dron_sel]
valor_ars_bna = valor_usd * tc_bna
amortizacion_ars = valor_ars_bna * 0.001 # 0.1% amortización diaria

total_op_ars = viaticos_ars + comb_gen_ars + conectividad_ars + amortizacion_ars

# --- 5. INTERFAZ DE RESULTADOS ---
st.markdown(f"### 💹 Cotización Aplicada: **$ {tc_bna:,.2f}** (Dólar BNA Vendedor)")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("DESPLIEGUE/REPLIEGUE", f"ARS {total_dr_ars:,.2f}")
with c2:
    st.metric("COSTO DÍA OPERATIVO", f"ARS {total_op_ars:,.2f}")
with c3:
    st.metric(f"EQUIPO: {dron_sel}", f"USD {valor_usd:,.2f}", delta=f"ARS {valor_ars_bna:,.2f}")

st.divider()

# TABLA DETALLADA
st.subheader("📋 Detalle de Valorización (Consolidado)")

resumen = pd.DataFrame({
    "Rubro": ["Combustible Movilidad", "Mantenimiento Programado", "Viáticos Personal (100%)", "Energía (Generador)", "Conectividad", "Amortización Equipo SRT"],
    "Moneda Origen": ["ARS", "ARS", "ARS", "ARS", "ARS", "USD"],
    "Costo Origen": [f"$ {costo_comb_dr:,.2f}", f"$ {costo_mant_dr:,.2f}", f"$ {viaticos_ars:,.2f}", f"$ {comb_gen_ars:,.2f}", f"$ {conectividad_ars:,.2f}", f"USD {valor_usd:,.2f}"],
    "Subtotal ARS (BNA)": [costo_comb_dr, costo_mant_dr, viaticos_ars, comb_gen_ars, conectividad_ars, amortizacion_ars]
})

st.table(resumen)

# TOTAL FINAL
total_final_ars = total_dr_ars + total_op_ars
st.sidebar.success(f"TOTAL MISION: $ {total_final_ars:,.2f}")

# BOTÓN DESCARGA (Corregido: Usa CSV y nombre de archivo coherente)
csv = resumen.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar Reporte de Valorización (CSV)",
    data=csv,
    file_name="valorizacion_dia_operativo.csv",
    mime="text/csv"
)
