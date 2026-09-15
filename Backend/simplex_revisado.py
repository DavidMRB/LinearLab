import numpy as np

from Backend.modelos import PasoSimplex, ProblemaLineal, ResultadoSimplex
from Backend.simplex import _construir_tableau


TOLERANCIA = 1e-9
MAX_ITERACIONES = 1000


class ProblemaNoAcotadoRevisado(Exception):
    pass


class BaseInvalidaRevisado(Exception):
    pass


def _guardar_paso(pasos, fase, iteracion, A, b, costos, base, nombres, entra="", sale="", razon="", entra_indice=None):
    try:
        base_matrix = np.linalg.solve(A[:, base], np.eye(len(base)))
    except np.linalg.LinAlgError as error:
        raise BaseInvalidaRevisado() from error
    costos_base = costos[base]
    y = costos_base @ base_matrix
    x_basicas = base_matrix @ b
    costos_reducidos = costos - y @ A

    # La tabla completa se conserva solo como equivalencia con el metodo por
    # tablas (para comparar resultados); el metodo revisado en si nunca la
    # arma: opera con B^-1, y = c_B B^-1 y, a lo sumo, la columna entrante.
    tabla = np.zeros((A.shape[0] + 1, A.shape[1] + 1))
    tabla[:-1, :-1] = base_matrix @ A
    tabla[:-1, -1] = x_basicas
    tabla[-1, :-1] = costos_reducidos
    tabla[-1, -1] = -costos_base @ x_basicas

    columna_pivote = (base_matrix @ A[:, entra_indice]).tolist() if entra_indice is not None else None

    pasos.append(PasoSimplex(
        fase,
        iteracion,
        nombres + ["LD"],
        tabla.tolist(),
        [nombres[i] for i in base],
        entra,
        sale,
        razon,
        base_inversa=base_matrix.tolist(),
        cb=costos_base.tolist(),
        y=y.tolist(),
        xb=x_basicas.tolist(),
        costos_reducidos=costos_reducidos.tolist(),
        columna_pivote=columna_pivote,
    ))


def _resolver_fase(A, b, costos, base, nombres, fase, pasos, iteracion=0):
    while True:
        try:
            base_matrix = np.linalg.solve(A[:, base], np.eye(len(base)))
        except np.linalg.LinAlgError as error:
            raise BaseInvalidaRevisado() from error
        x_basicas = base_matrix @ b
        costos_reducidos = costos - costos[base] @ base_matrix @ A
        candidatos = [indice for indice, costo in enumerate(costos_reducidos) if costo > TOLERANCIA and indice not in base]
        if not candidatos:
            _guardar_paso(pasos, fase, iteracion, A, b, costos, base, nombres)
            return x_basicas, iteracion

        entra_indice = candidatos[0]
        direccion = base_matrix @ A[:, entra_indice]
        razones = [
            x_basicas[fila] / direccion[fila]
            if direccion[fila] > TOLERANCIA and x_basicas[fila] >= -TOLERANCIA
            else np.inf
            for fila in range(len(base))
        ]
        if all(np.isinf(razon) for razon in razones):
            raise ProblemaNoAcotadoRevisado()
        menor_razon = min(razones)
        filas = [fila for fila, razon in enumerate(razones) if abs(razon - menor_razon) <= TOLERANCIA]
        fila_salida = min(filas, key=lambda fila: base[fila])
        sale_indice = base[fila_salida]
        _guardar_paso(
            pasos,
            fase,
            iteracion,
            A,
            b,
            costos,
            base,
            nombres,
            nombres[entra_indice],
            nombres[sale_indice],
            "Pivote con B^-1 y prueba de razon minima",
            entra_indice=entra_indice,
        )
        base[fila_salida] = entra_indice
        iteracion += 1
        if iteracion > MAX_ITERACIONES:
            raise BaseInvalidaRevisado()


def _quitar_artificiales(A, b, base, nombres, artificiales, pasos, costos):
    while True:
        posiciones = [fila for fila, indice in enumerate(base) if indice in artificiales]
        if not posiciones:
            break
        try:
            base_matrix = np.linalg.solve(A[:, base], np.eye(len(base)))
        except np.linalg.LinAlgError as error:
            raise BaseInvalidaRevisado()
        fila = posiciones[0]
        transformada = base_matrix @ A
        candidatos = [
            indice for indice in range(A.shape[1])
            if indice not in artificiales and indice not in base and abs(transformada[fila, indice]) > TOLERANCIA
        ]
        if candidatos:
            sale = base[fila]
            entra = candidatos[0]
            _guardar_paso(pasos, "Fase I", len(pasos), A, b, costos, base, nombres, nombres[entra], nombres[sale], "Se expulsa una artificial de la base", entra_indice=entra)
            base[fila] = entra
        elif abs((base_matrix @ b)[fila]) <= TOLERANCIA:
            A = np.delete(A, fila, axis=0)
            b = np.delete(b, fila)
            base.pop(fila)
        else:
            raise BaseInvalidaRevisado()
    conservar = [indice for indice in range(A.shape[1]) if indice not in artificiales]
    remapeo = {indice: posicion for posicion, indice in enumerate(conservar)}
    A = A[:, conservar]
    nombres = [nombres[indice] for indice in conservar]
    base = [remapeo[indice] for indice in base]
    return A, b, base, nombres


def resolver_simplex_revisado(problema: ProblemaLineal) -> ResultadoSimplex:
    """Resuelve un problema lineal usando el algoritmo simplex revisado."""
    if problema.tipo not in {"max", "min"}:
        raise ValueError("El tipo de objetivo debe ser max o min.")
    A, b, nombres, base_nombres, artificiales = _construir_tableau(problema)
    base = [nombres.index(nombre) for nombre in base_nombres]
    pasos = []
    originales = len(problema.objetivo)
    costos = np.zeros(len(nombres))
    costos[:originales] = problema.objetivo
    if problema.tipo == "min":
        costos *= -1

    try:
        if artificiales:
            costos_fase_1 = np.zeros(len(nombres))
            costos_fase_1[artificiales] = -1
            x_basicas, _ = _resolver_fase(A, b, costos_fase_1, base, nombres, "Fase I", pasos)
            if float(costos_fase_1[base] @ x_basicas) < -1e-7:
                return ResultadoSimplex("inviable", None, [], pasos, "El problema no tiene una solucion factible.")
            A, b, base, nombres = _quitar_artificiales(A, b, base, nombres, artificiales, pasos, costos_fase_1)
            costos = np.delete(costos, artificiales)
        x_basicas, _ = _resolver_fase(A, b, costos, base, nombres, "Fase II", pasos)
    except ProblemaNoAcotadoRevisado:
        return ResultadoSimplex("no acotado", None, [], pasos, "El problema puede crecer indefinidamente.")
    except BaseInvalidaRevisado:
        return ResultadoSimplex("error", None, [], pasos, "No fue posible construir una base valida para el problema.")

    solucion = np.zeros(len(nombres))
    solucion[base] = x_basicas
    valor = float(costos @ solucion)
    if problema.tipo == "min":
        valor *= -1
    return ResultadoSimplex("optimo", valor, solucion[:originales].tolist(), pasos, "Solucion optima encontrada con simplex revisado.")