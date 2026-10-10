from itertools import permutations

from Backend.asignacion import resolver_asignacion


def costo_por_fuerza_bruta(costos):
    filas = len(costos)
    columnas = len(costos[0])
    return min(
        sum(costos[fila][columna] for fila, columna in enumerate(orden))
        for orden in permutations(range(columnas), filas)
    )


def test_kuhn_munkres_resuelve_matriz_cuadrada():
    costos = [[9, 2, 7], [6, 4, 3], [5, 8, 1]]

    resultado = resolver_asignacion(costos)

    assert resultado.costo_total == 9
    assert len(resultado.asignaciones) == 3
    assert any("Reducción por filas" in paso.titulo for paso in resultado.pasos)
    assert any("Ceros independientes" in paso.titulo for paso in resultado.pasos)


def test_kuhn_munkres_resuelve_matriz_rectangular():
    costos = [[4, 1, 3], [2, 0, 5]]

    resultado = resolver_asignacion(costos)

    assert resultado.costo_total == costo_por_fuerza_bruta(costos)
    assert len(resultado.asignaciones) == len(costos)
