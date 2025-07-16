# 4_Abonos.py

import streamlit as st
import sqlite3
from components.views.lista_abonos import lista_abonos_view
from components.forms.form_abonos import registrar_abono  # (por ahora no es visual, pero lo importamos si se necesita)

# Conectar a la base de datos
conn = sqlite3.connect('datos.db', check_same_thread=False)

st.title("💸 Gestión de Abonos")

# ---------- Sección de carga de abonos (Formulario visual aquí) ----------
st.subheader("➕ Registrar nuevo abono")

with st.form("formulario_abono"):
    deuda_id = st.number_input("ID de la deuda", min_value=1, step=1)
    fecha_abono = st.date_input("Fecha del abono")
    monto = st.number_input("Monto del abono", min_value=0.0, format="%.2f")
    observacion = st.text_area("Observación", max_chars=200)

    submitted = st.form_submit_button("Registrar Abono")

    if submitted:
        try:
            registrar_abono(deuda_id, fecha_abono.strftime("%Y-%m-%d"), monto, observacion)
            st.success("✅ Abono registrado exitosamente.")
        except Exception as e:
            st.error(f"⚠️ Error al registrar abono: {str(e)}")

# ---------- Sección de lista de abonos ----------
st.divider()
lista_abonos_view(conn)
