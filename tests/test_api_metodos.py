"""Pruebas de la API por método, con ejercicios de libro y casos límite."""
import pytest
from fastapi.testclient import TestClient

from Backend.api.main import app

cliente = TestClient(app)


def modelo(objetivo, tipo, restricciones):
    return {
        "objetivo": objetivo,
        "tipo": tipo,
        "restricciones": [
            {"coeficientes": a, "relacion": rel, "termino_independiente": b}
            for a, rel, b in restricciones
        ],
    }


WYNDOR = modelo([3, 5], "max", [([1, 0], "<=", 4), ([0, 2], "<=", 12), ([3, 2], "<=", 18)])
DIETA = modelo([2, 3], "min", [([1, 1], ">=", 4), ([1, 3], ">=", 6)])
INVIABLE = modelo([1, 1], "max", [([1, 1], "<=", 2), ([1, 1], ">=", 5)])
NO_ACOTADO = modelo([1, 1], "max", [([1, -1], "<=", 2)])
REDUNDANTE = modelo([1, 1], "max", [([1, 1], "=", 4), ([2, 2], "=", 8), ([1, 0], "<=", 3)])
# Ejemplo de Beale: cicla con la regla de Dantzig pura.
BEALE = modelo(
    [0.75, -150, 0.02, -6], "max",
    [([0.25, -60, -0.04, 9], "<=", 0), ([0.5, -90, -0.02, 3], "<=", 0), ([0, 0, 1, 0], "<=", 1)],
)


def post(url, cuerpo):
    return cliente.post(url, json=cuerpo)


@pytest.mark.parametrize("url", ["/api/simplex/resolver", "/api/simplex-revisado/resolver", "/api/grafico/resolver"])
def test_wyndor_optimo(url):
    datos = post(url, WYNDOR).json()
    assert datos["estado"] == "optimo"
    assert datos["valor_objetivo"] == pytest.approx(36)
    assert datos["valores_variables"] == pytest.approx([2, 6])


@pytest.mark.parametrize("url", ["/api/simplex/resolver", "/api/simplex-revisado/resolver", "/api/grafico/resolver"])
def test_minimizacion_con_mayor_o_igual(url):
    datos = post(url, DIETA).json()
    assert datos["valor_objetivo"] == pytest.approx(9)
    assert datos["valores_variables"] == pytest.approx([3, 1])


def test_simplex_tabular_usa_regla_de_dantzig_como_el_revisado():
    tabular = post("/api/simplex/resolver", WYNDOR).json()["pasos"]
    revisado = post("/api/simplex-revisado/resolver", WYNDOR).json()["pasos"]
    assert tabular[1]["entra"] == "x2"  # mayor costo reducido (5 > 3)
    assert len(tabular) == 3 and len(revisado) == 3


@pytest.mark.parametrize("url", ["/api/simplex/resolver", "/api/simplex-revisado/resolver", "/api/grafico/resolver"])
def test_problema_inviable(url):
    datos = post(url, INVIABLE).json()
    assert datos["estado"] == "inviable"
    assert datos["valor_objetivo"] is None


@pytest.mark.parametrize("url", ["/api/simplex/resolver", "/api/simplex-revisado/resolver", "/api/grafico/resolver"])
def test_problema_no_acotado(url):
    assert post(url, NO_ACOTADO).json()["estado"] == "no acotado"


@pytest.mark.parametrize("url", ["/api/simplex/resolver", "/api/simplex-revisado/resolver"])
def test_restriccion_de_igualdad_redundante(url):
    datos = post(url, REDUNDANTE)
    assert datos.status_code == 200
    assert datos.json()["valor_objetivo"] == pytest.approx(4)


@pytest.mark.parametrize("url", ["/api/simplex/resolver", "/api/simplex-revisado/resolver"])
def test_ciclado_de_beale_termina(url):
    datos = post(url, BEALE).json()
    assert datos["estado"] == "optimo"
    assert datos["valor_objetivo"] == pytest.approx(0.05)


def test_grafico_sin_vertices_duplicados_ni_fuera_del_cuadrante():
    vertices = post("/api/grafico/resolver", NO_ACOTADO).json()["vertices"]
    puntos = [(v["x"], v["y"]) for v in vertices]
    assert len(puntos) == len(set(puntos))
    assert all(x >= 0 and y >= 0 for x, y in puntos)


