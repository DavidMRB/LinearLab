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
class PasoGrafico:
    titulo: str
    detalle: str


@dataclass
class ResultadoGrafico:
    estado: str
    valor_objetivo: float | None
    valores_variables: list[float]
    vertices: list[VerticeGrafico]
    pasos: list[PasoGrafico]
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
    # Un punto fuera del primer cuadrante no puede ser vertice de la region factible.
    if x < -TOLERANCIA or y < -TOLERANCIA:
        return
    x, y = max(0.0, x), max(0.0, y)
    if not any(abs(x - anterior_x) <= TOLERANCIA and abs(y - anterior_y) <= TOLERANCIA
               for anterior_x, anterior_y in candidatos):
        candidatos.append((x, y))


def _numero(valor: float) -> str:
    return f"{valor:.4f}".rstrip("0").rstrip(".")


def _ecuacion(a: float, b: float, relacion: str, limite: float) -> str:
    return f"{_numero(a)}x1 + {_numero(b)}x2 {relacion} {_numero(limite)}"


def _mejora_sin_limite(problema: ProblemaLineal) -> bool:
    """True si existe una direccion de la region factible que mejora Z sin limite."""
    direcciones = [(1.0, 0.0), (0.0, 1.0)]
    for restriccion in problema.restricciones:
        a, b = restriccion.coeficientes
        direcciones.extend([(b, -a), (-b, a)])
    c1, c2 = problema.objetivo
    signo = 1 if problema.tipo == "max" else -1
    for dx, dy in direcciones:
        if dx < -TOLERANCIA or dy < -TOLERANCIA or (abs(dx) <= TOLERANCIA and abs(dy) <= TOLERANCIA):
            continue
        if signo * (c1 * dx + c2 * dy) <= TOLERANCIA:
            continue
        en_cono = True
        for restriccion in problema.restricciones:
            a, b = restriccion.coeficientes
            avance = a * dx + b * dy
            if restriccion.relacion == "<=" and avance > TOLERANCIA:
                en_cono = False
            elif restriccion.relacion == ">=" and avance < -TOLERANCIA:
                en_cono = False
            elif restriccion.relacion == "=" and abs(avance) > TOLERANCIA:
                en_cono = False
        if en_cono:
            return True
    return False


def resolver_grafico(problema: ProblemaLineal) -> ResultadoGrafico:
    if len(problema.objetivo) != 2:
        raise ValueError("El método gráfico requiere exactamente dos variables.")

    candidatos: list[tuple[float, float]] = []
    pasos: list[PasoGrafico] = [
        PasoGrafico(
            titulo="1. Identificar el modelo",
            detalle=(
                f"Se trabaja con dos variables no negativas: x1 >= 0 y x2 >= 0. "
                f"La función objetivo es {_numero(problema.objetivo[0])}x1 + "
                f"{_numero(problema.objetivo[1])}x2."
            ),
        )
    ]
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
    ejes = []
    for indice, (a, b, limite) in enumerate(lineas, start=1):
        intersecciones = []
        if abs(a) > TOLERANCIA:
            intersecciones.append(f"con x2=0: ({_numero(limite / a)}, 0)")
        if abs(b) > TOLERANCIA:
            intersecciones.append(f"con x1=0: (0, {_numero(limite / b)})")
        ejes.append(f"R{indice}: {_ecuacion(a, b, problema.restricciones[indice - 1].relacion, limite)}; "
                    + (", ".join(intersecciones) or "no corta los ejes"))
    pasos.append(PasoGrafico(
        titulo="2. Calcular intersecciones con los ejes",
        detalle="\n".join(ejes),
    ))

    intersecciones = []
    for (indice_primera, primera), (indice_segunda, segunda) in combinations(enumerate(lineas), 2):
        a1, b1, c1 = primera
        a2, b2, c2 = segunda
        determinante = a1 * b2 - a2 * b1
        if abs(determinante) <= TOLERANCIA:
            continue
        x = (c1 * b2 - c2 * b1) / determinante
        y = (a1 * c2 - a2 * c1) / determinante
        intersecciones.append(
            f"R{indice_primera + 1} interseccion R{indice_segunda + 1}: "
            f"({_numero(x)}, {_numero(y)})"
        )
        _agregar_candidato(
            candidatos,
            x,
            y,
        )
    pasos.append(PasoGrafico(
        titulo="3. Calcular intersecciones entre restricciones",
        detalle="\n".join(intersecciones) if intersecciones else "No hay intersecciones entre restricciones no paralelas.",
    ))

    vertices = []
    verificaciones = []
    for x, y in candidatos:
        if _satisface(problema, x, y):
            valor = problema.objetivo[0] * x + problema.objetivo[1] * y
            vertices.append(VerticeGrafico(x=x, y=y, valor_objetivo=valor))
            verificaciones.append(f"({_numero(x)}, {_numero(y)}): factible")
        else:
            verificaciones.append(f"({_numero(x)}, {_numero(y)}): no factible")
    pasos.append(PasoGrafico(
        titulo="4. Verificar la región factible",
        detalle="\n".join(verificaciones) if verificaciones else "No se encontraron puntos candidatos.",
    ))

    if not vertices:
        return ResultadoGrafico(
            estado="inviable",
            valor_objetivo=None,
            valores_variables=[],
            vertices=[],
            pasos=pasos,
            mensaje="No existe una región factible en el primer cuadrante.",
        )

    vertices.sort(key=lambda vertice: (vertice.x, vertice.y))
    if _mejora_sin_limite(problema):
        pasos.append(PasoGrafico(
            titulo="5. Región no acotada",
            detalle="La región factible es no acotada en una dirección que mejora la función objetivo: Z puede mejorar indefinidamente.",
        ))
        return ResultadoGrafico(
            estado="no acotado",
            valor_objetivo=None,
            valores_variables=[],
            vertices=vertices,
            pasos=pasos,
            mensaje="El problema es no acotado: la función objetivo mejora indefinidamente.",
        )
    if problema.tipo == "min":
        optimo = min(vertices, key=lambda vertice: vertice.valor_objetivo)
    else:
        optimo = max(vertices, key=lambda vertice: vertice.valor_objetivo)

    evaluaciones = [
        f"Z({_numero(vertice.x)}, {_numero(vertice.y)}) = {_numero(vertice.valor_objetivo)}"
        for vertice in vertices
    ]
    pasos.append(PasoGrafico(
        titulo="5. Evaluar la función objetivo en los vértices",
        detalle="\n".join(evaluaciones),
    ))
    pasos.append(PasoGrafico(
        titulo="6. Seleccionar el óptimo",
        detalle=(
            f"Se elige el valor {'mínimo' if problema.tipo == 'min' else 'máximo'}: "
            f"Z = {_numero(optimo.valor_objetivo)} en "
            f"({_numero(optimo.x)}, {_numero(optimo.y)})."
        ),
    ))

    return ResultadoGrafico(
        estado="optimo",
        valor_objetivo=optimo.valor_objetivo,
        valores_variables=[optimo.x, optimo.y],
        vertices=vertices,
        pasos=pasos,
        mensaje="La solución óptima se encuentra en uno de los vértices de la región factible.",
    )
