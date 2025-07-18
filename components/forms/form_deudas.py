# form_deudas.py
import streamlit as st
import difflib
from datetime import date
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
    try:
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
    except Exception as e:
        st.error(f"💥 Error al guardar deuda: {e}")
        return None

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
    st.caption(f"Versión de Streamlit: {st.__version__}")

    st.header("🧾 Registro de Nueva Deuda")

    clientes = obtener_clientes(cursor)
    intermediarios = obtener_intermediarios(cursor)

    if "cliente_seleccionado" not in st.session_state:
        st.session_state.cliente_seleccionado = None

    cliente = st.session_state.cliente_seleccionado

    if cliente is None:
        st.subheader("Buscar Cliente")
        nombre_ingresado = st.text_input("Nombre / Cédula / Placa")
        coincidencias = buscar_cliente(nombre_ingresado, clientes) if nombre_ingresado else []

        if coincidencias:
            opcion = st.selectbox("Coincidencias:", coincidencias, key="coincidencia_seleccionada")
            st.write("🔍 Opción seleccionada:", opcion)

            if st.button("✅ Seleccionar cliente"):
                try:
                    partes = opcion.split(" - ")
                    if len(partes) < 2:
                        st.error("⚠️ Opción inválida: no se puede extraer cédula.")
                    else:
                        cedula = partes[1].strip()
                        cliente_encontrado = next((c for c in clientes if str(c["cedula"]).strip() == cedula), None)

                        if cliente_encontrado:
                            st.session_state.cliente_seleccionado = cliente_encontrado
                            st.success(f"Cliente encontrado: {cliente_encontrado['nombre']}")
                            st.rerun()
                        else:
                            st.error("😕 No se encontró el cliente con esa cédula.")
                except Exception as e:
                    st.exception(e)

        st.info("Busca y selecciona un cliente para comenzar.")

    else:
        st.success(f"Cliente seleccionado: {cliente['nombre']} ({cliente['cedula']})")

        if st.button("🔁 Cambiar cliente"):
            st.session_state.cliente_seleccionado = None
            st.session_state.pop("cronograma", None)
            st.rerun()

        intermediario_opciones = [i["nombre"] for i in intermediarios]
        intermediario_nombre = st.selectbox("Intermediario", intermediario_opciones)
        intermediario = next((i for i in intermediarios if i["nombre"] == intermediario_nombre), None)

        st.markdown("---")
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

            st.session_state["cronograma"] = resultado["cronograma"]
            st.session_state["cuota_fija"] = resultado.get("cuota_fija", 0)
            st.session_state["monto_total"] = resultado["monto_total"]
            st.session_state["cuotas_totales"] = resultado.get("cuotas_totales", cantidad_pagos)

            st.success("Simulación exitosa ✅")

        if "cronograma" in st.session_state:
            st.info(f"**Cuota fija:** {st.session_state['cuota_fija']:.2f} | "
                    f"**Monto total:** {st.session_state['monto_total']:.2f} | "
                    f"**# Cuotas:** {st.session_state['cuotas_totales']}")

            st.subheader("📅 Cronograma de Pagos")
            st.dataframe(st.session_state["cronograma"], use_container_width=True)

            if st.button("💾 Guardar deuda y cronograma"):
                deuda_id = guardar_deuda(
                    cursor,
                    cliente["id"],
                    intermediario["id"],
                    monto,
                    frecuencia_pago,
                    interes,
                    cantidad_pagos,
                    pagos_de_gracia,
                    fecha_inicio.isoformat(),
                    tipo_prestamo,
                    st.session_state["cuota_fija"],
                    st.session_state["cuotas_totales"],
                    st.session_state["monto_total"],
                    tasa_mora
                )

                if deuda_id:
                    conn.commit()  # 👈 AHORA SÍ: justo después de guardar la deuda

                    if not cronograma_existe(deuda_id, cursor):
                        guardar_cronograma(st.session_state["cronograma"], cliente["id"], deuda_id, cursor)
                        conn.commit()
                        st.success("Deuda y cronograma guardados exitosamente 🥳")
                        # Limpiar estado
                        st.session_state.pop("cronograma")
                        st.session_state.pop("cuota_fija")
                        st.session_state.pop("monto_total")
                        st.session_state.pop("cuotas_totales")
                        st.session_state.cliente_seleccionado = None
                        st.rerun()
                    else:
                        st.warning("Esta deuda ya tiene cronograma registrado.")
                else:
                    st.error("❌ No se pudo guardar la deuda.")

    cursor.close()
    conn.close()
