from Backend.modelos import ProblemaLineal, Restriccion
from Backend.simplex import resolver_simplex


def construir_dual(problema: ProblemaLineal) -> ProblemaLineal:
    """Construye el dual para un primal con variables x >= 0."""
    es_max = problema.tipo == "max"
    objetivo_dual = [r.termino_independiente for r in problema.restricciones]
    restricciones_dual = []
    for columna in range(len(problema.objetivo)):
        coeficientes = [r.coeficientes[columna] for r in problema.restricciones]
        restricciones_dual.append(Restriccion(coeficientes, ">=" if es_max else "<=", problema.objetivo[columna]))
    return ProblemaLineal(
        objetivo_dual,
        "min" if es_max else "max",
        restricciones_dual,
        [f"y{i + 1}" for i in range(len(objetivo_dual))],
    )


def resolver_con_dualidad(problema: ProblemaLineal):
    dual = construir_dual(problema)
    resultado_primal = resolver_simplex(problema)
    resultado_dual = resolver_simplex(dual)
    return dual, resultado_primal, resultado_dual
