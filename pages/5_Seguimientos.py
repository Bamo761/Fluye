import streamlit as st
from components.views.seguimiento_calendario import mostrar_calendario_seguimiento

st.set_page_config(page_title="Seguimiento de Pagos", layout="wide")

st.title("📅 Seguimiento de pagos")
st.markdown("Visualiza el estado de pagos de cada cliente según el cronograma. Haz clic en un nombre para ir a su dashboard.")

mostrar_calendario_seguimiento()
