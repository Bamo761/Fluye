# main.py

import streamlit as st
from db.crear_db import crear_tablas
crear_tablas()
# Configuración inicial
st.set_page_config(
    page_title="Fluye - Seguimiento de Deudas",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos personalizados
with open("assets/estilos.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Portada
st.image("assets/logos/mi_logo.png", width=150)
st.title("💸 Bienvenido a *Fluye*")
st.markdown("""
Bienvenido al sistema de seguimiento de deudas.  
Desde la barra lateral podés acceder a:
- Registro de clientes, deudas, abonos e intermediarios  
- Seguimiento de pagos en calendario  
- Dashboards de análisis  
""")
st.success("Elige una pestaña en el menú de la izquierda para comenzar.")