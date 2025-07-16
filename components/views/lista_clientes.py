# components/views/lista_clientes.py

import streamlit as st
import pandas as pd
from db.connection import get_connection

def listar_clientes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre, cedula, direccion, placa, sector, correo, telefono, 
               coordenada_x, coordenada_y, activo 
        FROM clientes
        ORDER BY nombre ASC
    """)
    rows = cursor.fetchall()

    columnas = ["ID", "Nombre", "Cédula", "Dirección", "Placa", "Sector", "Correo", "Teléfono", "X", "Y", "Activo"]
    df = pd.DataFrame(rows, columns=columnas)

    st.markdown("## Lista de Clientes")

    for index, row in df.iterrows():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{row['Nombre']}** - Cédula: {row['Cédula']} - Tel: {row['Teléfono']}")
        with col2:
            if st.button("✏️ Editar", key=f"edit_{row['ID']}"):
                st.session_state['cliente_a_editar'] = row.to_dict()
                st.rerun()  # Recarga para que el formulario detecte el cliente

    cursor.close()
    conn.close()
