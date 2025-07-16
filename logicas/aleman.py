# aleman.py

from datetime import datetime, timedelta

# Mapa de frecuencias a número de días
FRECUENCIA_DIAS = {
    'diario': 1,
    'semanal': 7,
    'quincenal': 15,
    'mensual': 30,
}


def calcular_prestamo(
    monto,
    interes,
    cantidad_pagos,
    periodo_gracia,
    fecha_inicio,
    frecuencia_pago
):
    """
    Calcula préstamo bajo sistema alemán (abono fijo al capital, cuota decreciente).

    Durante el periodo de gracia:
    - No se pagan cuotas.
    - Se acumulan intereses que se suman al saldo y se amortizan después.

    Retorna un dict con:
    - cronograma: lista de pagos
    - cuota_inicial: primera cuota después del periodo de gracia
    - cuotas_totales: cantidad de pagos efectivos
    - monto_total: suma total pagada al final
    """

    if periodo_gracia >= cantidad_pagos:
        raise ValueError("El periodo de gracia no puede ser mayor o igual a la cantidad de pagos.")

    dias_por_periodo = FRECUENCIA_DIAS[frecuencia_pago]
    fecha_base = datetime.strptime(fecha_inicio, "%Y-%m-%d")

    # Paso 1: calcular intereses acumulados durante el periodo de gracia
    saldo = monto
    interes_acumulado = 0.0

    for _ in range(periodo_gracia):
        interes_acumulado += round(saldo * interes, 2)

    saldo_total = round(monto + interes_acumulado, 2)
    cuotas_totales = cantidad_pagos - periodo_gracia
    abono_fijo = round(saldo_total / cuotas_totales, 2)

    cronograma = []

    for i in range(cantidad_pagos):
        fecha_pago = fecha_base + timedelta(days=i * dias_por_periodo)

        if i < periodo_gracia:
            cuota = 0.0
            interes_cuota = 0.0
            abono = 0.0
        else:
            interes_cuota = round(saldo_total * interes, 2)
            cuota = round(interes_cuota + abono_fijo, 2)
            abono = abono_fijo
            saldo_total = round(saldo_total - abono, 2)

        cronograma.append({
            "n_cuota": i + 1,
            "fecha": fecha_pago.strftime("%Y-%m-%d"),
            "cuota": cuota,
            "interes": interes_cuota,
            "abono": abono,
            "saldo_restante": max(saldo_total, 0),
        })

    monto_total_pagado = round(sum(p["cuota"] for p in cronograma), 2)

    return {
        "cronograma": cronograma,
        "cuota_inicial": cronograma[periodo_gracia]["cuota"] if cuotas_totales > 0 else 0,
        "cuotas_totales": cuotas_totales,
        "monto_total": monto_total_pagado
    }
