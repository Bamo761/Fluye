# pages/1_Clientes.py

import streamlit as st
from components.forms.form_cliente import formulario_cliente
from components.views.lista_clientes import listar_clientes

st.title("Gestión de Clientes")

formulario_cliente()
st.markdown("---")
listar_clientes()
