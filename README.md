# Calculadora de programacion lineal

Calculadora de terminal para resolver problemas de programacion lineal con:

- Metodo simplex de dos fases.
- Metodo simplex revisado con matriz de la base.
- Restricciones `<=`, `>=` y `=`.
- Problemas de maximizacion y minimizacion.
- Construccion y resolucion del problema dual.
- Tablas completas del tableau y movimientos de pivote.
- Expresiones numericas como `3/2`, `sqrt(2)`, `pi` y `2^3`.

## Como ingresar un ejercicio

La calculadora solicita el modelo por partes. Como ejemplo, considere el
siguiente problema:

```text
Maximizar Z = 3x1 + 5x2

Sujeto a:
		x1 + 2x2 <= 8
		3x1 + 2x2 <= 12
		x1, x2 >= 0
```

La condicion `x1, x2 >= 0` ya esta incluida automaticamente. No es necesario
ingresarla.

### Paso a paso

Al iniciar el programa, seleccione el metodo:

```text
Seleccione el metodo:
1. Metodo simplex
2. Metodo de simplex revisado
3. Metodo de dualidad
Opcion: 1
```

Elija `1` para resolver el problema con Simplex.

Luego responda las preguntas del modelo de esta forma:

```text
Tipo de objetivo (escriba max o min, no 1 o 2): max
Coeficientes de Z, ejemplo 3,5: 3,5
Cantidad de restricciones (1-20): 2
```

La entrada `3,5` representa la funcion objetivo:

```text
Z = 3x1 + 5x2
```

Los coeficientes siempre se escriben en el orden `x1, x2, ...`.

Para la primera restriccion:

```text
Restriccion 1
	Coeficientes: 1,2
	Relacion (escriba <=, >= o =): <=
	Termino independiente (numero o expresion): 8
```

Esto representa:

```text
x1 + 2x2 <= 8
```

Para la segunda restriccion:

```text
Restriccion 2
	Coeficientes: 3,2
	Relacion (escriba <=, >= o =): <=
	Termino independiente (numero o expresion): 12
```

Esto representa:

```text
3x1 + 2x2 <= 12
```

La secuencia de respuestas, sin los textos que muestra el programa, es:

```text
1
max
3,5
2
1,2
<=
8
3,2
<=
12
```

### Que significa cada entrada

| Entrada | Significado | Ejemplo |
| --- | --- | --- |
| `1` o `2` | Metodo que se utilizara | `1` para Simplex |
| `max` o `min` | Tipo de objetivo | `max` |
| Coeficientes de Z | Coeficientes de la funcion objetivo | `3,5` |
| Cantidad de restricciones | Numero de condiciones del problema | `2` |
| Coeficientes | Coeficientes de una restriccion, en orden `x1, x2` | `1,2` |
| Relacion | Tipo de desigualdad o igualdad | `<=` |
| Termino independiente | Numero situado al lado derecho | `8` |

El termino independiente puede ser un numero o una expresion numerica, por
ejemplo `12`, `3/2`, `sqrt(4)` o `2^3`. No debe contener variables como `x1`.

Si la funcion objetivo tiene dos variables, cada restriccion debe tener dos
coeficientes. Por ejemplo, `1,2` significa `1x1 + 2x2`; escribir solamente
`1` no es suficiente.

Al terminar, el programa muestra las tablas del Simplex, los pivotes realizados
y el resultado optimo. Para este ejemplo, el resultado esperado es `x1 = 2`,
`x2 = 3` y `Z = 21`.

## Instalacion

```powershell
python -m pip install -r requirements.txt
```

## Ejecucion

```powershell
python calculadora.py
```

El modelo supone que todas las variables son no negativas (`x_i >= 0`).

## API con FastAPI

La API esta separada del programa de terminal. Reutiliza el mismo motor
matematico de `simplex.py` y `dualidad.py`, pero recibe los problemas como JSON.

### Instalacion y ejecucion

Instale las dependencias:

```powershell
python -m pip install -r requirements.txt
```

Inicie el servidor desde la carpeta principal del proyecto:

```powershell
python -m uvicorn api.main:app --reload
```

La API quedara disponible en `http://127.0.0.1:8000`. FastAPI genera una
interfaz para probar los endpoints en `http://127.0.0.1:8000/docs`.

### Endpoint de Simplex

```text
POST /api/simplex/resolver
```

Ejemplo de datos para el problema de prueba:

```json
{
	"tipo": "max",
	"objetivo": [3, 5],
	"restricciones": [
		{
			"coeficientes": [1, 2],
			"relacion": "<=",
			"termino_independiente": 8
		},
		{
			"coeficientes": [3, 2],
			"relacion": "<=",
			"termino_independiente": 12
		}
	]
}
```

La respuesta incluye el estado, el valor optimo, los valores de las variables y
las tablas de todas las iteraciones.

### Endpoint de Simplex revisado

```text
POST /api/simplex-revisado/resolver
```

Recibe el mismo JSON del endpoint de Simplex. La respuesta incluye los pasos
del algoritmo usando la base y sus costos reducidos.

### Endpoint de dualidad

```text
POST /api/dualidad/resolver
```

Recibe el mismo JSON del problema primal. La respuesta contiene el primal, el
dual construido, sus resultados y un indicador `valores_coinciden` para comparar
los valores optimos cuando ambos problemas tienen solucion.

### Salud del servicio

```text
GET /api/salud
```

Sirve para verificar rapidamente que el servidor esta funcionando.