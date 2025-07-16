# components/forms/form_cliente.py

import streamlit as st
from db.connection import get_connection

def formulario_cliente():
    conn = get_connection()
    cursor = conn.cursor()

    cliente = st.session_state.get("cliente_a_editar", None)

    st.markdown("### Formulario de Cliente")

    with st.form("form_cliente"):
        nombre = st.text_input("Nombre completo", value=cliente["Nombre"] if cliente else "")
        cedula = st.text_input("Cédula", value=str(cliente["Cédula"]) if cliente else "")
        direccion = st.text_input("Dirección", value=cliente["Dirección"] if cliente else "")
        placa = st.text_input("Placa del vehículo", value=cliente["Placa"] if cliente else "")
        sector = st.text_input("Sector", value=cliente["Sector"] if cliente else "")
        correo = st.text_input("Correo electrónico", value=cliente["Correo"] if cliente else "")
        telefono = st.text_input("Teléfono", value=cliente["Teléfono"] if cliente else "")
        coordenada_x = st.number_input("Coordenada X", format="%.6f", value=cliente["X"] if cliente else 0.0)
        coordenada_y = st.number_input("Coordenada Y", format="%.6f", value=cliente["Y"] if cliente else 0.0)
        activo = st.checkbox("Activo", value=bool(cliente["Activo"]) if cliente else True)

        submitted = st.form_submit_button("Guardar cliente")

        if submitted:
            if not nombre or not cedula:
                st.warning("El nombre y la cédula son obligatorios.")
                return

            if not (direccion or telefono or placa):
                st.warning("Debes ingresar al menos uno entre Dirección, Teléfono o Placa.")
                return

            # Comprobamos si ya existe un cliente con esa cédula
            cursor.execute("SELECT id FROM clientes WHERE cedula = ?", (cedula,))
            cliente_existente = cursor.fetchone()

            if cliente_existente:
                cursor.execute("""
                    UPDATE clientes SET
                        nombre = ?, direccion = ?, placa = ?, sector = ?, correo = ?,
                        telefono = ?, coordenada_x = ?, coordenada_y = ?, activo = ?
                    WHERE cedula = ?
                """, (
                    nombre, direccion, placa, sector, correo, telefono,
                    coordenada_x or None, coordenada_y or None,
                    1 if activo else 0, cedula
                ))
                st.success(f"Cliente actualizado: {nombre}")
            else:
                cursor.execute("""
                    INSERT INTO clientes (
                        nombre, cedula, direccion, placa, sector, correo, telefono,
                        coordenada_x, coordenada_y, activo
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                                   nombre, cedula, direccion, placa, sector, correo, telefono,
                                   coordenada_x or None, coordenada_y or None,
                                   1 if activo else 0
                ))
                st.success("Cliente registrado.")

            conn.commit()
            st.session_state.pop("cliente_a_editar", None)  # Limpiamos después de guardar
            st.experimental_rerun()

    cursor.close()
    conn.close()
