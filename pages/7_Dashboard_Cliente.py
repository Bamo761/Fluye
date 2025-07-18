import streamlit as st
import sqlite3
import pandas as pd
from db.connection import get_connection





st.set_page_config(page_title="Dashboard Cliente", layout="wide")

# --- Conexión a la base de datos --- #
conn = get_connection()
cursor = conn.cursor()

# FUNCIÓN UTILITARIA PARA BUSCAR CLIENTES
def buscar_clientes(query):
    query_like = f"%{query}%"
    return cursor.execute("""
        SELECT id, nombre, cedula, placa
        FROM clientes
        WHERE nombre LIKE ? OR cedula LIKE ? OR placa LIKE ?
    """, (query_like, query_like, query_like)).fetchall()

# 1. Buscar cliente si no se recibe por parámetro
cliente_id = st.query_params.get("cliente_id", None)

if not cliente_id:
    st.subheader("🔍 Buscar cliente por nombre, placa o cédula")
    input_query = st.text_input("Ingrese el nombre, cédula o placa del cliente")

    if input_query:
        resultados = buscar_clientes(input_query)
        if len(resultados) == 0:
            st.warning("No se encontraron coincidencias.")
            st.stop()
        elif len(resultados) == 1:
            cliente_id = resultados[0][0]
        else:
            opciones = {f"{nombre} | {cedula} | {placa}": id_ for id_, nombre, cedula, placa in resultados}
            seleccion = st.selectbox("Seleccione un cliente:", opciones.keys())
            cliente_id = opciones[seleccion]

if not cliente_id:
    st.warning("Seleccione un cliente para continuar.")
    st.stop()

# Asegurarse de convertir a int
cliente_id = int(cliente_id)

# 2. Obtener info del cliente
cliente = cursor.execute("""
    SELECT nombre, cedula, direccion, placa, sector, telefono, correo
    FROM clientes WHERE id = ?
""", (cliente_id,)).fetchone()

if cliente is None:
    st.error("Cliente no encontrado.")
    st.stop()

st.header(f"📌 Dashboard del cliente: {cliente[0]}")
st.write(f"**Cédula:** {cliente[1]} | **Dirección:** {cliente[2]} | **Teléfono:** {cliente[5]} | **Correo:** {cliente[6]}")

# 3. Obtener deuda activa
deuda = cursor.execute("""
    SELECT id, monto, interes, frecuencia_pago, cantidad_pagos, pagos_de_gracia,
           fecha_inicio, tipo_prestamo, cuota_fija, monto_total, tasa_mora, estado
    FROM deudas WHERE cliente_id = ? ORDER BY fecha_inicio DESC LIMIT 1
""", (cliente_id,)).fetchone()

if deuda is None:
    st.warning("Este cliente no tiene deudas registradas.")
    st.stop()

(deuda_id, monto, interes, frecuencia, cantidad_pagos, pagos_gracia,
 fecha_inicio, tipo_prestamo, cuota_fija, monto_total, tasa_mora, estado) = deuda

# 4. Obtener cronograma
df_crono = pd.read_sql_query("""
    SELECT n_cuota, fecha, cuota, interes, abono, saldo_restante, estado
    FROM cronograma_pagos
    WHERE cliente_id = ? AND deuda_id = ?
    ORDER BY n_cuota ASC
""", conn, params=(cliente_id, deuda_id))

# 5. Métricas calculadas
total_abonado = df_crono["abono"].sum()
cuotas_pagadas = df_crono[df_crono["estado"] == "pagado"].shape[0]
cuotas_mora = df_crono[df_crono["estado"] == "mora"].shape[0]
cuotas_pendientes = df_crono[df_crono["estado"] == "pendiente"].shape[0]
dias_en_mora = cuotas_mora * {"diaria": 1, "semanal": 7, "quincenal": 15, "mensual": 30}.get(frecuencia, 30)

capital_pagado = total_abonado - df_crono["interes"].sum()
interes_pagado = df_crono["interes"].sum()

# 6. Mostrar KPIs
st.subheader("📊 Resumen de la deuda")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Monto Total", f"${monto_total:,.0f}")
col2.metric("📅 Cuotas", f"{cantidad_pagos} cuotas de ${cuota_fija:,.0f}")
col3.metric("🟢 Pagadas", f"{cuotas_pagadas}")
col4.metric("🔴 En Mora", f"{cuotas_mora} ({dias_en_mora} días)")

col5, col6, col7 = st.columns(3)
col5.metric("💸 Total Abonado", f"${total_abonado:,.0f}")
col6.metric("🏦 Capital Pagado", f"${capital_pagado:,.0f}")
col7.metric("📈 Intereses Pagados", f"${interes_pagado:,.0f}")

# 7. Mostrar detalles de la deuda
st.subheader("📑 Detalles de la deuda")
