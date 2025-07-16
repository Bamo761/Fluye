# simulador.py

from logicas import frances, aleman, americano, simple, compuesto  # Ajusta la ruta si están en otra carpeta

SISTEMAS_DISPONIBLES = {
    'frances': frances.calcular_prestamo,
    'aleman': aleman.calcular_prestamo,
    'americano': americano.calcular_prestamo,
    'simple': simple.calcular_prestamo,
    'compuesto': compuesto.calcular_prestamo,
}


def simular_prestamo(
    sistema,
    monto,
    interes,
    cantidad_pagos,
    periodo_gracia,
    fecha_inicio,
    frecuencia_pago
):
    """
    Ejecuta el cálculo del préstamo según el sistema elegido.

    Retorna el resultado del sistema específico.
    """

    sistema = sistema.lower()

    if sistema not in SISTEMAS_DISPONIBLES:
        raise ValueError(f"Sistema '{sistema}' no soportado. Debe ser uno de: {list(SISTEMAS_DISPONIBLES.keys())}")

    funcion_calculo = SISTEMAS_DISPONIBLES[sistema]

    return funcion_calculo(
        monto,
        interes,
        cantidad_pagos,
        periodo_gracia,
        fecha_inicio,
        frecuencia_pago
    )
