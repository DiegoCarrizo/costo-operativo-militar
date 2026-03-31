import streamlit as st
import pandas as pd
from docx import Document
from io import BytesIO

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Valorización Día Operativo - Oficial", page_icon="🛡️", layout="wide")

st.title("🛡️ Sistema de Valorización de Costos Operativos (SRT)")
st.info("Cómputo basado en Orden de Valorización de Medios y Personal - Datos Oficiales")

# --- BASE DE DATOS TÉCNICA (Basada en tus archivos) ---
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

db_drones_usd = {
    "Mavic II Enterprise": 3150.0, "Mavic IV": 6950.0,
    "Phantom 4 Pro": 1260.0, "Phantom 4 RTK": 7890.0, "Matrice 200": 5700.0
}

# --- BARRA LATERAL (CONFIGURACIONES) ---
with st.sidebar:
    st.header("📊 Mercado y Divisas")
    tc_bna = st.number_input("Tipo de Cambio BNA (Vendedor)", min_value=1.0, value=950.0)
    
    st.header("⛽ Combustible (Manual)")
    p_nafta = st.number_input("Precio Litro Nafta ($)", min_value=0.0, value=1114.0)
    p_gasoil = st.number_input("Precio Litro Gasoil ($)", min_value=0.0, value=1414.0)

    st.divider()
    st.header("📡 Conectividad (Starlink)")
    quiere_antena = st.checkbox("Sumar Adquisición de Antena ($300.000)", value=False)
    quiere_internet = st.checkbox("Sumar Servicio Internet Mensual ($87.500)", value=False)
    
    costo_antena_fijo = 300000.0
    abono_mensual_fijo = 87500.0 
    
    st.divider()
    st.header("⚙️ Configuración Misión")
    vehiculo_sel = st.selectbox("Vehículo 4x4", list(db_vehiculos.keys()))
    km_despliegue = st.number_input("Distancia Despliegue (km)", value=100)
    
    st.subheader("👥 Personal")
    p1 = st.selectbox("Conductor", list(db_viaticos.keys()), index=5)
    p2 = st.selectbox("Operador 1", list(db_viaticos.keys()), index=3)
    p3 = st.selectbox("Operador 2", list(db_viaticos.keys()), index=4)
    p4 = st.selectbox("Auxiliar", list(db_viaticos.keys()), index=7)
    
    dron_sel = st.selectbox("Modelo de Dron (USD)", list(db_drones_usd.keys()))
    horas_gen = st.slider("Horas Generador", 0, 24, 8)

# --- LÓGICA DE CÁLCULO ---
v_data = db_vehiculos[vehiculo_sel]
p_uso = p_gasoil if "Gasoil" in vehiculo_sel else p_nafta
costo_comb_dr = (km_despliegue / 100) * v_data["cons_100"] * p_uso
costo_mant_dr = km_despliegue * v_data["mant_km"]
total_logistica = costo_comb_dr + costo_mant_dr

viaticos_ars = db_viaticos[p1] + db_viaticos[p2] + db_viaticos[p3] + db_viaticos[p4]
comb_gen_ars = horas_gen * 1.5 * p_gasoil

gasto_antena = costo_antena_fijo if quiere_antena else 0.0
gasto_internet = abono_mensual_fijo if quiere_internet else 0.0

# Cálculo específico del equipo en ambas monedas
valor_usd = db_drones_usd[dron_sel]
valor_pesos_bna = valor_usd * tc_bna
amortizacion_ars = valor_pesos_bna * 0.001

total_mision = total_logistica + viaticos_ars + comb_gen_ars + gasto_antena + gasto_internet + amortizacion_ars

# --- INTERFAZ DE RESULTADOS ---
st.markdown(f"### 💹 Cotización Aplicada: **$ {tc_bna:,.2f}** (Dólar BNA Vendedor)")

col_a, col_b, col_c = st.columns(3)
col_a.metric("LOGÍSTICA Y PERSONAL", f"$ {(total_logistica + viaticos_ars):,.2f}")
col_b.metric("TOTAL CONECTIVIDAD", f"$ {(gasto_antena + gasto_internet):,.2f}")
# Punto solicitado: Muestra USD y abajo el equivalente en ARS (delta)
col_c.metric(
    label=f"EQUIPO SRT: {dron_sel}", 
    value=f"u$s {valor_usd:,.2f}", 
    delta=f"Equiv. ARS {valor_pesos_bna:,.2f}",
    delta_color="normal"
)

st.divider()

# TABLA DE DETALLE
resumen_data = [
    ["Combustible y Mantenimiento", "ARS", f"$ {total_logistica:,.2f}", total_logistica],
    ["Viáticos Personal (100%)", "ARS", f"$ {viaticos_ars:,.2f}", viaticos_ars],
    ["Energía (Generador)", "ARS", f"$ {comb_gen_ars:,.2f}", comb_gen_ars],
    ["Amortización Diaria SRT (0.1%)", "ARS", f"$ {amortizacion_ars:,.2f}", amortizacion_ars]
]

if quiere_antena:
    resumen_data.append(["Adquisición Antena Starlink (Hardware)", "ARS", f"$ {costo_antena_fijo:,.2f}", costo_antena_fijo])
if quiere_internet:
    resumen_data.append(["Servicio Starlink (Abono Mensual)", "ARS", f"$ {abono_mensual_fijo:,.2f}", abono_mensual_fijo])

df_resumen = pd.DataFrame(resumen_data, columns=["Rubro", "Origen", "Detalle de Costo", "Subtotal ARS"])
st.subheader("📋 Detalle de Valorización Consolidado")
st.table(df_resumen.drop(columns=["Subtotal ARS"]))

st.header(f"TOTAL FINAL A LIQUIDAR: $ {total_mision:,.2f}")

# --- FUNCIÓN GENERAR WORD ---
def generate_docx(df, total_final):
    doc = Document()
    doc.add_heading('VALORIZACIÓN DE COSTOS OPERATIVOS SRT', 0)
    doc.add_paragraph(f"Vehículo: {vehiculo_sel} | Dron: {dron_sel}")
    doc.add_paragraph(f"Tipo de Cambio: $ {tc_bna} (BNA Vendedor)")

    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Rubro'
    hdr_cells[1].text = 'Origen'
    hdr_cells[2].text = 'Costo Consolidado (ARS)'

    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        row_cells[0].text = str(row['Rubro'])
        row_cells[1].text = str(row['Origen'])
        row_cells[2].text = f"$ {row['Subtotal ARS']:,.2f}"

    doc.add_paragraph(f"\nTOTAL FINAL: $ {total_final:,.2f}").bold = True
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# BOTÓN DESCARGA
st.divider()
doc_buffer = generate_docx(df_resumen, total_mision)
st.download_button(
    label="📥 Descargar Planilla en WORD (Editable)",
    data=doc_buffer,
    file_name="valorizacion_srt_oficial.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
