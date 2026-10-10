from pydantic import BaseModel, Field, model_validator


class AristaEntrada(BaseModel):
    origen: int
    destino: int
    capacidad: float = Field(gt=0)
    costo: float = 0


class FlujoEntrada(BaseModel):
    nodos: int = Field(ge=2, le=20)
    origen: int
    destino: int
    aristas: list[AristaEntrada] = Field(min_length=1, max_length=40)
    flujo_requerido: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validar_extremos(self):
        if not 1 <= self.origen <= self.nodos or not 1 <= self.destino <= self.nodos or self.origen == self.destino:
            raise ValueError("El origen y el destino deben ser nodos distintos dentro de la red.")
        return self


class FlujoAristaSalida(BaseModel):
    origen: int
    destino: int
    flujo: float
    capacidad: float
    costo: float


class PasoFlujoSalida(BaseModel):
    titulo: str
    detalle: str
    estado: list[FlujoAristaSalida] | None = None


class FlujoSalida(BaseModel):
    flujo: float
    costo_total: float
    flujos: list[FlujoAristaSalida]
    pasos: list[PasoFlujoSalida]
    mensaje: str
