#compuesto

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
    Calcula préstamo con interés compuesto. Durante el periodo de gracia no se paga nada,
    pero se capitalizan los intereses. Luego se calculan cuotas fijas sobre el nuevo monto.
    """

    dias_por_periodo = FRECUENCIA_DIAS[frecuencia_pago]
    fecha_base = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    cuotas_totales = cantidad_pagos - periodo_gracia

    if cuotas_totales <= 0:
        raise ValueError("El periodo de gracia no puede ser mayor o igual a la cantidad de pagos.")

    r = interes

    # Capitalizamos intereses durante el período de gracia
    monto_ajustado = round(monto * ((1 + r) ** periodo_gracia), 2)

    # Cálculo de cuota fija con fórmula de anualidades sobre el nuevo monto
    if r == 0:
        cuota_fija = round(monto_ajustado / cuotas_totales, 2)
    else:
        cuota_fija = round(monto_ajustado * r * (1 + r) ** cuotas_totales / ((1 + r) ** cuotas_totales - 1), 2)

    saldo = monto_ajustado
    cronograma = []

    for i in range(cantidad_pagos):
        fecha_pago = fecha_base + timedelta(days=i * dias_por_periodo)

        if i < periodo_gracia:
            cuota = 0.0
            interes_cuota = 0.0
            abono = 0.0
        else:
            interes_cuota = round(saldo * r, 2)
            abono = round(cuota_fija - interes_cuota, 2)
            cuota = round(interes_cuota + abono, 2)
            saldo = round(saldo - abono, 2)

        cronograma.append({
            "n_cuota": i + 1,
            "fecha": fecha_pago.strftime("%Y-%m-%d"),
            "cuota": cuota,
            "interes": interes_cuota,
            "abono": abono,
            "saldo_restante": max(saldo, 0),
        })

    monto_total = round(cuota_fija * cuotas_totales, 2)

    return {
        "cronograma": cronograma,
        "cuota_fija": cuota_fija,
        "cuotas_totales": cuotas_totales,
        "monto_total": monto_total
    }

