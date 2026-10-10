from dataclasses import dataclass
from math import isfinite


@dataclass
class PasoAsignacion:
    titulo: str
    detalle: str
    matriz: list[list[float]] | None = None
    asignaciones: list[tuple[int, int]] | None = None


@dataclass
class ResultadoAsignacion:
    costos: list[list[float]]
    asignaciones: list[dict[str, int | float]]
    costo_total: float
    pasos: list[PasoAsignacion]


def _validar(costos: list[list[float]]) -> None:
    if not costos or not costos[0]:
        raise ValueError("La matriz de costos no puede estar vacía.")
    columnas = len(costos[0])
    if any(len(fila) != columnas for fila in costos):
        raise ValueError("Todas las filas deben tener la misma cantidad de costos.")
    if any(not isfinite(valor) for fila in costos for valor in fila):
        raise ValueError("Todos los costos deben ser números finitos.")
    if any(valor < 0 for fila in costos for valor in fila):
        raise ValueError("Los costos no pueden ser negativos.")


def _reducir_filas(matriz: list[list[float]]) -> list[list[float]]:
    return [[valor - min(fila) for valor in fila] for fila in matriz]


def _reducir_columnas(matriz: list[list[float]]) -> list[list[float]]:
    minimos = [min(fila[columna] for fila in matriz) for columna in range(len(matriz))]
    return [[valor - minimos[columna] for columna, valor in enumerate(fila)] for fila in matriz]


def _emparejar_ceros(matriz: list[list[float]]) -> list[tuple[int, int]]:
    emparejadas: dict[int, int] = {}

    def buscar(fila: int, visitadas: set[int]) -> bool:
        for columna, valor in enumerate(matriz[fila]):
            if abs(valor) > 1e-9 or columna in visitadas:
                continue
            visitadas.add(columna)
            if columna not in emparejadas or buscar(emparejadas[columna], visitadas):
                emparejadas[columna] = fila
                return True
        return False

    for fila in range(len(matriz)):
        buscar(fila, set())
    return sorted((fila, columna) for columna, fila in emparejadas.items())


def _cubrir_ceros(matriz: list[list[float]], emparejamientos: list[tuple[int, int]]) -> tuple[set[int], set[int]]:
    filas_visibles = set(range(len(matriz))) - {fila for fila, _ in emparejamientos}
    columnas_visibles: set[int] = set()
    cambio = True
    while cambio:
        cambio = False
        for fila in list(filas_visibles):
            for columna, valor in enumerate(matriz[fila]):
                if abs(valor) <= 1e-9 and columna not in columnas_visibles:
                    columnas_visibles.add(columna)
                    cambio = True
        for fila, columna in emparejamientos:
            if columna in columnas_visibles and fila not in filas_visibles:
                filas_visibles.add(fila)
                cambio = True
    return set(range(len(matriz))) - filas_visibles, columnas_visibles


def _ajustar_matriz(matriz: list[list[float]], filas_cubiertas: set[int], columnas_cubiertas: set[int]) -> tuple[list[list[float]], float]:
    no_cubiertos = [
        matriz[fila][columna]
        for fila in range(len(matriz))
        if fila not in filas_cubiertas
        for columna in range(len(matriz))
        if columna not in columnas_cubiertas
    ]
    minimo = min(no_cubiertos)
    return [
        [
            valor + minimo if fila in filas_cubiertas and columna in columnas_cubiertas
            else valor - minimo if fila not in filas_cubiertas and columna not in columnas_cubiertas
            else valor
            for columna, valor in enumerate(fila_valores)
        ]
        for fila, fila_valores in enumerate(matriz)
    ], minimo


def _normalizar_matriz(costos: list[list[float]]) -> tuple[list[list[float]], int, int]:
    filas, columnas = len(costos), len(costos[0])
    dimension = max(filas, columnas)
    matriz = [fila + [0.0] * (dimension - columnas) for fila in costos]
    matriz.extend([[0.0] * dimension for _ in range(dimension - filas)])
    return matriz, filas, columnas


def _texto_cobertura(filas: set[int], columnas: set[int]) -> str:
    partes = []
    if filas:
        partes.append(f"filas {', '.join(str(fila + 1) for fila in sorted(filas))}")
    if columnas:
        partes.append(f"columnas {', '.join(str(columna + 1) for columna in sorted(columnas))}")
    return " y ".join(partes)


def _resolver_kuhn_munkres(costos: list[list[float]]) -> tuple[list[tuple[int, int]], list[PasoAsignacion]]:
    matriz, filas_originales, columnas_originales = _normalizar_matriz(costos)
    pasos: list[PasoAsignacion] = []
    if len(costos) != len(costos[0]):
        pasos.append(PasoAsignacion(
            "1. Matriz cuadrada",
            f"Se agregan elementos ficticios con costo 0 para trabajar con una matriz {len(matriz)} x {len(matriz)}.",
            matriz,
        ))
    matriz = _reducir_filas(matriz)
    pasos.append(PasoAsignacion(
        "2. Reducción por filas",
        "Se resta el menor valor de cada fila para crear al menos un cero en cada fila.",
        matriz,
    ))
    matriz = _reducir_columnas(matriz)
    pasos.append(PasoAsignacion(
        "3. Reducción por columnas",
        "Se resta el menor valor de cada columna para crear ceros independientes potenciales.",
        matriz,
    ))
    iteracion = 1
    while True:
        emparejamientos = _emparejar_ceros(matriz)
        if len(emparejamientos) == len(matriz):
            pasos.append(PasoAsignacion(
                f"4.{iteracion} Ceros independientes",
                f"Se seleccionan {len(emparejamientos)} ceros independientes, uno por fila y columna. "
                "Como el número de líneas coincide con la dimensión, la solución es óptima.",
                matriz,
                emparejamientos,
            ))
            return [
                (fila, columna) for fila, columna in emparejamientos
                if fila < filas_originales and columna < columnas_originales
            ], pasos
        filas_cubiertas, columnas_cubiertas = _cubrir_ceros(matriz, emparejamientos)
        matriz, minimo = _ajustar_matriz(matriz, filas_cubiertas, columnas_cubiertas)
        pasos.append(PasoAsignacion(
            f"4.{iteracion} Cubrir y ajustar ceros",
            f"Se cubren todos los ceros con {len(filas_cubiertas) + len(columnas_cubiertas)} líneas "
            f"({_texto_cobertura(filas_cubiertas, columnas_cubiertas)}). "
            f"El menor valor no cubierto es {minimo:g}: se resta a las celdas no cubiertas "
            "y se suma en las intersecciones de líneas.",
            matriz,
        ))
        iteracion += 1


def resolver_asignacion(costos: list[list[float]]) -> ResultadoAsignacion:
    _validar(costos)
    pares, pasos = _resolver_kuhn_munkres(costos)
    asignaciones = [
        {"fila": fila, "columna": columna, "costo": costos[fila][columna]}
        for fila, columna in sorted(pares)
    ]
    for indice, asignacion in enumerate(asignaciones, 1):
        pasos.append(PasoAsignacion(
            f"5.{indice} Asignación definitiva",
            f"Trabajador {asignacion['fila'] + 1} se asigna a Tarea {asignacion['columna'] + 1} "
            f"con costo {asignacion['costo']:g}.",
        ))
    costo_total = sum(asignacion["costo"] for asignacion in asignaciones)
    pasos.append(PasoAsignacion("6. Costo mínimo", f"Se suman los costos seleccionados: {costo_total:g}."))
    return ResultadoAsignacion(costos, asignaciones, costo_total, pasos)
