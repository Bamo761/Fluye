#components/forms/form_intermediario.py

import streamlit as st
from db.connection import get_connection

def form_intermediario(data_edicion=None):
    st.subheader("Agregar / Editar Intermediario")

    nombre = st.text_input("Nombre del intermediario", value=data_edicion["nombre"] if data_edicion else "")
    contacto = st.number_input(
        "Contacto (número de teléfono)",
        value=float(data_edicion["contacto"]) if data_edicion and data_edicion["contacto"] else 0.0,
        format="%0.0f"
    )

    if st.button("Guardar Intermediario"):
        if not nombre or not contacto:
            st.warning("Por favor, completa todos los campos obligatorios.")
            return

        conn = get_connection()
        cursor = conn.cursor()

        if data_edicion:
            # Actualizar
            cursor.execute("""
                UPDATE intermediarios
                SET nombre = ?, contacto = ?
                WHERE id = ?
            """, (nombre, contacto, data_edicion["id"]))
            st.success("Intermediario actualizado correctamente.")
        else:
            # Insertar nuevo
            cursor.execute("""
                INSERT INTO intermediarios (nombre, contacto)
                VALUES (?, ?)
            """, (nombre, contacto))
            st.success("Intermediario agregado correctamente.")

        conn.commit()
        conn.close()

