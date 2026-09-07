from Backend.modelos import PasoSimplex, ProblemaLineal, Restriccion, ResultadoSimplex
from Backend.simplex import resolver_simplex


def construir_dual(problema: ProblemaLineal) -> ProblemaLineal:
    """Construye el dual conceptual para un primal con variables x >= 0."""
    es_max = problema.tipo == "max"
    objetivo_dual = [r.termino_independiente for r in problema.restricciones]
    restricciones_dual = []
    signos_dual = []
    for restriccion in problema.restricciones:
        if es_max:
            signos_dual.append({"<=": ">=0", ">=": "<=0", "=": "libre"}[restriccion.relacion])
        else:
            signos_dual.append({"<=": "<=0", ">=": ">=0", "=": "libre"}[restriccion.relacion])
    for columna in range(len(problema.objetivo)):
        coeficientes = [r.coeficientes[columna] for r in problema.restricciones]
        restricciones_dual.append(Restriccion(coeficientes, ">=" if es_max else "<=", problema.objetivo[columna]))
    return ProblemaLineal(
        objetivo_dual,
        "min" if es_max else "max",
        restricciones_dual,
        [f"y{i + 1}" for i in range(len(objetivo_dual))],
        signos_dual,
    )


def _dual_estandar(dual: ProblemaLineal):
    """Expresa variables duales negativas/libres mediante variables no negativas."""
    nombres = []
    mapeo_estandar = []
    objetivo = []
    for indice, signo in enumerate(dual.signos_variables or [">=0"] * len(dual.objetivo)):
        if signo == ">=0":
            nombres.append(f"u{indice + 1}")
            mapeo_estandar.append((indice, 1.0))
            objetivo.append(dual.objetivo[indice])
        elif signo == "<=0":
            nombres.append(f"u{indice + 1}")
            mapeo_estandar.append((indice, -1.0))
            objetivo.append(-dual.objetivo[indice])
        else:
            nombres.extend([f"u{indice + 1}p", f"u{indice + 1}n"])
            mapeo_estandar.extend([(indice, 1.0), (indice, -1.0)])
            objetivo.extend([dual.objetivo[indice], -dual.objetivo[indice]])

    relacion = dual.restricciones[0].relacion
    estandar = []
    for columna in range(len(dual.restricciones)):
        coeficientes = [
            dual.restricciones[columna].coeficientes[original] * factor
            for original, factor in mapeo_estandar
        ]
        estandar.append(Restriccion(coeficientes, relacion, dual.restricciones[columna].termino_independiente))
    return ProblemaLineal(objetivo, dual.tipo, estandar, nombres), mapeo_estandar


def _mapear_resultado(resultado: ResultadoSimplex, dual: ProblemaLineal, transformaciones, nombres_estandar):
    valores = []
    for original in range(len(dual.objetivo)):
        valores.append(sum(
            resultado.valores_variables[posicion] * factor
            for posicion, (indice, factor) in enumerate(transformaciones)
            if indice == original
        ))
    equivalencias = {}
    for nombre, (original, _) in zip(nombres_estandar, transformaciones):
        equivalencias[nombre] = dual.nombres_variables[original]

    pasos = []
    for paso in resultado.pasos:
        pasos.append(PasoSimplex(
            paso.fase,
            paso.iteracion,
            [equivalencias.get(nombre, nombre) for nombre in paso.encabezados],
            paso.tabla,
            [equivalencias.get(nombre, nombre) for nombre in paso.base],
            equivalencias.get(paso.entra, paso.entra),
            equivalencias.get(paso.sale, paso.sale),
            paso.razon,
        ))
    return ResultadoSimplex(resultado.estado, resultado.valor_objetivo, valores, pasos, resultado.mensaje)
def resolver_con_dualidad(problema: ProblemaLineal):
    dual = construir_dual(problema)
    resultado_primal = resolver_simplex(problema)
    dual_estandar, transformaciones = _dual_estandar(dual)
    resultado_dual = _mapear_resultado(
        resolver_simplex(dual_estandar), dual, transformaciones, dual_estandar.nombres_variables
    )
    return dual, resultado_primal, resultado_dual
