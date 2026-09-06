import math
from typing import Sequence

import numpy as np

from modelos import PasoSimplex, ProblemaLineal, ResultadoSimplex, Restriccion


class ProblemaNoAcotado(Exception):
    pass


def _normalizar(restricciones: Sequence[Restriccion]):
    filas = []
    for restriccion in restricciones:
        coef = np.array(restriccion.coeficientes, dtype=float)
        relacion = restriccion.relacion
        rhs = float(restriccion.termino_independiente)
        if rhs < 0:
            coef *= -1
            rhs *= -1
            relacion = {"<=": ">=", ">=": "<=", "=": "="}[relacion]
        filas.append([coef, relacion, rhs])
    return filas


def _construir_tableau(problema: ProblemaLineal):
    filas = _normalizar(problema.restricciones)
    n = len(problema.objetivo)
    nombres = list(problema.nombres_variables)
    columnas = []
    for coef, relacion, rhs in filas:
        extras = []
        if relacion == "<=":
            extras = [(1.0, f"h{len(columnas) + 1}")]
        elif relacion == ">=":
            extras = [(-1.0, f"s{len(columnas) + 1}"), (1.0, f"a{len(columnas) + 1}")]
        elif relacion == "=":
            extras = [(1.0, f"a{len(columnas) + 1}")]
        columnas.extend((nombre, signo) for signo, nombre in extras)

    # Las columnas se generan por fila; se reconstruyen con nombres unicos.
    nombres_extra = []
    for indice, (_, relacion, _) in enumerate(filas, start=1):
        if relacion == "<=":
            nombres_extra.append(f"h{indice}")
        elif relacion == ">=":
            nombres_extra.extend([f"s{indice}", f"a{indice}"])
        else:
            nombres_extra.append(f"a{indice}")
    nombres_totales = nombres + nombres_extra
    A = np.zeros((len(filas), len(nombres_totales)))
    b = np.zeros(len(filas))
    base = []
    artificiales = []
    extra_pos = 0
    for i, (coef, relacion, rhs) in enumerate(filas):
        A[i, :n] = coef
        b[i] = rhs
        if relacion == "<=":
            A[i, n + extra_pos] = 1
            base.append(nombres_extra[extra_pos])
            extra_pos += 1
        elif relacion == ">=":
            A[i, n + extra_pos] = -1
            extra_pos += 1
            A[i, n + extra_pos] = 1
            base.append(nombres_extra[extra_pos])
            artificiales.append(n + extra_pos)
            extra_pos += 1
        else:
            A[i, n + extra_pos] = 1
            base.append(nombres_extra[extra_pos])
            artificiales.append(n + extra_pos)
            extra_pos += 1
    return A, b, nombres_totales, base, artificiales


def _tabla_inicial(A, b, c, base, nombres, fase, iteracion, razon=""):
    tabla = np.zeros((A.shape[0] + 1, A.shape[1] + 1))
    tabla[:-1, :-1] = A
    tabla[:-1, -1] = b
    costos_base = np.array([c[nombres.index(nombre)] for nombre in base])
    tabla[-1, :-1] = c - costos_base @ A
    tabla[-1, -1] = -costos_base @ b
    return tabla


def _guardar_paso(pasos, fase, iteracion, tabla, base, nombres, entra="", sale="", razon=""):
    pasos.append(PasoSimplex(fase, iteracion, nombres + ["LD"], tabla.tolist(), list(base), entra, sale, razon))


def resolver_simplex(problema: ProblemaLineal) -> ResultadoSimplex:
    """Resuelve un problema con variables no negativas mediante dos fases."""
    if problema.tipo not in {"max", "min"}:
        raise ValueError("El tipo de objetivo debe ser max o min.")
    A, b, nombres, base, artificiales = _construir_tableau(problema)
    pasos = []
    n_originales = len(problema.objetivo)
    c_original = np.zeros(len(nombres))
    c_original[:n_originales] = problema.objetivo
    if problema.tipo == "min":
        c_original *= -1

    def ejecutar_fase(tabla, costos, fase, iteracion=0):
        while True:
            _guardar_paso(pasos, fase, iteracion, tabla, base, nombres)
            reducidos = tabla[-1, :-1]
            candidatos = np.where(reducidos > 1e-9)[0]
            if not len(candidatos):
                return tabla, iteracion
            columna = int(candidatos[0])
            razones = []
            for fila in range(len(b)):
                valor = tabla[fila, columna]
                razones.append(tabla[fila, -1] / valor if valor > 1e-9 else math.inf)
            fila = int(np.argmin(razones))
            if razones[fila] == math.inf:
                raise ProblemaNoAcotado()
            entra, sale = nombres[columna], base[fila]
            pivote = tabla[fila, columna]
            tabla[fila] /= pivote
            for indice in range(tabla.shape[0]):
                if indice != fila:
                    tabla[indice] -= tabla[indice, columna] * tabla[fila]
            base[fila] = entra
            iteracion += 1
            _guardar_paso(pasos, fase, iteracion, tabla, base, nombres, entra, sale, "Pivote Gauss-Jordan")

    try:
        if artificiales:
            c_fase_1 = np.zeros(len(nombres))
            c_fase_1[artificiales] = -1
            tabla = _tabla_inicial(A, b, c_fase_1, base, nombres, "Fase I", 0)
            tabla, _ = ejecutar_fase(tabla, c_fase_1, "Fase I")
            if tabla[-1, -1] < -1e-7:
                return ResultadoSimplex("inviable", None, [], pasos, "El problema no tiene una solucion factible.")
            for indice in artificiales:
                if nombres[indice] in base:
                    fila = base.index(nombres[indice])
                    reemplazo = next((j for j in range(len(nombres)) if j not in artificiales and abs(tabla[fila, j]) > 1e-9), None)
                    if reemplazo is not None:
                        pivote = tabla[fila, reemplazo]
                        tabla[fila] /= pivote
                        for k in range(tabla.shape[0]):
                            if k != fila:
                                tabla[k] -= tabla[k, reemplazo] * tabla[fila]
                        base[fila] = nombres[reemplazo]
            conservar = [j for j in range(len(nombres)) if j not in artificiales]
            tabla = np.column_stack((tabla[:, conservar], tabla[:, -1]))
            nombres = [nombres[j] for j in conservar]
            c_original = c_original[conservar]
            tabla[-1] = 0
            costos_base = np.array([c_original[nombres.index(nombre)] for nombre in base])
            tabla[-1, :-1] = c_original - costos_base @ tabla[:-1, :-1]
            tabla[-1, -1] = -costos_base @ tabla[:-1, -1]
        else:
            tabla = _tabla_inicial(A, b, c_original, base, nombres, "Fase II", 0)
        tabla, _ = ejecutar_fase(tabla, c_original, "Fase II")
    except ProblemaNoAcotado:
        return ResultadoSimplex("no acotado", None, [], pasos, "El problema puede crecer indefinidamente.")

    solucion = np.zeros(len(nombres))
    for fila, nombre in enumerate(base):
        solucion[nombres.index(nombre)] = tabla[fila, -1]
    valor = float(-tabla[-1, -1] if problema.tipo == "max" else tabla[-1, -1])
    return ResultadoSimplex("optimo", valor, solucion[:n_originales].tolist(), pasos, "Solucion optima encontrada.")
