from pydantic import BaseModel, Field, field_validator, model_validator


class RestriccionEntrada(BaseModel):
    coeficientes: list[float] = Field(min_length=1, max_length=20)
    relacion: str
    termino_independiente: float

    @field_validator("relacion")
    @classmethod
    def validar_relacion(cls, valor: str) -> str:
        valor = {"≤": "<=", "≥": ">="}.get(valor.strip(), valor.strip())
        if valor not in {"<=", ">=", "="}:
            raise ValueError("La relacion debe ser <=, >= o =.")
        return valor


class ProblemaEntrada(BaseModel):
    objetivo: list[float] = Field(min_length=1, max_length=20)
    tipo: str
    restricciones: list[RestriccionEntrada] = Field(min_length=1, max_length=20)

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if valor not in {"max", "min"}:
            raise ValueError("El tipo debe ser max o min.")
        return valor

    @model_validator(mode="after")
    def validar_dimensiones(self):
        cantidad_variables = len(self.objetivo)
        if any(len(restriccion.coeficientes) != cantidad_variables for restriccion in self.restricciones):
            raise ValueError("Cada restriccion debe tener un coeficiente por variable.")
        return self


class PasoSalida(BaseModel):
    fase: str
    iteracion: int
    encabezados: list[str]
    tabla: list[list[float]]
    base: list[str]
    entra: str
    sale: str
    razon: str
    # Exclusivos del simplex revisado (None en el simplex por tablas y en dualidad).
    base_inversa: list[list[float]] | None = None
    cb: list[float] | None = None
    y: list[float] | None = None
    xb: list[float] | None = None
    costos_reducidos: list[float] | None = None
    columna_pivote: list[float] | None = None


class ResultadoSalida(BaseModel):
    estado: str
    valor_objetivo: float | None
    valores_variables: list[float]
    pasos: list[PasoSalida]
    mensaje: str
    nombres_variables: list[str]


class DualidadSalida(BaseModel):
    primal: ResultadoSalida
    dual: ResultadoSalida
    modelo_dual: ProblemaEntrada
    valores_coinciden: bool | None


class VerticeGraficoSalida(BaseModel):
    x: float
    y: float
    valor_objetivo: float


class PasoGraficoSalida(BaseModel):
    titulo: str
    detalle: str


class GraficoSalida(BaseModel):
    estado: str
    valor_objetivo: float | None
    valores_variables: list[float]
    vertices: list[VerticeGraficoSalida]
    pasos: list[PasoGraficoSalida]
    mensaje: str


class TransporteEntrada(BaseModel):
    costos: list[list[float]] = Field(min_length=1, max_length=20)
    oferta: list[float] = Field(min_length=1, max_length=20)
    demanda: list[float] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def validar_dimensiones(self):
        if len(self.costos) != len(self.oferta):
            raise ValueError("Debe existir una oferta por cada origen.")
        if any(len(fila) != len(self.demanda) for fila in self.costos):
            raise ValueError("La matriz debe tener una columna por cada destino.")
        return self


class PasoTransporteSalida(BaseModel):
    titulo: str
    detalle: str


class SolucionTransporteSalida(BaseModel):
    nombre: str
    asignaciones: list[list[float]]
    costo_total: float
    pasos: list[PasoTransporteSalida]


class TransporteSalida(BaseModel):
    oferta: list[float]
    demanda: list[float]
    costos: list[list[float]]
    soluciones: list[SolucionTransporteSalida]
    mensaje: str


class AsignacionEntrada(BaseModel):
    costos: list[list[float]] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def validar_matriz(self):
        if not self.costos or not self.costos[0]:
            raise ValueError("La matriz de costos no puede estar vacía.")
        if any(len(fila) != len(self.costos[0]) for fila in self.costos):
            raise ValueError("Todas las filas deben tener la misma cantidad de costos.")
        return self


class PasoAsignacionSalida(BaseModel):
    titulo: str
    detalle: str
    matriz: list[list[float]] | None = None
    asignaciones: list[list[int]] | None = None


class AsignacionSalida(BaseModel):
    costos: list[list[float]]
    asignaciones: list[dict[str, int | float]]
    costo_total: float
    pasos: list[PasoAsignacionSalida]
