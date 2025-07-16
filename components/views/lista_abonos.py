#lista_abonos.py

import streamlit as st
import sqlite3
from datetime import datetime
from difflib import get_close_matches
import pandas as pd

def buscar_clientes_similares(nombre_input, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, cedula, placa FROM clientes")
    clientes = cursor.fetchall()
    nombres = [f"{c[1]} - {c[2]} - {c[3]}" for c in clientes]
    coincidencias = get_close_matches(nombre_input, nombres, n=10, cutoff=0.3)
    return [c for c in clientes if f"{c[1]} - {c[2]} - {c[3]}" in coincidencias]

def lista_abonos_view(conn):
    st.title("📜 Lista de Abonos")

    cursor = conn.cursor()

    st.subheader("🔍 Filtros")

    # ------------------------------
    # Filtro por cliente
    nombre_input = st.text_input("Buscar cliente (nombre, placa o cédula)")
    cliente_id_filtrado = None
    if nombre_input:
        clientes = buscar_clientes_similares(nombre_input, conn)
        if clientes:
            cliente_elegido = st.selectbox("Coincidencias encontradas:", clientes, format_func=lambda c: f"{c[1]} - {c[2]} - {c[3]}")
            cliente_id_filtrado = cliente_elegido[0]
        else:
            st.warning("No se encontraron coincidencias.")

    # ------------------------------
    # Filtro por fecha (individual o rango)
    col1, col2 = st.columns(2)
    fecha_inicio = col1.date_input("Desde", value=None)
    fecha_fin = col2.date_input("Hasta", value=None)

    # ------------------------------
    # Query base
    query = """
        SELECT abonos.id, abonos.fecha, abonos.monto, abonos.observacion, clientes.nombre
        FROM abonos
        JOIN deudas ON abonos.deuda_id = deudas.id
        JOIN clientes ON deudas.cliente_id = clientes.id
    """
    condiciones = []
    valores = []

    if cliente_id_filtrado:
        condiciones.append("clientes.id = ?")
        valores.append(cliente_id_filtrado)

    if fecha_inicio:
        condiciones.append("date(abonos.fecha) >= date(?)")
        valores.append(str(fecha_inicio))
    if fecha_fin:
        condiciones.append("date(abonos.fecha) <= date(?)")
        valores.append(str(fecha_fin))

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    query += " ORDER BY abonos.fecha DESC"

    cursor.execute(query, valores)
    resultados = cursor.fetchall()

    if resultados:
        df = pd.DataFrame(resultados, columns=["ID", "Fecha", "Monto", "Observación", "Cliente"])
        st.dataframe(df)
    else:
        st.info("No se encontraron abonos con esos filtros.")
