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


@dataclass
class ResultadoSimplex:
    estado: str
    valor_objetivo: float | None
    valores_variables: List[float]
    pasos: List[PasoSimplex]
    mensaje: str
