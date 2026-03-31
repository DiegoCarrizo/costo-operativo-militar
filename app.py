import streamlit as st
import pandas as pd
from docx import Document
from io import BytesIO

# CONFIGURACIÓN
st.set_page_config(page_title="Valorización Día Operativo - Oficial", page_icon="🛡️", layout="wide")

st.title("🛡️ Sistema de Valorización de Costos Operativos (SRT)")
st.info("Cómputo basado en Orden de Valorización de Medios y Personal - Datos Oficiales")

# --- BASE DE DATOS ---
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

# --- BARRA LATERAL ---
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
    
    dron_sel = st.selectbox("Modelo de Dron (USD)", list(db_drones_usd.keys()))
    horas_gen = st.slider("Horas Generador (Dogo 3500)", 0, 24, 8)

# --- CÁLCULOS ---
v_data = db_vehiculos[vehiculo_sel]
p_uso = p_gasoil if "Gasoil" in vehiculo_sel else p_nafta
costo_comb_dr = (km_despliegue / 100) * v_data["cons_100"] * p_uso
costo_mant_dr = km_despliegue * v_data["mant_km"]
total_dr_ars = costo_comb_dr + costo_mant_dr

viaticos_ars = db_viaticos[p1] + db_viaticos[p2] + db_viaticos[p3] + db_viaticos[p4]
comb_gen_ars = horas_gen * 1.5 * p_gasoil
conectividad_ars = 87500 / 30
valor_usd = db_drones_usd[dron_sel]
valor_ars_bna = valor_usd * tc_bna
amortizacion_ars = valor_ars_bna * 0.001

total_op_ars = viaticos_ars + comb_gen_ars + conectividad_ars + amortizacion_ars
total_final = total_dr_ars + total_op_ars

# --- INTERFAZ ---
st.markdown(f"### 💹 Cotización: **$ {tc_bna:,.2f}** (BNA Vendedor)")
c1, c2, c3 = st.columns(3)
c1.metric("DESPLIEGUE/REPLIEGUE", f"ARS {total_dr_ars:,.2f}")
c2.metric("COSTO DÍA OPERATIVO", f"ARS {total_op_ars:,.2f}")
c3.metric(f"EQUIPO: {dron_sel}", f"u$s {valor_usd:,.2f}", delta=f"ARS {valor_ars_bna:,.2f}")

resumen = pd.DataFrame({
    "Rubro": ["Combustible Movilidad", "Mantenimiento", "Viáticos (100%)", "Energía", "Conectividad", "Amortización SRT"],
    "Origen": ["ARS", "ARS", "ARS", "ARS", "ARS", "USD"],
    "Costo": [f"$ {costo_comb_dr:,.2f}", f"$ {costo_mant_dr:,.2f}", f"$ {viaticos_ars:,.2f}", f"$ {comb_gen_ars:,.2f}", f"$ {conectividad_ars:,.2f}", f"u$s {valor_usd:,.2f}"],
    "Subtotal ARS": [costo_comb_dr, costo_mant_dr, viaticos_ars, comb_gen_ars, conectividad_ars, amortizacion_ars]
})
st.table(resumen)

# --- FUNCIÓN PARA GENERAR WORD ---
def generate_docx(df, total):
    doc = Document()
    doc.add_heading('PLANILLA DE VALORIZACIÓN DE COSTOS - SRT', 0)
    doc.add_paragraph(f"Vehículo: {vehiculo_sel}")
    doc.add_paragraph(f"Tipo de Cambio BNA: {tc_bna}")
    
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Rubro'
    hdr_cells[1].text = 'Costo Origen'
    hdr_cells[2].text = 'Subtotal (ARS)'

    for index, row in df.iterrows():
        row_cells = table.add_row().cells
        row_cells[0].text = str(row['Rubro'])
        row_cells[1].text = str(row['Costo'])
        row_cells[2].text = f"$ {row['Subtotal ARS']:,.2f}"

    doc.add_paragraph(f"\nTOTAL VALORIZADO: $ {total:,.2f}")
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- BOTÓN DE DESCARGA ---
st.divider()
doc_buffer = generate_docx(resumen, total_final)
st.download_button(
    label="📥 Descargar Planilla en WORD (Editable)",
    data=doc_buffer,
    file_name="valorizacion_mision.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
