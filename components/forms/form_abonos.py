#form_abonos
import sqlite3
from db.connection import get_connection
from datetime import datetime
from logicas.simulador import simular_prestamo

# Conexión a la base de datos
    conn = get_connection()
    cursor = conn.cursor()

def registrar_abono(deuda_id, fecha_abono, monto, observacion):
    # 1. Obtener datos básicos de la deuda
    cursor.execute("SELECT cliente_id, monto, interes, cantidad_pagos, frecuencia_pago, tipo_prestamo FROM deudas WHERE id = ?", (deuda_id,))
    deuda = cursor.fetchone()
    if deuda is None:
        raise ValueError("Deuda no encontrada")

    cliente_id, monto_original, interes, cantidad_pagos, frecuencia_pago, tipo_prestamo = deuda

    # 2. Insertar el abono en la tabla abonos
    cursor.execute("INSERT INTO abonos (deuda_id, fecha, monto, observacion) VALUES (?, ?, ?, ?)",
                   (deuda_id, fecha_abono, monto, observacion))

    # 3. Agregar observación como nota
    cursor.execute("INSERT INTO notas (cliente_id, fecha, texto) VALUES (?, ?, ?)",
                   (cliente_id, fecha_abono, f"[Abono] {observacion}"))

    # 4. Obtener cuotas pendientes hasta la fecha del abono
    cursor.execute("""
        SELECT id, n_cuota, fecha, cuota, abono, saldo_restante, estado FROM cronograma_pagos
        WHERE deuda_id = ? AND fecha <= ? AND estado = 'pendiente'
        ORDER BY fecha ASC
    """, (deuda_id, fecha_abono))
    cuotas_pendientes = cursor.fetchall()

    monto_restante = monto
    mora_generada = 0.0

    # 5. Procesar cuotas vencidas
    for cuota in cuotas_pendientes:
        cuota_id, n_cuota, fecha, cuota_valor, abono_actual, saldo_restante, estado = cuota

        cuota_valor = round(cuota_valor, 2)
        saldo_restante = round(saldo_restante, 2)

        if monto_restante <= 0:
            break

        pago = min(saldo_restante, monto_restante)
        nuevo_abono = abono_actual + pago
        nuevo_saldo = saldo_restante - pago
        nuevo_estado = 'pagado' if nuevo_saldo <= 0.01 else 'pendiente'

        cursor.execute("""
            UPDATE cronograma_pagos SET abono = ?, saldo_restante = ?, estado = ? WHERE id = ?
        """, (nuevo_abono, nuevo_saldo, nuevo_estado, cuota_id))

        monto_restante -= pago

    # 6. Verificar si se completaron todas las cuotas
    cursor.execute("SELECT COUNT(*) FROM cronograma_pagos WHERE deuda_id = ? AND estado = 'pendiente'", (deuda_id,))
    cuotas_restantes = cursor.fetchone()[0]

    if cuotas_restantes == 0:
        cursor.execute("UPDATE deudas SET estado = 'cancelada' WHERE id = ?", (deuda_id,))
        conn.commit()
        print("Deuda totalmente saldada.")
        return

    # 7. Si hay excedente (monto_restante > 0), se ofrece refinanciación
    if monto_restante > 0:
        # Obtener datos de cuotas efectivamente pagadas
        cursor.execute("SELECT COUNT(*) FROM cronograma_pagos WHERE deuda_id = ? AND estado = 'pagado'", (deuda_id,))
        cuotas_pagadas = cursor.fetchone()[0]

        nuevas_cuotas = cantidad_pagos - cuotas_pagadas

        if nuevas_cuotas <= 0:
            nuevas_cuotas = 1  # Mínimo 1 cuota

        # Ejecutar simulación de nuevo préstamo
        nuevo_cronograma = simular_prestamo(
            sistema=tipo_prestamo,
            monto=monto_original - obtener_total_abonado(deuda_id) - monto_restante,
            interes=interes,
            cantidad_pagos=nuevas_cuotas,
            periodo_gracia=0,
            fecha_inicio=fecha_abono,
            frecuencia_pago=frecuencia_pago
        )

        # 8. Crear nueva deuda
        cursor.execute("""
            INSERT INTO deudas (cliente_id, intermediario_id, monto, frecuencia_pago, interes, cantidad_pagos,
                                pagos_de_gracia, fecha_inicio, tipo_prestamo, cuota_fija, cuotas_totales,
                                monto_total, tasa_mora, estado)
            VALUES (?, NULL, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, 0, 'activa')
        """, (
            cliente_id,
            nuevo_cronograma['monto_total'],
            frecuencia_pago,
            interes,
            nuevas_cuotas,
            fecha_abono,
            tipo_prestamo,
            nuevo_cronograma['cuota_fija'],
            len(nuevo_cronograma['cuotas']),
            nuevo_cronograma['monto_total']
        ))

        deuda_nueva_id = cursor.lastrowid

        # 9. Registrar cuotas en cronograma
        for cuota in nuevo_cronograma['cuotas']:
            cursor.execute("""
                INSERT INTO cronograma_pagos (cliente_id, deuda_id, n_cuota, fecha, cuota, interes, abono, saldo_restante)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                cliente_id, deuda_nueva_id, cuota['n_cuota'], cuota['fecha'], cuota['cuota'], cuota['interes'], cuota['saldo_restante']
            ))

        # 10. Cancelar cuotas restantes de la deuda original
        cursor.execute("""
            UPDATE cronograma_pagos SET estado = 'cancelada'
            WHERE deuda_id = ? AND estado = 'pendiente'
        """, (deuda_id,))

        # 11. Registrar en tabla refinanciaciones
        cursor.execute("""
            INSERT INTO refinanciaciones (deuda_original_id, deuda_nueva_id, fecha_refinanciamiento, tipo_reduccion, observacion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            deuda_id, deuda_nueva_id, fecha_abono, 'capital', f"Refinanciación por abono con excedente de {monto_restante}"
        ))

    conn.commit()
    print("Abono registrado exitosamente")

def obtener_total_abonado(deuda_id):
    cursor.execute("SELECT SUM(monto) FROM abonos WHERE deuda_id = ?", (deuda_id,))
    total = cursor.fetchone()[0]
    return total if total else 0
