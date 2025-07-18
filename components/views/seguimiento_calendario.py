import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from db.connection import get_connection

def mostrar_calendario_seguimiento():
    st.title("📅 Seguimiento de Pagos")

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT c.nombre AS cliente, cp.fecha, cp.estado, cp.deuda_id
        FROM cronograma_pagos cp
        JOIN clientes c ON cp.cliente_id = c.id
        JOIN deudas d ON cp.deuda_id = d.id
        WHERE d.estado = 'activa'
    """

    df = pd.read_sql_query(query, conn)
    conn.close()  # Cerramos la conexión porque ya no la necesitamos

    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'])
        hoy = pd.to_datetime(datetime.now().date())

        def estado_real(row):
            if row['estado'] == 'pagado':
                return '✅ Pagado'
            elif row['fecha'] < hoy:
                return '❌ Mora'
            elif row['fecha'] == hoy:
                return '⚠️ Vence hoy'
            else:
                return '🕒 Próximo'

        df['estado_real'] = df.apply(estado_real, axis=1)

        dias_mostrar = st.slider("Ver cuotas de los próximos (días):", 7, 60, 30)
        hasta = hoy + timedelta(days=dias_mostrar)
        df_filtrado = df[(df['fecha'] >= hoy - timedelta(days=3)) & (df['fecha'] <= hasta)]
        df_filtrado = df_filtrado.sort_values("fecha")

        st.subheader("📆 Calendario de Pagos")
        for fecha, grupo in df_filtrado.groupby('fecha'):
            st.markdown(f"### {fecha.strftime('%d/%m/%Y')}")
            for _, row in grupo.iterrows():
                nombre = row['cliente']
                estado = row['estado_real']
                deuda_id = row['deuda_id']
                st.markdown(f"- [{nombre} - {estado}](?dashboard_cliente={deuda_id})")
    else:
        st.info("No hay cuotas registradas aún.")

    # Redirección automática si hay query param (?dashboard_cliente=...)
    if "dashboard_cliente" in st.query_params:
        deuda_id = st.query_params["dashboard_cliente"]
        st.switch_page("pages/7_Dashboard_Cliente.py")
