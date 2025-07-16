#pages/2_Intermediarios.py

import streamlit as st
from components.forms.form_intermediario import form_intermediario
from components.views.lista_intermediarios import listar_intermediarios

st.title("Intermediarios")

data_edicion = st.session_state.get("intermediario_editar", None)

form_intermediario(data_edicion=data_edicion)

# Limpiar sesión tras uso
if "intermediario_editar" in st.session_state:
    del st.session_state["intermediario_editar"]

st.markdown("---")
listar_intermediarios()
