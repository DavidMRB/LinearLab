import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from Backend.dualidad import construir_dual, resolver_con_dualidad
from Backend.asignacion import resolver_asignacion
from Backend.flujo import resolver_flujo_costo_minimo, resolver_flujo_maximo
from Backend.grafico import resolver_grafico
from Backend.transporte import resolver_transporte
from Backend.modelos import ProblemaLineal, Restriccion
from Backend.simplex import resolver_simplex
from Backend.simplex_revisado import resolver_simplex_revisado
from Backend.api.esquemas import (
    DualidadSalida,
    GraficoSalida,
    ProblemaEntrada,
    ResultadoSalida,
    TransporteEntrada,
    TransporteSalida,
    AsignacionEntrada,
    AsignacionSalida,
)
from Backend.api.esquemas_flujo import FlujoEntrada, FlujoSalida

load_dotenv()

frontend_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("FRONTEND_URL", "http://127.0.0.1:5500").split(",")
    if origin.strip()
]


app = FastAPI(
    title="Calculadora de Programacion Lineal",
    version="1.0.0",
    description="API para resolver problemas con Simplex y dualidad.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(dict.fromkeys(frontend_origins + ["http://localhost:5500", "http://127.0.0.1:5500"])),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def convertir_problema(entrada: ProblemaEntrada) -> ProblemaLineal:
    return ProblemaLineal(
        objetivo=entrada.objetivo,
        tipo=entrada.tipo,
        restricciones=[
            Restriccion(
                coeficientes=restriccion.coeficientes,
                relacion=restriccion.relacion,
                termino_independiente=restriccion.termino_independiente,
            )
            for restriccion in entrada.restricciones
        ],
        nombres_variables=[f"x{i + 1}" for i in range(len(entrada.objetivo))],
    )


def convertir_resultado(resultado, nombres_variables: list[str]) -> ResultadoSalida:
    return ResultadoSalida(
        estado=resultado.estado,
        valor_objetivo=resultado.valor_objetivo,
        valores_variables=resultado.valores_variables,
        pasos=[
            {
                "fase": paso.fase,
                "iteracion": paso.iteracion,
                "encabezados": paso.encabezados,
                "tabla": paso.tabla,
                "base": paso.base,
                "entra": paso.entra,
                "sale": paso.sale,
                "razon": paso.razon,
                "base_inversa": paso.base_inversa,
                "cb": paso.cb,
                "y": paso.y,
                "xb": paso.xb,
                "costos_reducidos": paso.costos_reducidos,
                "columna_pivote": paso.columna_pivote,
            }
            for paso in resultado.pasos
        ],
        mensaje=resultado.mensaje,
        nombres_variables=nombres_variables,
    )


def convertir_entrada(problema: ProblemaLineal) -> ProblemaEntrada:
    return ProblemaEntrada(
        objetivo=problema.objetivo,
        tipo=problema.tipo,
        restricciones=[
            {
                "coeficientes": restriccion.coeficientes,
                "relacion": restriccion.relacion,
                "termino_independiente": restriccion.termino_independiente,
            }
            for restriccion in problema.restricciones
        ],
    )


@app.get("/api/salud")
def salud():
    return {"estado": "ok", "servicio": "calculadora-programacion-lineal"}


@app.post("/api/simplex/resolver", response_model=ResultadoSalida)
def resolver_simplex_api(entrada: ProblemaEntrada):
    problema = convertir_problema(entrada)
    resultado = resolver_simplex(problema)
    return convertir_resultado(resultado, problema.nombres_variables)


@app.post("/api/simplex-revisado/resolver", response_model=ResultadoSalida)
def resolver_simplex_revisado_api(entrada: ProblemaEntrada):
    problema = convertir_problema(entrada)
    resultado = resolver_simplex_revisado(problema)
    return convertir_resultado(resultado, problema.nombres_variables)


@app.post("/api/dualidad/resolver", response_model=DualidadSalida)
def resolver_dualidad_api(entrada: ProblemaEntrada):
    problema = convertir_problema(entrada)
    dual, resultado_primal, resultado_dual = resolver_con_dualidad(problema)
    valor_primal = resultado_primal.valor_objetivo
    valor_dual = resultado_dual.valor_objetivo
    coinciden = None
    if valor_primal is not None and valor_dual is not None:
        coinciden = abs(valor_primal - valor_dual) <= 1e-6
    return DualidadSalida(
        primal=convertir_resultado(resultado_primal, problema.nombres_variables),
        dual=convertir_resultado(resultado_dual, dual.nombres_variables),
        modelo_dual=convertir_entrada(dual),
        valores_coinciden=coinciden,
    )


@app.post("/api/grafico/resolver", response_model=GraficoSalida)
def resolver_grafico_api(entrada: ProblemaEntrada):
    if len(entrada.objetivo) != 2:
        raise HTTPException(
            status_code=422,
            detail="El método gráfico requiere exactamente dos variables.",
        )
    problema = convertir_problema(entrada)
    resultado = resolver_grafico(problema)
    return GraficoSalida(
        estado=resultado.estado,
        valor_objetivo=resultado.valor_objetivo,
        valores_variables=resultado.valores_variables,
        vertices=[
            {
                "x": vertice.x,
                "y": vertice.y,
                "valor_objetivo": vertice.valor_objetivo,
            }
            for vertice in resultado.vertices
        ],
        pasos=[
            {"titulo": paso.titulo, "detalle": paso.detalle}
            for paso in resultado.pasos
        ],
        mensaje=resultado.mensaje,
    )


@app.post("/api/transporte/resolver", response_model=TransporteSalida)
def resolver_transporte_api(entrada: TransporteEntrada):
    resultado = resolver_transporte(entrada.costos, entrada.oferta, entrada.demanda)
    return TransporteSalida(
        oferta=resultado.oferta,
        demanda=resultado.demanda,
        costos=resultado.costos,
        soluciones=[
            {
                "nombre": solucion.nombre,
                "asignaciones": solucion.asignaciones,
                "costo_total": solucion.costo_total,
                "pasos": [
                    {"titulo": paso.titulo, "detalle": paso.detalle}
                    for paso in solucion.pasos
                ],
            }
            for solucion in resultado.soluciones
        ],
        mensaje=resultado.mensaje,
    )


@app.post("/api/asignacion/resolver", response_model=AsignacionSalida)
def resolver_asignacion_api(entrada: AsignacionEntrada):
    resultado = resolver_asignacion(entrada.costos)
    return AsignacionSalida(
        costos=resultado.costos,
        asignaciones=resultado.asignaciones,
        costo_total=resultado.costo_total,
        pasos=[
            {
                "titulo": paso.titulo,
                "detalle": paso.detalle,
                "matriz": paso.matriz,
                "asignaciones": paso.asignaciones,
            }
            for paso in resultado.pasos
        ],
    )


@app.post("/api/flujo-maximo/resolver", response_model=FlujoSalida)
def resolver_flujo_maximo_api(entrada: FlujoEntrada):
    resultado = resolver_flujo_maximo(
        entrada.nodos, entrada.origen, entrada.destino,
        [arista.model_dump() for arista in entrada.aristas],
    )
    return FlujoSalida(
        flujo=resultado.flujo, costo_total=resultado.costo_total, flujos=resultado.flujos,
        pasos=[{"titulo": paso.titulo, "detalle": paso.detalle, "estado": paso.estado} for paso in resultado.pasos],
        mensaje=resultado.mensaje,
    )


@app.post("/api/flujo-costo-minimo/resolver", response_model=FlujoSalida)
def resolver_flujo_costo_minimo_api(entrada: FlujoEntrada):
    if entrada.flujo_requerido is None:
        raise HTTPException(status_code=422, detail="El flujo requerido es obligatorio para este método.")
    resultado = resolver_flujo_costo_minimo(
        entrada.nodos, entrada.origen, entrada.destino,
        [arista.model_dump() for arista in entrada.aristas], entrada.flujo_requerido,
    )
    return FlujoSalida(
        flujo=resultado.flujo, costo_total=resultado.costo_total, flujos=resultado.flujos,
        pasos=[{"titulo": paso.titulo, "detalle": paso.detalle, "estado": paso.estado} for paso in resultado.pasos],
        mensaje=resultado.mensaje,
    )