def test_dualidad_valores_coinciden_y_expone_signos():
    mixto = modelo([3, 2], "max", [([1, 1], "<=", 10), ([1, 0], ">=", 2)])
    datos = post("/api/dualidad/resolver", mixto).json()
    assert datos["valores_coinciden"] is True
    assert datos["primal"]["valor_objetivo"] == pytest.approx(30)
    assert datos["signos_dual"] == [">=0", "<=0"]


def test_dualidad_primal_inviable_no_falla():
    datos = post("/api/dualidad/resolver", INVIABLE)
    assert datos.status_code == 200
    assert datos.json()["primal"]["estado"] == "inviable"


def test_dualidad_primal_no_acotado_tiene_dual_inviable():
    datos = post("/api/dualidad/resolver", NO_ACOTADO).json()
    assert datos["primal"]["estado"] == "no acotado"
    assert datos["dual"]["estado"] == "inviable"


def test_transporte_taha():
    cuerpo = {"costos": [[10, 2, 20, 11], [12, 7, 9, 20], [4, 14, 16, 18]], "oferta": [15, 25, 10], "demanda": [5, 15, 15, 15]}
    soluciones = {s["nombre"]: s["costo_total"] for s in post("/api/transporte/resolver", cuerpo).json()["soluciones"]}
    assert soluciones == {"Esquina noroeste": 520, "Costo mínimo": 475, "Vogel": 475}


def test_transporte_desbalanceado_agrega_ficticio():
    cuerpo = {"costos": [[1, 2], [3, 4]], "oferta": [10, 10], "demanda": [5, 5]}
    datos = post("/api/transporte/resolver", cuerpo).json()
    assert len(datos["demanda"]) == 3 and sum(datos["oferta"]) == sum(datos["demanda"])


def test_transporte_costos_negativos_devuelve_422_con_mensaje():
    respuesta = post("/api/transporte/resolver", {"costos": [[-1, 2]], "oferta": [5], "demanda": [2, 3]})
    assert respuesta.status_code == 422
    assert "negativos" in respuesta.json()["detail"]


def test_asignacion_libro():
    datos = post("/api/asignacion/resolver", {"costos": [[9, 2, 7, 8], [6, 4, 3, 7], [5, 8, 1, 8], [7, 6, 9, 4]]}).json()
    assert datos["costo_total"] == 13


def test_asignacion_sin_solucion_devuelve_422():
    respuesta = post("/api/asignacion/resolver", {"costos": [["X", "X"], [1, 2]]})
    assert respuesta.status_code == 422


RED_CLRS = [(1, 2, 16), (1, 3, 13), (2, 3, 10), (3, 2, 4), (2, 4, 12), (4, 3, 9), (3, 5, 14), (5, 4, 7), (4, 6, 20), (5, 6, 4)]


def test_flujo_maximo_clrs():
    cuerpo = {"nodos": 6, "origen": 1, "destino": 6, "aristas": [{"origen": a, "destino": b, "capacidad": c} for a, b, c in RED_CLRS]}
    assert post("/api/flujo-maximo/resolver", cuerpo).json()["flujo"] == 23


def test_flujo_costo_minimo():
    aristas = [(1, 2, 4, 2), (1, 3, 2, 2), (2, 3, 2, 1), (2, 4, 3, 3), (3, 4, 5, 1)]
    cuerpo = {
        "nodos": 4, "origen": 1, "destino": 4, "flujo_requerido": 5,
        "aristas": [{"origen": a, "destino": b, "capacidad": c, "costo": k} for a, b, c, k in aristas],
    }
    assert post("/api/flujo-costo-minimo/resolver", cuerpo).json()["costo_total"] == 19


def test_flujo_costo_minimo_capacidad_insuficiente_devuelve_422():
    cuerpo = {
        "nodos": 3, "origen": 1, "destino": 3, "flujo_requerido": 99,
        "aristas": [{"origen": 1, "destino": 3, "capacidad": 5, "costo": 1}],
    }
    respuesta = post("/api/flujo-costo-minimo/resolver", cuerpo)
    assert respuesta.status_code == 422
    assert "capacidad" in respuesta.json()["detail"]
