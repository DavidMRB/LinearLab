from Backend.modelos import ProblemaLineal, Restriccion
from Backend.simplex_revisado import resolver_simplex_revisado


def test_simplex_revisado_elige_la_variable_con_mayor_costo_reducido():
    problema = ProblemaLineal(
        objetivo=[2, 3],
        tipo="max",
        restricciones=[
            Restriccion([1, 2], "<=", 6),
            Restriccion([2, 1], "<=", 8),
        ],
        nombres_variables=["x1", "x2"],
    )

    resultado = resolver_simplex_revisado(problema)

    assert resultado.estado == "optimo"
    assert resultado.valor_objetivo is not None
    assert abs(resultado.valor_objetivo - 10.666666666666666) < 1e-9
    assert abs(resultado.valores_variables[0] - 3.3333333333333335) < 1e-9
    assert abs(resultado.valores_variables[1] - 1.3333333333333333) < 1e-9
    assert resultado.pasos[0].entra == "x2"
    assert resultado.pasos[0].sale == "h1"
