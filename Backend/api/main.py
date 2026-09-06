import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from Backend.dualidad import construir_dual, resolver_con_dualidad
from Backend.modelos import ProblemaLineal, Restriccion
from Backend.simplex import resolver_simplex
from Backend.api.esquemas import DualidadSalida, ProblemaEntrada, ResultadoSalida

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
