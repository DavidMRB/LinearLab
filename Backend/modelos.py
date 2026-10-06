from dataclasses import dataclass
from typing import List


@dataclass
class Restriccion:
    coeficientes: List[float]
    relacion: str
    termino_independiente: float


@dataclass
class ProblemaLineal:
    objetivo: List[float]
    tipo: str
    restricciones: List[Restriccion]
    nombres_variables: List[str]
    signos_variables: List[str] | None = None


@dataclass
class PasoSimplex:
    fase: str
    iteracion: int
    encabezados: List[str]
    tabla: List[List[float]]
    base: List[str]
    entra: str = ""
    sale: str = ""
    razon: str = ""
    # Campos exclusivos del metodo simplex revisado: exponen las operaciones
    # matriciales (B^-1, y = c_B B^-1, x_B = B^-1 b y la columna B^-1 A_j de
    # la variable entrante) que lo distinguen del metodo simplex por tablas.
    base_inversa: List[List[float]] | None = None
    cb: List[float] | None = None
    y: List[float] | None = None
    xb: List[float] | None = None
    costos_reducidos: List[float] | None = None
    columna_pivote: List[float] | None = None


@dataclass
class ResultadoSimplex:
    estado: str
    valor_objetivo: float | None
    valores_variables: List[float]
    pasos: List[PasoSimplex]
    mensaje: str
