from dataclasses import dataclass
from math import isfinite


@dataclass
class PasoFlujo:
    titulo: str
    detalle: str
    estado: list[dict[str, float | int]] | None = None


@dataclass
class ResultadoFlujo:
    flujo: float
    costo_total: float
    flujos: list[dict[str, float | int]]
    pasos: list[PasoFlujo]
    mensaje: str


def _validar(nodos, origen, destino, aristas, flujo_requerido=None):
    if nodos < 2 or origen == destino or not 1 <= origen <= nodos or not 1 <= destino <= nodos:
        raise ValueError("Los nodos y los extremos origen/destino no son válidos.")
    if not aristas:
        raise ValueError("Debe existir al menos una arista.")
    if flujo_requerido is not None and (not isfinite(flujo_requerido) or flujo_requerido < 0):
        raise ValueError("El flujo requerido debe ser un número no negativo.")
    for arista in aristas:
        if not 1 <= arista["origen"] <= nodos or not 1 <= arista["destino"] <= nodos:
            raise ValueError("Cada arista debe apuntar a un nodo existente.")
        if arista["origen"] == arista["destino"] or arista["capacidad"] <= 0:
            raise ValueError("Las aristas deben conectar nodos distintos y tener capacidad positiva.")
        if not isfinite(arista["capacidad"]) or not isfinite(arista.get("costo", 0)):
            raise ValueError("Capacidad y costo deben ser números finitos.")


def _crear_red(nodos, aristas, con_costos):
    red = [[] for _ in range(nodos)]
    for indice, arista in enumerate(aristas):
        origen = arista["origen"] - 1
        destino = arista["destino"] - 1
        costo = arista.get("costo", 0) if con_costos else 0
        red[origen].append([destino, arista["capacidad"], costo, len(red[destino]), indice, True])
        red[destino].append([origen, 0.0, -costo, len(red[origen]) - 1, indice, False])
    return red


def _aumentar(red, nodo, indice, cantidad):
    arco = red[nodo][indice]
    arco[1] -= cantidad
    red[arco[0]][arco[3]][1] += cantidad


def _flujos_finales(red, aristas):
    flujos = []
    for indice, arista in enumerate(aristas):
        flujo = 0.0
        for origen in red:
            for arco in origen:
                if arco[4] == indice and arco[5]:
                    flujo = arista["capacidad"] - arco[1]
                    break
        flujos.append({
            "origen": arista["origen"],
            "destino": arista["destino"],
            "flujo": round(flujo, 10),
            "capacidad": arista["capacidad"],
            "costo": arista.get("costo", 0),
        })
    return flujos


def _estado_aristas(red, aristas):
    return _flujos_finales(red, aristas)


def _camino(padres, origen, destino):
    camino = [destino]
    actual = destino
    while actual != origen:
        actual, _ = padres[actual]
        camino.append(actual)
    return list(reversed(camino))


def resolver_flujo_maximo(nodos, origen, destino, aristas):
    _validar(nodos, origen, destino, aristas)
    red = _crear_red(nodos, aristas, False)
    s, t = origen - 1, destino - 1
    flujo = 0.0
    pasos = [PasoFlujo(
        "Inicio",
        "Se construye la red residual. BFS busca un camino aumentante y cada arista se representa como flujo/capacidad.",
        _estado_aristas(red, aristas),
    )]
    while True:
        padres = [None] * nodos
        padres[s] = (-1, -1)
        cola = [s]
        for actual in cola:
            for indice, arco in enumerate(red[actual]):
                if padres[arco[0]] is None and arco[1] > 1e-9:
                    padres[arco[0]] = (actual, indice)
                    cola.append(arco[0])
        if padres[t] is None:
            break
        camino = _camino(padres, s, t)
        aumento = float("inf")
        for anterior, siguiente in zip(camino, camino[1:]):
            indice = padres[siguiente][1]
            aumento = min(aumento, red[anterior][indice][1])
        actual = t
        while actual != s:
            anterior, indice = padres[actual]
            _aumentar(red, anterior, indice, aumento)
            actual = anterior
        flujo += aumento
        pasos.append(PasoFlujo(
            f"Aumento {len(pasos)}",
            f"Camino {' → '.join(str(nodo + 1) for nodo in camino)}: se aumentan {aumento:g} unidades. Flujo acumulado: {flujo:g}.",
            _estado_aristas(red, aristas),
        ))
    return ResultadoFlujo(
        flujo, 0.0, _flujos_finales(red, aristas),
        pasos + [PasoFlujo(
            "Flujo máximo",
            f"No quedan caminos aumentantes. El flujo máximo es {flujo:g}. El corte mínimo confirma la optimalidad.",
            _estado_aristas(red, aristas),
        )],
        "Se alcanzó el flujo máximo.",
    )


def resolver_flujo_costo_minimo(nodos, origen, destino, aristas, flujo_requerido):
    _validar(nodos, origen, destino, aristas, flujo_requerido)
    red = _crear_red(nodos, aristas, True)
    s, t = origen - 1, destino - 1
    flujo = costo_total = 0.0
    pasos = [PasoFlujo(
        "Inicio",
        f"Se construye la red residual para enviar {flujo_requerido:g} unidades al menor costo. Bellman-Ford permite usar aristas inversas.",
        _estado_aristas(red, aristas),
    )]
    while flujo < flujo_requerido - 1e-9:
        distancias = [float("inf")] * nodos
        padres = [None] * nodos
        distancias[s] = 0
        for _ in range(nodos - 1):
            cambio = False
            for actual in range(nodos):
                if distancias[actual] == float("inf"):
                    continue
                for indice, arco in enumerate(red[actual]):
                    if arco[1] > 1e-9 and distancias[actual] + arco[2] < distancias[arco[0]]:
                        distancias[arco[0]] = distancias[actual] + arco[2]
                        padres[arco[0]] = (actual, indice)
                        cambio = True
            if not cambio:
                break
        if padres[t] is None:
            raise ValueError("No existe capacidad suficiente para enviar el flujo requerido.")
        camino = _camino(padres, s, t)
        aumento = flujo_requerido - flujo
        costo_camino = 0.0
        for anterior, siguiente in zip(camino, camino[1:]):
            indice = padres[siguiente][1]
            arco = red[anterior][indice]
            aumento = min(aumento, arco[1])
            costo_camino += arco[2]
        actual = t
        while actual != s:
            anterior, indice = padres[actual]
            _aumentar(red, anterior, indice, aumento)
            actual = anterior
        flujo += aumento
        costo_total += aumento * costo_camino
        pasos.append(PasoFlujo(
            f"Aumento {len(pasos)}",
            f"Camino {' → '.join(str(nodo + 1) for nodo in camino)}: {aumento:g} unidades a costo unitario {costo_camino:g}. Flujo acumulado: {flujo:g}. Costo acumulado: {costo_total:g}.",
            _estado_aristas(red, aristas),
        ))
    return ResultadoFlujo(
        flujo, costo_total, _flujos_finales(red, aristas),
        pasos + [PasoFlujo(
            "Costo mínimo",
            f"Se satisfizo el flujo requerido. El costo total mínimo es {costo_total:g}. Cada camino seleccionado fue el de menor costo residual disponible.",
            _estado_aristas(red, aristas),
        )],
        "Se satisfizo el flujo requerido con costo mínimo.",
    )
