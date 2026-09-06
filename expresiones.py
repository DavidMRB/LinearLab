import math
import re

try:
    import sympy as sp
except ImportError:  # Permite usar el programa sin SymPy instalado.
    sp = None


_SIMBOLOS = {nombre: getattr(math, nombre) for nombre in dir(math) if not nombre.startswith("_")}
_SIMBOLOS.update({"pi": math.pi, "e": math.e})


def evaluar_numero(texto: str) -> float:
    """Convierte expresiones numericas seguras a float."""
    limpio = texto.strip().replace("^", "**").replace(",", ".")
    if not limpio:
        raise ValueError("La expresion no puede estar vacia.")

    if sp is not None:
        try:
            expresion = sp.sympify(limpio, locals=_SIMBOLOS)
            if getattr(expresion, "free_symbols", set()):
                raise ValueError("La expresion contiene simbolos no definidos.")
            resultado = float(expresion.evalf() if hasattr(expresion, "evalf") else expresion)
            if not math.isfinite(resultado):
                raise ValueError("El resultado debe ser un numero finito.")
            return resultado
        except (TypeError, ValueError, SyntaxError) as error:
            raise ValueError(f"Expresion no valida: {texto}") from error

    if not re.fullmatch(r"[0-9eE+*/()._\- a-zA-Z]+", limpio):
        raise ValueError(f"Expresion no valida: {texto}")
    try:
        resultado = float(eval(limpio, {"__builtins__": {}}, _SIMBOLOS))
        if not math.isfinite(resultado):
            raise ValueError("El resultado debe ser un numero finito.")
        return resultado
    except Exception as error:
        raise ValueError(f"Expresion no valida: {texto}") from error


def evaluar_lista(texto: str) -> list[float]:
    elementos = texto.split(",")
    if not texto.strip() or any(not elemento.strip() for elemento in elementos):
        raise ValueError("Escriba una lista completa, separada por comas.")
    return [evaluar_numero(item) for item in elementos]
