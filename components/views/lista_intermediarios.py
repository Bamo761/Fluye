#components/views/lista_intermediarios.py

import streamlit as st
from db.connection import get_connection

def listar_intermediarios():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM intermediarios")
    intermediarios = cursor.fetchall()
    conn.close()

    st.subheader("Lista de Intermediarios")
    st.write("Haz clic en 'Editar' para modificar un intermediario.")

    for inter in intermediarios:
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            st.markdown(f"**{inter[1]}**")  # nombre
        with col2:
            st.markdown(f"📞 {inter[2]}")  # contacto
        with col3:
            if st.button("Editar", key=f"editar_inter_{inter[0]}"):
                st.session_state["intermediario_editar"] = {
                    "id": inter[0],
                    "nombre": inter[1],
                    "contacto": inter[2]
                }
                st.rerun()
