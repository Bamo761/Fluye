#mora

def calcular_mora(faltante, dias_atraso, tasa_mora):
    """
    Calcula la mora acumulada por una cuota atrasada según lo que falta pagar de la cuota.

    Parámetros:
    - faltante: lo que no se ha pagado de la cuota esperada
    - dias_atraso: número de días de atraso
    - tasa_mora: interés diario de mora (ej: 0.01 = 1% diario)

    Retorna:
    - monto de mora acumulado
    """
    mora = faltante * ((1 + tasa_mora) ** dias_atraso - 1)
    return round(mora, 2)
