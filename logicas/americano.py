# americano.py

from datetime import datetime, timedelta

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
    Calcula préstamo bajo sistema americano (solo intereses hasta el final, capital se paga todo en la última cuota).

    Durante el periodo de gracia:
    - No se pagan cuotas.
    - Los intereses se acumulan y se pagan después.

    Retorna un dict con:
    - cronograma: lista de pagos
    - intereses_acumulados: intereses no pagados durante la gracia
    - monto_total: total pagado al final del préstamo
    """

    if periodo_gracia >= cantidad_pagos:
        raise ValueError("El periodo de gracia no puede ser mayor o igual a la cantidad de pagos.")

    dias_por_periodo = FRECUENCIA_DIAS[frecuencia_pago]
    fecha_base = datetime.strptime(fecha_inicio, "%Y-%m-%d")

    interes_periodico = round(monto * interes, 2)
    intereses_acumulados = round(interes_periodico * periodo_gracia, 2)
    cronograma = []

    for i in range(cantidad_pagos):
        fecha_pago = fecha_base + timedelta(days=i * dias_por_periodo)

        if i < periodo_gracia:
            cuota = 0.0
            interes_cuota = 0.0
            abono = 0.0

        elif i < cantidad_pagos - 1:
            cuota = interes_periodico
            interes_cuota = interes_periodico
            abono = 0.0

        else:
            cuota = interes_periodico + monto + intereses_acumulados
            interes_cuota = interes_periodico + intereses_acumulados
            abono = monto

        saldo_restante = 0.0 if i == cantidad_pagos - 1 else monto

        cronograma.append({
            "n_cuota": i + 1,
            "fecha": fecha_pago.strftime("%Y-%m-%d"),
            "cuota": round(cuota, 2),
            "interes": round(interes_cuota, 2),
            "abono": round(abono, 2),
            "saldo_restante": saldo_restante,
        })

    monto_total = round(sum(p["cuota"] for p in cronograma), 2)

    return {
        "cronograma": cronograma,
        "intereses_acumulados": intereses_acumulados,
        "monto_total": monto_total
    }
