# Calculadora de programacion lineal

Calculadora de terminal para resolver problemas de programacion lineal con:

- Metodo simplex de dos fases.
- Restricciones `<=`, `>=` y `=`.
- Problemas de maximizacion y minimizacion.
- Construccion y resolucion del problema dual.
- Tablas completas del tableau y movimientos de pivote.
- Expresiones numericas como `3/2`, `sqrt(2)`, `pi` y `2^3`.

## Instalacion

```powershell
python -m pip install -r requirements.txt
```

## Ejecucion

```powershell
python calculadora.py
```

El modelo supone que todas las variables son no negativas (`x_i >= 0`).