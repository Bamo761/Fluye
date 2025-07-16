import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from db.connection import get_connection

st.set_page_config(page_title="Dashboard General", layout="wide")

# --- Conexión a la base de datos --- #
conn = get_connection()
cursor = conn.cursor()

def get_datos_dashboard(fecha_inicio=None, fecha_fin=None):
    query = """
        SELECT d.id as deuda_id, d.estado, d.fecha_inicio, d.monto, d.interes as interes_deuda,
               c.nombre as cliente, cp.fecha, cp.cuota, cp.interes as interes_pago, cp.abono,
               cp.saldo_restante, cp.estado as estado_cuota
        FROM deudas d
        LEFT JOIN clientes c ON d.cliente_id = c.id
        LEFT JOIN cronograma_pagos cp ON cp.deuda_id = d.id
    """

    df = pd.read_sql_query(query, conn)
    df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')

    if fecha_inicio and fecha_fin:
        df = df[(df["fecha"] >= fecha_inicio) & (df["fecha"] <= fecha_fin)]

    return df

# --- Filtros --- #
st.title("📊 Dashboard General")

col1, col2 = st.columns(2)

with col1:
    fecha_inicio = st.date_input("Desde", datetime.today().replace(day=1))
with col2:
    fecha_fin = st.date_input("Hasta", datetime.today())

fecha_inicio = pd.to_datetime(fecha_inicio)
fecha_fin = pd.to_datetime(fecha_fin)

# --- Obtener datos filtrados --- #
df = get_datos_dashboard(fecha_inicio, fecha_fin)

# --- Métricas generales --- #
cuotas_pagadas = df[df['estado_cuota'] == 'pagado']

capital_pagado = cuotas_pagadas['abono'].sum()
interes_ganado = cuotas_pagadas['interes_pago'].sum() if not cuotas_pagadas.empty else 0
mora_ganada = 0  # Puedes calcularla si llevás tabla de mora aparte

saldo_pendiente = df[df['estado_cuota'] == 'pendiente']['saldo_restante'].sum()

# --- Deudas activas vs canceladas --- #
deudas_estado = df.groupby('estado')['deuda_id'].nunique().reset_index()

# --- Mostrar métricas --- #
st.subheader("Resumen de Ingresos")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Capital recibido", f"${capital_pagado:,.0f}")
col2.metric("📈 Intereses ganados", f"${interes_ganado:,.0f}")
col3.metric("❗️ Pendiente por cobrar", f"${saldo_pendiente:,.0f}")
col4.metric("⏳ Total ganado (cap + int)", f"${capital_pagado + interes_ganado:,.0f}")

st.divider()

# --- Visualización Deudas Activas vs Canceladas --- #
st.subheader("🧮 Estado de las deudas")

deudas_estado.columns = ['Estado', 'Cantidad']
st.bar_chart(deudas_estado.set_index('Estado'))

# --- Tabla resumen de cuotas --- #
st.subheader("📆 Detalle de pagos en el periodo")
if not cuotas_pagadas.empty:
    st.dataframe(cuotas_pagadas[['cliente', 'fecha', 'cuota', 'abono', 'interes_pago']], use_container_width=True)
else:
    st.info("No se encontraron pagos registrados en el período seleccionado.")

conn.close()
