from dataclasses import dataclass
from itertools import combinations
from math import isfinite

from Backend.modelos import ProblemaLineal


TOLERANCIA = 1e-8


@dataclass
class VerticeGrafico:
    x: float
    y: float
    valor_objetivo: float


@dataclass
class ResultadoGrafico:
    estado: str
    valor_objetivo: float | None
    valores_variables: list[float]
    vertices: list[VerticeGrafico]
    mensaje: str


def _satisface(problema: ProblemaLineal, x: float, y: float) -> bool:
    if x < -TOLERANCIA or y < -TOLERANCIA:
        return False
    for restriccion in problema.restricciones:
        a, b = restriccion.coeficientes
        valor = a * x + b * y
        limite = restriccion.termino_independiente
        if restriccion.relacion == "<=" and valor > limite + TOLERANCIA:
            return False
        if restriccion.relacion == ">=" and valor < limite - TOLERANCIA:
            return False
        if restriccion.relacion == "=" and abs(valor - limite) > TOLERANCIA:
            return False
    return True


def _agregar_candidato(candidatos: list[tuple[float, float]], x: float, y: float) -> None:
    if not isfinite(x) or not isfinite(y):
        return
    if not any(abs(x - anterior_x) <= TOLERANCIA and abs(y - anterior_y) <= TOLERANCIA
               for anterior_x, anterior_y in candidatos):
        candidatos.append((max(0.0, x), max(0.0, y)))


def resolver_grafico(problema: ProblemaLineal) -> ResultadoGrafico:
    if len(problema.objetivo) != 2:
        raise ValueError("El método gráfico requiere exactamente dos variables.")

    candidatos: list[tuple[float, float]] = []
    _agregar_candidato(candidatos, 0.0, 0.0)

    lineas = [
        (restriccion.coeficientes[0], restriccion.coeficientes[1],
         restriccion.termino_independiente)
        for restriccion in problema.restricciones
    ]
    for a, b, limite in lineas:
        if abs(a) > TOLERANCIA:
            _agregar_candidato(candidatos, limite / a, 0.0)
        if abs(b) > TOLERANCIA:
            _agregar_candidato(candidatos, 0.0, limite / b)

    for primera, segunda in combinations(lineas, 2):
        a1, b1, c1 = primera
        a2, b2, c2 = segunda
        determinante = a1 * b2 - a2 * b1
        if abs(determinante) <= TOLERANCIA:
            continue
        _agregar_candidato(
            candidatos,
            (c1 * b2 - c2 * b1) / determinante,
            (a1 * c2 - a2 * c1) / determinante,
        )

    vertices = []
    for x, y in candidatos:
        if _satisface(problema, x, y):
            valor = problema.objetivo[0] * x + problema.objetivo[1] * y
            vertices.append(VerticeGrafico(x=x, y=y, valor_objetivo=valor))

    if not vertices:
        return ResultadoGrafico(
            estado="inviable",
            valor_objetivo=None,
            valores_variables=[],
            vertices=[],
            mensaje="No existe una región factible en el primer cuadrante.",
        )

    vertices.sort(key=lambda vertice: (vertice.x, vertice.y))
    if problema.tipo == "min":
        optimo = min(vertices, key=lambda vertice: vertice.valor_objetivo)
    else:
        optimo = max(vertices, key=lambda vertice: vertice.valor_objetivo)

    return ResultadoGrafico(
        estado="optimo",
        valor_objetivo=optimo.valor_objetivo,
        valores_variables=[optimo.x, optimo.y],
        vertices=vertices,
        mensaje="La solución óptima se encuentra en uno de los vértices de la región factible.",
    )
