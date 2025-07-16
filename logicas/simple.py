#simple.py

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
    Calcula un préstamo con interés simple considerando período de gracia.
    Durante el período de gracia no se paga nada, pero los intereses se acumulan igual.
    """

    dias_por_periodo = FRECUENCIA_DIAS[frecuencia_pago]
    fecha_base = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    cuotas_totales = cantidad_pagos - periodo_gracia

    if cuotas_totales <= 0:
        raise ValueError("El periodo de gracia no puede ser mayor o igual a la cantidad de pagos.")

    # Se calcula el interés simple por el total de períodos (incluyendo gracia)
    total_interes = monto * interes * cantidad_pagos
    monto_total = monto + total_interes

    cuota_fija = round(monto_total / cuotas_totales, 2)
    saldo = monto_total

    cronograma = []

    for i in range(cantidad_pagos):
        fecha_pago = fecha_base + timedelta(days=i * dias_por_periodo)

        if i < periodo_gracia:
            cuota = 0.0
            interes_cuota = 0.0
            abono = 0.0
        else:
            interes_cuota = round(monto * interes, 2)
            abono = round(cuota_fija - interes_cuota, 2)
            cuota = cuota_fija
            saldo = round(saldo - cuota, 2)

        cronograma.append({
            "n_cuota": i + 1,
            "fecha": fecha_pago.strftime("%Y-%m-%d"),
            "cuota": cuota,
            "interes": interes_cuota,
            "abono": abono,
            "saldo_restante": max(saldo, 0),
        })

    return {
        "cronograma": cronograma,
        "cuota_fija": cuota_fija,
        "cuotas_totales": cuotas_totales,
        "monto_total": round(monto_total, 2)
    }



