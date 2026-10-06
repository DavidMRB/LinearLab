from dataclasses import dataclass


@dataclass
class PasoTransporte:
    titulo: str
    detalle: str


@dataclass
class SolucionTransporte:
    nombre: str
    asignaciones: list[list[float]]
    costo_total: float
    pasos: list[PasoTransporte]


@dataclass
class ResultadoTransporte:
    oferta: list[float]
    demanda: list[float]
    costos: list[list[float]]
    soluciones: list[SolucionTransporte]
    mensaje: str


def _validar_matriz(costos: list[list[float]], oferta: list[float], demanda: list[float]) -> None:
    if not costos or not costos[0]:
        raise ValueError("La matriz de costos no puede estar vacía.")
    if len(costos) != len(oferta) or any(len(fila) != len(demanda) for fila in costos):
        raise ValueError("Las dimensiones de costos, oferta y demanda no coinciden.")
    if any(valor < 0 for fila in costos for valor in fila):
        raise ValueError("Los costos no pueden ser negativos.")
    if any(valor < 0 for valor in oferta + demanda):
        raise ValueError("La oferta y la demanda no pueden ser negativas.")


def _normalizar(costos: list[list[float]], oferta: list[float], demanda: list[float]):
    costos = [fila[:] for fila in costos]
    oferta = oferta[:]
    demanda = demanda[:]
    total_oferta = sum(oferta)
    total_demanda = sum(demanda)
    ajuste = None
    if total_oferta < total_demanda:
        oferta.append(total_demanda - total_oferta)
        costos.append([0.0] * len(demanda))
        ajuste = "Se agregó un origen ficticio con costo 0 para cubrir la demanda restante."
    elif total_demanda < total_oferta:
        demanda.append(total_oferta - total_demanda)
        for fila in costos:
            fila.append(0.0)
        ajuste = "Se agregó un destino ficticio con costo 0 para absorber la oferta restante."
    return costos, oferta, demanda, ajuste


def _matriz_vacia(filas: int, columnas: int) -> list[list[float]]:
    return [[0.0 for _ in range(columnas)] for _ in range(filas)]


def _detalle_asignacion(origen: int, destino: int, cantidad: float, costo: float) -> str:
    return f"Asignar {cantidad:g} unidades en O{origen + 1}-D{destino + 1} (costo unitario {costo:g})."


def _costo_total(asignaciones: list[list[float]], costos: list[list[float]]) -> float:
    return sum(asignaciones[i][j] * costos[i][j] for i in range(len(costos)) for j in range(len(costos[0])))


def _solucion_noroeste(costos, oferta, demanda) -> SolucionTransporte:
    restantes_oferta = oferta[:]
    restantes_demanda = demanda[:]
    asignaciones = _matriz_vacia(len(oferta), len(demanda))
    pasos = [PasoTransporte("Inicio: esquina noroeste", "Se comienza en la celda O1-D1 y se avanza cuando se agota una oferta o demanda.")]
    i = j = 0
    while i < len(oferta) and j < len(demanda):
        cantidad = min(restantes_oferta[i], restantes_demanda[j])
        asignaciones[i][j] = cantidad
        pasos.append(PasoTransporte(f"Asignación {len(pasos)}", _detalle_asignacion(i, j, cantidad, costos[i][j])))
        restantes_oferta[i] -= cantidad
        restantes_demanda[j] -= cantidad
        if restantes_oferta[i] <= 1e-9:
            i += 1
        if restantes_demanda[j] <= 1e-9:
            j += 1
    return SolucionTransporte("Esquina noroeste", asignaciones, _costo_total(asignaciones, costos), pasos)


def _solucion_costo_minimo(costos, oferta, demanda) -> SolucionTransporte:
    restantes_oferta = oferta[:]
    restantes_demanda = demanda[:]
    asignaciones = _matriz_vacia(len(oferta), len(demanda))
    disponibles = {(i, j) for i in range(len(oferta)) for j in range(len(demanda))}
    pasos = [PasoTransporte("Inicio: costo mínimo", "En cada iteración se selecciona la celda disponible con menor costo unitario.")]
    while disponibles:
        i, j = min(disponibles, key=lambda celda: (costos[celda[0]][celda[1]], celda[0], celda[1]))
        cantidad = min(restantes_oferta[i], restantes_demanda[j])
        asignaciones[i][j] = cantidad
        pasos.append(PasoTransporte(f"Asignación {len(pasos)}", _detalle_asignacion(i, j, cantidad, costos[i][j])))
        restantes_oferta[i] -= cantidad
        restantes_demanda[j] -= cantidad
        if restantes_oferta[i] <= 1e-9:
            disponibles = {celda for celda in disponibles if celda[0] != i}
        if restantes_demanda[j] <= 1e-9:
            disponibles = {celda for celda in disponibles if celda[1] != j}
    return SolucionTransporte("Costo mínimo", asignaciones, _costo_total(asignaciones, costos), pasos)


def _penalidad(valores: list[float]) -> float:
    ordenados = sorted(valores)
    return ordenados[1] - ordenados[0] if len(ordenados) > 1 else ordenados[0]


def _solucion_vogel(costos, oferta, demanda) -> SolucionTransporte:
    restantes_oferta = oferta[:]
    restantes_demanda = demanda[:]
    asignaciones = _matriz_vacia(len(oferta), len(demanda))
    filas = set(range(len(oferta)))
    columnas = set(range(len(demanda)))
    pasos = [PasoTransporte("Inicio: aproximación de Vogel", "Se calculan penalizaciones como la diferencia entre los dos costos menores de cada fila y columna.")]
    while filas and columnas:
        penalidades_filas = {
            i: _penalidad([costos[i][j] for j in columnas]) for i in filas
        }
        penalidades_columnas = {
            j: _penalidad([costos[i][j] for i in filas]) for j in columnas
        }
        tipo, indice, penalidad = max(
            [("fila", i, valor) for i, valor in penalidades_filas.items()]
            + [("columna", j, valor) for j, valor in penalidades_columnas.items()],
            key=lambda item: (item[2], item[0] == "columna", -item[1]),
        )
        if tipo == "fila":
            i = indice
            j = min(columnas, key=lambda columna: (costos[i][columna], columna))
        else:
            j = indice
            i = min(filas, key=lambda fila: (costos[fila][j], fila))
        cantidad = min(restantes_oferta[i], restantes_demanda[j])
        asignaciones[i][j] = cantidad
        pasos.append(PasoTransporte(
            f"Asignación {len(pasos)}",
            f"Penalidad seleccionada: {penalidad:g}. " + _detalle_asignacion(i, j, cantidad, costos[i][j]),
        ))
        restantes_oferta[i] -= cantidad
        restantes_demanda[j] -= cantidad
        if restantes_oferta[i] <= 1e-9:
            filas.remove(i)
        if restantes_demanda[j] <= 1e-9:
            columnas.remove(j)
    return SolucionTransporte("Vogel", asignaciones, _costo_total(asignaciones, costos), pasos)


def resolver_transporte(costos: list[list[float]], oferta: list[float], demanda: list[float]) -> ResultadoTransporte:
    _validar_matriz(costos, oferta, demanda)
    costos, oferta, demanda, ajuste = _normalizar(costos, oferta, demanda)
    soluciones = [
        _solucion_noroeste(costos, oferta, demanda),
        _solucion_costo_minimo(costos, oferta, demanda),
        _solucion_vogel(costos, oferta, demanda),
    ]
    mensaje = ajuste or "El problema está balanceado: la oferta total es igual a la demanda total."
    return ResultadoTransporte(oferta, demanda, costos, soluciones, mensaje)
