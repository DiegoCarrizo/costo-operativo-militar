import streamlit as st
import pandas as pd

# CONFIGURACIÓN PROFESIONAL
st.set_page_config(page_title="MIL-OPS: Valorización SRT", page_icon="🪖", layout="wide")

st.title("🪖 Sistema de Valorización de Costos Operativos (SRT)")
st.info("Cómputo basado en Orden de Valorización de Medios y Personal (Escala 2024-2025)")

# --- DATOS EXTRAÍDOS DE TUS ADJUNTOS ---
# Combustible (según Calculos Logisticos Sep24)
PRECIO_NAFTA = 1114.0
PRECIO_GASOIL = 1414.0

# Vehículos: Consumo c/100 km (según archivos adjuntos)
db_vehiculos = {
    "Ford Ranger (Gasoil)": {"cons_100": 11.0, "tipo": "Gasoil", "mant_km": 150},
    "Hummvee / Hummer (Gasoil)": {"cons_100": 30.0, "tipo": "Gasoil", "mant_km": 450},
    "Jeep MB 230G (Nafta)": {"cons_100": 25.0, "tipo": "Nafta", "mant_km": 300},
    "Unimog (Gasoil)": {"cons_100": 20.0, "tipo": "Gasoil", "mant_km": 400},
    "Atego 1726 (Gasoil)": {"cons_100": 50.0, "tipo": "Gasoil", "mant_km": 600}
}

# Viáticos al 100% (según costo dia operativo dron.xlsx)
db_viaticos = {
    "JEMGE": 114644.60,
    "Oficial Superior": 94581.80,
    "Oficial Jefe": 74518.99,
    "Oficial Subalterno": 63054.53,
    "Suboficial Superior": 57322.30,
    "Suboficial Subalterno": 51590.07,
    "Cadete": 37259.50,
    "Soldado Voluntario / Aspirante": 34393.38
}

# Drones e Insumos (según costo dia operativo dron.xlsx)
db_drones = {
    "Mavic II Enterprise": 3000000,
    "Mavic IV": 6603000,
    "Phantom 4 Pro": 1200000,
    "Phantom 4 RTK": 7500000,
    "Matrice 200": 5425000
}

# --- INTERFAZ DE USUARIO ---
with st.sidebar:
    st.header("⚙️ Parámetros de Operación")
    
    st.subheader("🚚 Movilidad (Punto 1.d)")
    vehiculo_sel = st.selectbox("Vehículo de la Unidad", list(db_vehiculos.keys()))
    km_despliegue = st.number_input("Distancia Despliegue/Repliegue (km)", value=100)
    
    st.subheader("👥 Personal (Punto 1.b)")
    # Cuatro personas fijas según requerimiento
    p1 = st.selectbox("Conductor", list(db_viaticos.keys()), index=5)
    p2 = st.selectbox("Operador Dron 1", list(db_viaticos.keys()), index=3)
    p3 = st.selectbox("Operador Dron 2", list(db_viaticos.keys()), index=4)
    p4 = st.selectbox("Auxiliar", list(db_viaticos.keys()), index=7)
    
    st.subheader("⚡ Equipos e Insumos (Punto 1.a)")
    dron_sel = st.selectbox("Modelo de Dron", list(db_drones.keys()))
    horas_gen = st.slider("Horas Generador (Dogo 3500)", 0, 24, 8)
    starlink_posesion = st.checkbox("Posee antena Starlink", value=True)

# --- LÓGICA DE CÁLCULO (CUMPLIENDO LA ORDEN) ---

# 1. Costo Despliegue/Repliegue (Cuotas de combustible c/100km + Mantenimiento)
v_data = db_vehiculos[vehiculo_sel]
precio_v = PRECIO_GASOIL if v_data["tipo"] == "Gasoil" else PRECIO_NAFTA
comb_dr = (km_despliegue / 100) * v_data["cons_100"] * precio_v
mant_dr = km_despliegue * v_data["mant_km"]
costo_despliegue_total = comb_dr + mant_dr

# 2. Costo Operativo Diario (Personal 100% + Insumos + Seguros)
viaticos_total = db_viaticos[p1] + db_viaticos[p2] + db_viaticos[p3] + db_viaticos[p4]
# Generador Dogo 3500 (15L / 10hs = 1.5 L/h)
comb_gen = horas_gen * 1.5 * PRECIO_GASOIL 
# Starlink itinerante (87.500 / 30 días)
costo_starlink = 87500 / 30
# Amortización/Seguro (Prorrateo 0.1% valor equipo)
amortizacion = db_drones[dron_sel] * 0.001 

costo_operativo_total = viaticos_total + comb_gen + costo_starlink + amortizacion

# --- VISUALIZACIÓN ---
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.error(f"📦 COSTO DESPLIEGUE/REPLIEGUE\n\n$ {costo_despliegue_total:,.2f}")
    st.caption(f"Valorizado en Cuotas de Combustible cada {km_despliegue}km + Mantenimiento Prorrateado.")

with c2:
    st.success(f"⏱️ COSTO DÍA OPERATIVO\n\n$ {costo_operativo_total:,.2f}")
    st.caption(f"Incluye Viáticos (4 PAX al 100%), Insumos, Energía y Conectividad.")

st.markdown("---")
st.subheader("📋 Detalle de Gastos por Módulo")

# Tabla de desglose
resumen_data = {
    "Categoría": ["Combustible Vehículo", "Mantenimiento Programado", "Viáticos Personal (100%)", "Combustible Generador", "Conectividad Satelital", "Seguro/Amortización Equipo"],
    "Despliegue/Repliegue ($)": [comb_dr, mant_dr, 0, 0, 0, 0],
    "Día Operativo ($)": [0, 0, viaticos_total, comb_gen, costo_starlink, amortizacion]
}
df_resumen = pd.DataFrame(resumen_data)
st.table(df_resumen)

# TOTAL FINAL MISION
st.divider()
total_mision = costo_despliegue_total + costo_operativo_total
st.header(f"TOTAL VALORIZADO PRIMER DÍA: $ {total_mision:,.2f}")

# Botón de Descarga
csv = df_resumen.to_csv(index=False).encode('utf-8')
st.download_button("📥 Exportar Planilla de Valorización", csv, "valorizacion_mision.csv", "text/csv")
