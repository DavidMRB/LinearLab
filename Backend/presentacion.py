from Backend.modelos import ProblemaLineal, ResultadoSimplex


def numero(valor: float) -> str:
    if abs(valor) < 1e-9:
        valor = 0
    return f"{valor:.4f}".rstrip("0").rstrip(".")


def mostrar_problema(problema: ProblemaLineal, titulo: str = "Problema"):
    print(f"\n{titulo}: {problema.tipo.upper()} Z = " + " + ".join(f"({numero(c)}){v}" for c, v in zip(problema.objetivo, problema.nombres_variables)))
    for restriccion in problema.restricciones:
        izquierda = " + ".join(f"({numero(c)}){v}" for c, v in zip(restriccion.coeficientes, problema.nombres_variables))
        print(f"  {izquierda} {restriccion.relacion} {numero(restriccion.termino_independiente)}")


def mostrar_tabla(paso):
    print(f"\n[{paso.fase} | iteracion {paso.iteracion}] Base: {', '.join(paso.base)}")
    if paso.entra or paso.sale:
        print(f"Movimiento: entra {paso.entra or '-'} / sale {paso.sale or '-'}")
    encabezados = ["Base"] + paso.encabezados
    filas = []
    for indice, fila in enumerate(paso.tabla[:-1]):
        filas.append([paso.base[indice]] + [numero(valor) for valor in fila])
    filas.append(["Z"] + [numero(valor) for valor in paso.tabla[-1]])
    anchos = [max(len(str(fila[col])) for fila in [encabezados] + filas) for col in range(len(encabezados))]
    print(" | ".join(str(valor).rjust(anchos[i]) for i, valor in enumerate(encabezados)))
    print("-+-".join("-" * ancho for ancho in anchos))
    for fila in filas:
        print(" | ".join(str(valor).rjust(anchos[i]) for i, valor in enumerate(fila)))


def mostrar_resultado(resultado: ResultadoSimplex, variables):
    print(f"\nEstado: {resultado.estado.upper()}")
    print(resultado.mensaje)
    if resultado.valor_objetivo is not None:
        print(f"Valor optimo: {numero(resultado.valor_objetivo)}")
        print("Variables: " + ", ".join(f"{v} = {numero(x)}" for v, x in zip(variables, resultado.valores_variables)))
