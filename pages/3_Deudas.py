#3_Deudas.py

import streamlit as st
import pandas as pd
import difflib
from db.connection import get_connection
from components.forms.form_deudas import formulario_deuda


# ─── Función para cargar deudas desde la base de datos ────────────────

def cargar_deudas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, c.nombre, c.cedula, c.placa, 
               IFNULL(i.nombre, '-') as intermediario,
               d.monto, d.interes, d.cuotas_totales, 
               d.monto_total, d.tipo_prestamo, 
               d.fecha_inicio, d.estado
        FROM deudas d
        JOIN clientes c ON d.cliente_id = c.id
        LEFT JOIN intermediarios i ON d.intermediario_id = i.id
        ORDER BY d.fecha_inicio DESC
    """)
    rows = cursor.fetchall()
    columnas = ["ID", "Cliente", "Cédula", "Placa", "Intermediario",
                "Monto", "Interés", "Cuotas", "Total", "Tipo", "Inicio", "Estado"]
    df = pd.DataFrame(rows, columns=columnas)
    conn.close()
    return df


# ─── Búsqueda difusa por columnas combinadas ───────────────────────────

def buscar_coincidencias(valor_buscado, df, columnas):
    combinadas = df[columnas].astype(str).agg(" - ".join, axis=1).tolist()
    coincidencias = difflib.get_close_matches(valor_buscado, combinadas, n=10, cutoff=0.3)
    return df[df[columnas].astype(str).agg(" - ".join, axis=1).isin(coincidencias)]


# ─── Vista completa para esta pestaña de Deudas ────────────────────────

def vista_deudas():
    st.title("💰 Gestión de Deudas")

    tabs = st.tabs(["📒 Lista de Deudas", "🧾 Registrar Nueva Deuda"])

    # ─── TAB 1: LISTA DE DEUDAS ─────────────────────────────────────────

    with tabs[0]:
        st.subheader("🔍 Buscar por cliente / cédula / placa / intermediario")
        df = cargar_deudas()

        if df.empty:
            st.warning("No hay deudas registradas aún.")
        else:
            busqueda = st.text_input("Escribe al menos 3 letras", max_chars=50)

            if len(busqueda) >= 3:
                df_filtrado = buscar_coincidencias(busqueda, df, ["Cliente", "Cédula", "Placa", "Intermediario"])
            else:
                df_filtrado = df.copy()

            st.write(f"Se encontraron **{len(df_filtrado)}** deudas.")
            st.dataframe(df_filtrado, use_container_width=True)

            if not df_filtrado.empty:
                with st.expander("📊 Ver resumen por cliente"):
                    resumen = df_filtrado.groupby("Cliente")[["Monto", "Total"]].sum().reset_index()
                    resumen.columns = ["Cliente", "Monto Total", "Total a Pagar"]
                    st.dataframe(resumen, use_container_width=True)

    # ─── TAB 2: FORMULARIO NUEVA DEUDA ──────────────────────────────────

    with tabs[1]:
        formulario_deuda()


vista_deudas()