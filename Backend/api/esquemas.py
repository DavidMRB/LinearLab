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
