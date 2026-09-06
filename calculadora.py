from dualidad import construir_dual, resolver_con_dualidad
from expresiones import evaluar_lista, evaluar_numero
from modelos import ProblemaLineal, Restriccion
from presentacion import mostrar_problema, mostrar_resultado, mostrar_tabla
from simplex import resolver_simplex


def pedir_texto_no_vacio(mensaje: str) -> str:
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("Este campo no puede quedar vacio.")


def pedir_entero(mensaje: str, minimo: int, maximo: int) -> int:
    while True:
        texto = input(mensaje).strip()
        try:
            valor = int(texto)
        except ValueError:
            print("Ingrese un numero entero.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"Ingrese un valor entre {minimo} y {maximo}.")


def pedir_expresion(mensaje: str) -> float:
    while True:
        try:
            return evaluar_numero(input(mensaje))
        except (TypeError, ValueError) as error:
            print(f"Entrada no valida: {error}")


def pedir_lista(mensaje: str, cantidad: int | None = None) -> list[float]:
    while True:
        try:
            valores = evaluar_lista(input(mensaje))
        except (TypeError, ValueError) as error:
            print(f"Entrada no valida: {error}")
            continue
        if cantidad is not None and len(valores) != cantidad:
            print(
                f"Debe ingresar exactamente {cantidad} coeficientes. "
                f"Ejemplo: " + ",".join(["0"] * cantidad)
            )
            continue
        return valores


def pedir_problema() -> ProblemaLineal:
    print("\nIngrese los datos del modelo. Use coma para separar coeficientes.")
    tipo = pedir_texto_no_vacio("Tipo de objetivo (escriba max o min, no 1 o 2): ").lower()
    while tipo not in {"max", "min"}:
        print("Debe escribir max o min.")
        tipo = pedir_texto_no_vacio("Tipo de objetivo: ").lower()
    objetivo = pedir_lista("Coeficientes de Z, ejemplo 3,5: ")
    if not 1 <= len(objetivo) <= 20:
        raise ValueError("El modelo debe tener entre 1 y 20 variables.")
    nombres = [f"x{i + 1}" for i in range(len(objetivo))]
    cantidad = pedir_entero("Cantidad de restricciones (1-20): ", 1, 20)
    restricciones = []
    for indice in range(cantidad):
        print(f"Restriccion {indice + 1}")
        coeficientes = pedir_lista("  Coeficientes: ", len(objetivo))
        relacion = pedir_texto_no_vacio("  Relacion (escriba <=, >= o =): ")
        relacion = {"≤": "<=", "≥": ">="}.get(relacion, relacion)
        if relacion not in {"<=", ">=", "="}:
            print("Relación inválida. Escriba la combinación completa: <=, >= o =.")
            while relacion not in {"<=", ">=", "="}:
                relacion = pedir_texto_no_vacio("  Relacion (escriba <=, >= o =): ")
                relacion = {"≤": "<=", "≥": ">="}.get(relacion, relacion)
        rhs = pedir_expresion("  Termino independiente (numero o expresion): ")
        restricciones.append(Restriccion(coeficientes, relacion, rhs))
    return ProblemaLineal(objetivo, tipo, restricciones, nombres)


def ejecutar_simplex(problema):
    resultado = resolver_simplex(problema)
    mostrar_problema(problema)
    for paso in resultado.pasos:
        mostrar_tabla(paso)
    mostrar_resultado(resultado, problema.nombres_variables)


def ejecutar_dualidad(problema):
    dual = construir_dual(problema)
    mostrar_problema(problema, "Primal")
    mostrar_problema(dual, "Dual construido")
    print("\nResolucion del primal")
    ejecutar_simplex(problema)
    print("\nResolucion del dual")
    ejecutar_simplex(dual)


def pedir_metodo() -> str:
    print("\nSeleccione el metodo:")
    print("1. Metodo simplex")
    print("2. Metodo de dualidad")
    opcion = input("Opcion: ").strip()
    while opcion not in {"1", "2"}:
        opcion = input("Seleccione 1 para Simplex o 2 para Dualidad: ").strip()
    return opcion


def main():
    print("CALCULADORA DE PROGRAMACION LINEAL")
    print("Variables no negativas: x1, x2, ...")
    while True:
        try:
            opcion = pedir_metodo()
            problema = pedir_problema()
            if opcion == "1":
                ejecutar_simplex(problema)
            elif opcion == "2":
                ejecutar_dualidad(problema)
            else:
                print("Metodo no valido.")
        except (ValueError, TypeError) as error:
            print(f"Entrada no valida: {error}")
        except KeyboardInterrupt:
            print("\nPrograma terminado.")
            return
        continuar = input("\nResolver otro problema? (s/n): ").strip().lower()
        if continuar != "s":
            break


if __name__ == "__main__":
    main()
