# Calculadora de programacion lineal

Calculadora de terminal para resolver problemas de programacion lineal con:

- Metodo simplex de dos fases.
- Metodo simplex revisado con matriz de la base.
- Restricciones `<=`, `>=` y `=`.
- Problemas de maximizacion y minimizacion.
- Construccion y resolucion del problema dual.
- Metodo grafico para problemas con exactamente dos variables.
- Metodo Kuhn-Munkres (hungaro) para asociar trabajadores y tareas con costo minimo.
- Problema de flujo maximo y flujo a costo minimo sobre redes dirigidas.
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

Inicie el servidor desde la carpeta principal del proyecto (la carpeta que
contiene `Backend`):

```powershell
python -m uvicorn Backend.api.main:app --reload
```

La API quedara disponible en `http://127.0.0.1:8000`. FastAPI genera una
interfaz para probar los endpoints en `http://127.0.0.1:8000/docs`.

Los endpoints `/api/flujo-maximo/resolver` y
`/api/flujo-costo-minimo/resolver` reciben una red con `nodos`, `origen`,
`destino` y una lista de aristas `{origen, destino, capacidad, costo}`.
El flujo a costo minimo agrega `flujo_requerido`; el flujo maximo no lo
necesita.

Si actualmente se encuentra dentro de la carpeta `Backend`, vuelva primero a
la carpeta principal:

```powershell
cd ..
python -m uvicorn Backend.api.main:app --reload
```

### Ejecucion del frontend

El frontend es una aplicacion estatica. Inicie un segundo servidor desde la
carpeta `Frontend`, en otra terminal:

```powershell
cd "C:\Users\David\Documents\FESC\8_Semestre\Geiner\Primer Corte\Frontend"
python -m http.server 5500
```

Abra `http://127.0.0.1:5500` en el navegador. En desarrollo deben mantenerse
ejecutandose ambos servidores:

| Terminal | Carpeta | Comando | Direccion |
| --- | --- | --- | --- |
| Backend | Carpeta principal | `python -m uvicorn Backend.api.main:app --reload` | `http://127.0.0.1:8000` |
| Frontend | `Frontend` | `python -m http.server 5500` | `http://127.0.0.1:5500` |

### Estructura modular del frontend

El archivo `Frontend/index.html` funciona como un shell mínimo y carga el
módulo principal `script.js`. La interfaz compartida se construye desde
`Frontend/components/layout.js`, mientras que cada método mantiene su
configuración en un módulo independiente dentro de `Frontend/modules/`:

- `simplex.js`
- `simplexRevisado.js`
- `dualidad.js`
- `grafico.js`
- `transporte.js`
- `asignacion.js`

Los componentes compartidos, como el selector de métodos, la entrada y el
panel de resultados, se reutilizan desde `components/` sin duplicarlos en
cada método.

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

### Endpoint del método gráfico

```text
POST /api/grafico/resolver
```

Recibe el mismo JSON del problema primal, pero requiere exactamente dos
variables. La respuesta incluye los vértices de la región factible, el valor
de la función objetivo en cada vértice y la solución óptima. La interfaz web
representa estos datos en una gráfica junto con las rectas de las
restricciones.

### Problema del transporte

La aplicación también permite resolver la primera fase del problema del
transporte mediante tres métodos de solución inicial:

- Esquina noroeste.
- Costo mínimo.
- Aproximación de Vogel.

El módulo recibe una matriz de costos, la oferta de cada origen y la demanda de
cada destino. Si la oferta total y la demanda total no coinciden, agrega
automáticamente un origen o destino ficticio con costo cero para balancear el
modelo.

El endpoint es:

```text
POST /api/transporte/resolver
```

Ejemplo de datos:

```json
{
  "costos": [
    [2, 5, 7, 3],
    [3, 6, 4, 2],
    [5, 4, 3, 6]
  ],
  "oferta": [20, 30, 25],
  "demanda": [10, 25, 20, 20]
}
```

La interfaz muestra las asignaciones, el costo total y el desarrollo paso a
paso de cada método. La optimización y verificación mediante MODI (u-v) se
agregará en una siguiente fase.

### Método Kuhn-Munkres

El método de asignación recibe una matriz de costos donde cada fila representa
un trabajador y cada columna una tarea. La interfaz permite matrices cuadradas
o rectangulares de hasta 20 x 20 y agrega automáticamente filas o columnas
ficticias con costo cero cuando son necesarias.

El procedimiento que se muestra en la interfaz es:

1. Normalizar la matriz a una matriz cuadrada.
2. Restar el menor valor de cada fila.
3. Restar el menor valor de cada columna.
4. Buscar ceros independientes. Si no existe uno por cada fila y columna,
   cubrir todos los ceros con el número mínimo de líneas; restar el menor
   valor no cubierto y sumarlo en las intersecciones de las líneas. Repetir.
5. Leer los ceros independientes como asignaciones definitivas.
6. Sumar los costos originales de las asignaciones para obtener el costo mínimo.

El endpoint es:

```text
POST /api/asignacion/resolver
```

Ejemplo:

```json
{
  "costos": [
    [9, 2, 7],
    [6, 4, 3],
    [5, 8, 1]
  ]
}
```

### Salud del servicio

```text
GET /api/salud
```

Sirve para verificar rapidamente que el servidor esta funcionando.