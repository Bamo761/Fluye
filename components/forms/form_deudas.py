#form_deudas.py
import streamlit as st
import difflib
from datetime import datetime, date
from db.connection import get_connection
from logicas.simulador import simular_prestamo


# ─── Funciones auxiliares ───────────────────────────────────────────

def obtener_clientes(cursor):
    cursor.execute("SELECT id, nombre, cedula, placa FROM clientes")
    rows = cursor.fetchall()
    return [{"id": r[0], "nombre": r[1], "cedula": r[2], "placa": r[3]} for r in rows]


def obtener_intermediarios(cursor):
    cursor.execute("SELECT id, nombre FROM intermediarios")
    rows = cursor.fetchall()
    return [{"id": r[0], "nombre": r[1]} for r in rows]


def buscar_cliente(nombre_buscado, clientes):
    opciones = [f'{c["nombre"]} - {c["cedula"]} - {c["placa"]}' for c in clientes]
    coincidencias = difflib.get_close_matches(nombre_buscado, opciones, n=10, cutoff=0.3)
    return coincidencias


def guardar_deuda(cursor, cliente_id, intermediario_id, monto, frecuencia_pago, interes,
                  cantidad_pagos, pagos_de_gracia, fecha_inicio, tipo_prestamo,
                  cuota_fija, cuotas_totales, monto_total, tasa_mora):
    cursor.execute("""
        INSERT INTO deudas (
            cliente_id, intermediario_id, monto, frecuencia_pago, interes,
            cantidad_pagos, pagos_de_gracia, fecha_inicio, tipo_prestamo,
            cuota_fija, cuotas_totales, monto_total, tasa_mora, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activa')
    """, (
        cliente_id, intermediario_id, monto, frecuencia_pago, interes,
        cantidad_pagos, pagos_de_gracia, fecha_inicio, tipo_prestamo,
        cuota_fija, cuotas_totales, monto_total, tasa_mora
    ))
    return cursor.lastrowid


def guardar_cronograma(cronograma, cliente_id, deuda_id, cursor):
    for fila in cronograma:
        cursor.execute("""
            INSERT INTO cronograma_pagos (
                deuda_id, cliente_id, n_cuota, fecha, cuota, interes, abono, saldo_restante
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            deuda_id, cliente_id, fila["n_cuota"], fila["fecha"], fila["cuota"],
            fila["interes"], fila["abono"], fila["saldo_restante"]
        ))


def cronograma_existe(deuda_id, cursor):
    cursor.execute("SELECT COUNT(*) FROM cronograma_pagos WHERE deuda_id = ?", (deuda_id,))
    count = cursor.fetchone()[0]
    return count > 0


# ─── FORMULARIO ─────────────────────────────────────────────────────

def formulario_deuda():

    conn = get_connection()
    cursor = conn.cursor()

    st.header("🧾 Registro de Nueva Deuda")

    clientes = obtener_clientes(cursor)
    intermediarios = obtener_intermediarios(cursor)

    st.subheader("Buscar Cliente")
    nombre_ingresado = st.text_input("Nombre / Cédula / Placa")

    coincidencias = buscar_cliente(nombre_ingresado, clientes) if nombre_ingresado else []

    if coincidencias:
        opcion = st.selectbox("Coincidencias:", coincidencias, key="coincidencia_seleccionada")
    
        if st.button("✅ Seleccionar cliente"):
            cedula = opcion.split(" - ")[1]
            cliente = next((c for c in clientes if c["cedula"] == cedula), None)
            if cliente:
                st.session_state.cliente_seleccionado = cliente


    cliente_seleccionado = st.session_state.get("cliente_seleccionado", None)


    if cliente_seleccionado:
        st.success(f"Cliente seleccionado: {cliente_seleccionado['nombre']} ({cliente_seleccionado['cedula']})")

        intermediario_opciones = [i["nombre"] for i in intermediarios]
        intermediario_nombre = st.selectbox("Intermediario", intermediario_opciones)
        intermediario = next((i for i in intermediarios if i["nombre"] == intermediario_nombre), None)

        st.divider()
        st.subheader("Datos del préstamo")

        monto = st.number_input("Monto del préstamo", min_value=0.0, format="%.2f")
        interes = st.number_input("Interés mensual (ej: 0.05 para 5%)", min_value=0.0, format="%.4f")
        cantidad_pagos = st.number_input("Número de cuotas", min_value=1, step=1)
        pagos_de_gracia = st.number_input("Meses de gracia", min_value=0, step=1)
        tasa_mora = st.number_input("Tasa de mora mensual", min_value=0.0, format="%.4f")
        frecuencia_pago = st.selectbox("Frecuencia de pago", ["mensual", "quincenal", "semanal"])
        fecha_inicio = st.date_input("Fecha de inicio", value=date.today())
        tipo_prestamo = st.selectbox("Tipo de préstamo", ["frances", "aleman", "americano", "simple", "compuesto"])

        with st.expander("🧠 ¿Qué significa cada sistema de préstamo?"):
            st.info("""
            **Francés**: Cuota fija.  
            **Alemán**: Amortización fija, intereses decrecientes.  
            **Americano**: Intereses periódicos y capital al final.  
            **Simple/Compuesto**: Modelos financieros generales.
            """)

        if st.button("📊 Simular"):
            resultado = simular_prestamo(
                tipo_prestamo, monto, interes, cantidad_pagos,
                pagos_de_gracia, fecha_inicio, frecuencia_pago
            )

            st.success("Simulación exitosa ✅")

            cuota_fija = resultado.get("cuota_fija", 0)
            monto_total = resultado["monto_total"]
            cuotas_totales = resultado.get("cuotas_totales", cantidad_pagos)

            st.info(f"**Cuota fija:** {cuota_fija:.2f} | **Monto total:** {monto_total:.2f} | **# Cuotas:** {cuotas_totales}")

            cronograma = resultado["cronograma"]
            st.subheader("📅 Cronograma de Pagos")
            st.dataframe(cronograma, use_container_width=True)

            if st.button("💾 Guardar deuda y cronograma"):
                deuda_id = guardar_deuda(
                    cursor, cliente_seleccionado["id"], intermediario["id"], monto,
                    frecuencia_pago, interes, cantidad_pagos, pagos_de_gracia,
                    fecha_inicio.isoformat(), tipo_prestamo,
                    cuota_fija, cuotas_totales, monto_total, tasa_mora
                )

                if not cronograma_existe(deuda_id, cursor):
                    guardar_cronograma(cronograma, cliente_seleccionado["id"], deuda_id, cursor)
                    conn.commit()
                    st.success("Deuda y cronograma guardados exitosamente 🥳")
                else:
                    st.warning("Esta deuda ya tiene cronograma registrado. No se volvió a guardar.")

    else:
        st.info("Busca y selecciona un cliente para comenzar.")

    cursor.close()
    conn.close()
