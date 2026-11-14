# Safe Zone Contraction Optimization (SZCO)

SZCO es una metaheurística poblacional para la **minimización de funciones continuas sujetas a límites conocidos**.

Su diseño se inspira en una partida **Battle Royale**, donde un conjunto de jugadores explora el mapa, compite por encontrar mejores posiciones y debe permanecer dentro de una zona segura que se contrae progresivamente.

## Instalación y ejecución

### Requisitos

- Python 3 con soporte para `venv` y `pip`.
- Git, para clonar el repositorio.
- Dependencia de Python: **NumPy**.

### 1. Clonar el repositorio

```bash
git clone https://github.com/LoreDreamer/SZCO.git
cd SZCO
```

### 2. Crear un entorno virtual

Desde la raíz del proyecto:

**Windows (PowerShell o CMD):**

```powershell
py -m venv .venv
```

**Linux / macOS:**

```bash
python3 -m venv .venv
```

### 3. Activar el entorno virtual

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```bat
.venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

> Si PowerShell bloquea la activación, puedes ejecutar el intérprete del entorno directamente sin activarlo: `.venv\Scripts\python.exe imports.py`.

### 4. Instalar dependencias

Con el entorno activado:

```bash
python -m pip install -r requirements.txt
```

El archivo `requirements.txt` contiene `numpy`, que es la única dependencia externa usada actualmente por `imports.py` y `szco.py`.

Si no has añadido `requirements.txt` al repositorio, puedes instalarla directamente:

```bash
python -m pip install numpy
```

### 5. Ejecutar los experimentos

```bash
python imports.py
```

Este comando ejecuta **tres pruebas independientes** con las funciones **Sphere**, **Rastrigin** y **Rosenbrock**, utilizando los límites propios de cada función y la configuración definida en `imports.py`.

Para cada función se muestran en la terminal el mejor fitness, la mejor posición real, las evaluaciones, las iteraciones completadas, la población final, la causa de terminación, las aceptaciones greedy y por seguridad, y las eliminaciones por tormenta y combate.

### 6. Desactivar el entorno virtual

```bash
deactivate
```

**Nota:** `.venv/` ya está excluido del control de versiones mediante `.gitignore`. No es necesario subir el entorno virtual a GitHub. Un archivo `.env` de variables de entorno **no es necesario** para la ejecución actual del proyecto.

## Estructura del repositorio

```text
SZCO/
├── .gitignore        # Excluye el entorno virtual y archivos temporales
├── README.md         # Documentación e instrucciones de ejecución
├── requirements.txt  # Dependencias de Python
├── imports.py        # Configuración y ejecución de los benchmarks
└── szco.py           # Implementación de SZCO y funciones objetivo
```

## Configuración experimental

Los parámetros se modifican dentro de la función `main()` del archivo `imports.py`. No es necesario modificar `szco.py` para repetir las pruebas del informe.

| Parámetro | Variable en `imports.py` | Valor del informe |
|---|---|---:|
| Población inicial | `population_size` | 100 |
| Iteraciones máximas | `max_iterations` | 500 |
| Dimensión | `dimension` | 30 |
| Semilla aleatoria | `seed` | 42 |
| Exploración inicial (α₀) | `alpha0` | 0.04 |
| Explotación máxima (βmax) | `beta_max` | 0.80 |
| Exponente de contracción (γ) | `gamma` | 2.50 |
| Reducción poblacional (η) | `eta` | 1.00 |
| Seguridad máxima (λmax) | `lambda_max` | 1.00 |
| Fases de la tormenta (S) | `storm_phases` | 300 |
| Factor de radio mínimo (ρ) | `r_min_factor` | 0.01 |

Cada función utiliza límites reales diferentes:

| Función | Dominio por dimensión | Óptimo global conocido |
|---|---|---|
| Sphere | `[-100, 100]` | `f(0, …, 0) = 0` |
| Rastrigin | `[-5.12, 5.12]` | `f(0, …, 0) = 0` |
| Rosenbrock | `[-30, 30]` | `f(1, …, 1) = 0` |

La semilla `42` se reinicializa en cada benchmark mediante `np.random.default_rng(seed)`, tal como está implementado en `imports.py`.

### Resultados de referencia del informe final

En las ejecuciones individuales documentadas en el informe (30 dimensiones, 100 jugadores y máximo 500 iteraciones), se obtuvo:

| Función | Mejor fitness | Evaluaciones | Iteraciones | Población final |
|---|---:|---:|---:|---:|
| Sphere | 0.008583 | 25445 | 496 | 1 |
| Rastrigin | 39.8017 | 25445 | 496 | 1 |
| Rosenbrock | 29.3036 | 25445 | 496 | 1 |

Estos valores son **resultados experimentales de referencia**, no garantías de rendimiento general. Corresponden a una ejecución por función y requieren validación estadística mediante más semillas, dimensiones y comparaciones con otras metaheurísticas.

## 1. Representación de los jugadores

Cada jugador `i` representa una solución candidata mediante el par:

$$
(Z_i, F_i)
$$

Donde:

- **$Z_i$:** Posición normalizada del jugador dentro de $[0,1]^d$.
- **$F_i$:** Valor obtenido al evaluar la función objetivo.
- **$d$:** Dimensión del problema de optimización.

Durante la inicialización, los jugadores se generan en el dominio real del problema y sus posiciones se transforman al dominio normalizado mediante **min-max scaling**:

$$Z_i = \frac{X_i-LB}{UB-LB}$$

Para evaluar una solución, la posición normalizada se convierte nuevamente al dominio real definido por los límites de la función objetivo:

$$X_i = LB + Z_i(UB-LB)$$

## 2. Mejores soluciones

SZCO mantiene dos conceptos relacionados con la mejor solución:

- **Mejor activo:** Jugador con el menor fitness en la población actual.
- **Mejor histórico:** Mejor solución encontrada durante toda la ejecución.

El mejor histórico se protege mediante **elitismo** y se utiliza como centro de la zona segura y como referencia para el movimiento de explotación.

## 3. Movimiento de los jugadores

En cada ronda, los jugadores generan una posición candidata mediante la combinación de dos movimientos.

### 3.1. Exploración (Loot)

Consiste en una perturbación aleatoria cuyo alcance disminuye junto con el radio de la zona segura. Permite explorar nuevas regiones del espacio de búsqueda.

$$L_i(t)=\alpha(t)\,r(t)\,R_i(t),\quad R_i(t)\sim U([-1,1]^d)$$

La intensidad de exploración disminuye con el progreso $p_t$:

$$\alpha(t)=\alpha_0(1-p_t)$$

### 3.2. Explotación (Tormenta)

Consiste en una atracción progresiva hacia el mejor histórico. Permite concentrar la búsqueda alrededor de las mejores soluciones encontradas.

$$T_i(t)=\beta(t)(Z_{best}-Z_i(t)),\quad \beta(t)=\beta_{max}p_t^2$$

### 3.3. Generación de candidatos

Las posiciones candidatas se proyectan sobre $[0,1]^d$ para impedir que salgan del mapa normalizado:

$$Z_i^{cand}=\operatorname{clip}(Z_i+L_i+T_i,0,1)$$

Posteriormente, se transforman al dominio real y se evalúan mediante la función objetivo.

### 3.4. Contracción de la zona segura

La zona segura es una región esférica centrada en el mejor histórico. Su radio inicial es $r_0=\sqrt{d}$, el mínimo es $r_{min}=\rho r_0$ y la contracción ocurre en `storm_phases` fases discretas:

$$s_t=\frac{\lfloor p_t S\rfloor}{S},\qquad r(t)=r_{min}+(r_0-r_{min})(1-s_t)^\gamma$$

## 4. Criterios de aceptación

La aceptación de una posición utiliza dos criterios, siempre que el candidato esté dentro de la zona segura. El riesgo de una posición se calcula como:

$$R(Z_i,t)=\frac{\lVert Z_i-Z_{best}\rVert_2}{r(t)+\epsilon},\qquad \epsilon=10^{-12}$$

Si el riesgo candidato supera `1`, se rechaza el movimiento.

### 4.1. Selección Greedy

Se acepta cualquier mejora estricta del fitness, **si el candidato está dentro de la zona segura**.

### 4.2. Selección por seguridad (Safety Score)

Una posición de peor fitness puede aceptarse si permanece dentro de la zona segura y su acercamiento al centro compensa suficientemente la pérdida de calidad.

$$\Delta Q_i=\frac{F_i^{cand}-F_i}{|F_i|+\epsilon},\qquad \Delta R_i=R(Z_i^{cand},t)-R(Z_i,t)$$

$$SS_i=\Delta Q_i+\lambda(t)\Delta R_i,\qquad \lambda(t)=\lambda_{max}p_t$$

El candidato que no mejora el fitness se acepta por seguridad únicamente si $\Delta R_i<0$ y $SS_i\leq0$. De esta forma, los jugadores priorizan gradualmente la supervivencia conforme se contrae la zona.

## 5. Mecanismos de eliminación

Después del movimiento y la selección se aplican dos mecanismos de eliminación irreversible. El tamaño objetivo en la ronda es:

$$N_{objetivo}(t)=\max\left(1,\left\lceil N_0(1-p_t)^\eta\right\rceil\right)$$

### 5.1. Eliminación por tormenta

Identifica jugadores situados fuera de la zona segura. La cantidad de eliminaciones por tormenta está limitada por $\max(0,N_t-N_{objetivo})$; se eliminan prioritariamente los más alejados, preservando al mejor jugador activo.

### 5.2. Eliminación por combate

Si la población restante excede el máximo permitido en la ronda, sobreviven los jugadores con menor fitness.

### 5.3. Comportamiento de la población

- La población es no creciente.
- Los jugadores eliminados no reaparecen.
- La reducción de población ocurre progresivamente.

## 6. Condiciones de terminación

La ejecución termina cuando se cumple alguna de las siguientes condiciones:

1. Se alcanza el número máximo de iteraciones.
2. Queda un único superviviente antes de la ronda final.

## 7. Funcionamiento general del algoritmo

El orden de ejecución de cada ronda es el siguiente:

1. Guardar el mejor histórico al comienzo de la ronda.
2. Calcular progreso, exploración, explotación, radio y seguridad.
3. Generar las posiciones candidatas.
4. Proyectar los candidatos sobre $[0,1]^d$.
5. Transformar y evaluar los candidatos en el dominio real.
6. Aplicar selección greedy o aceptación por seguridad (rechazando candidatos fuera de zona).
7. Actualizar el mejor histórico.
8. Eliminar jugadores por tormenta.
9. Aplicar reducción competitiva por combate.
10. Registrar las métricas de la ronda.
11. Verificar las condiciones de terminación.

## 8. Resultados devueltos

La función `szcoAlgorithm(...)` devuelve un diccionario con la siguiente información:

| Clave del diccionario | Descripción |
|---|---|
| `best_position` | Mejor solución encontrada en el dominio original |
| `best_normalized_position` | Mejor solución encontrada en $[0,1]^d$ |
| `best_fitness` | Valor de la función objetivo de la mejor solución |
| `evaluations` | Número total de evaluaciones realizadas |
| `iterations` | Cantidad de iteraciones completadas |
| `final_population_size` | Número de jugadores supervivientes |
| `termination_reason` | Motivo de terminación: `single_survivor` o `max_iterations` |
| `history` | Registro del comportamiento durante las rondas |

## 9. Parámetros y coeficientes de SZCO

### 9.1. Parámetros principales

| Parámetro | Descripción | Efecto |
|---|---|---|
| **$\alpha_0$** | Intensidad inicial de exploración aleatoria | Un valor mayor genera movimientos exploratorios más amplios |
| **$\beta_{max}$** | Atracción máxima hacia el mejor histórico | Un valor mayor acerca más rápidamente los jugadores al centro |
| **$\gamma$** | Forma y velocidad de contracción del radio | Un valor mayor contrae más rápidamente la zona |
| **$\eta$** | Coeficiente de reducción poblacional | Un valor mayor reduce la población más rápidamente |
| **$\lambda_{max}$** | Coeficiente máximo de calidad y seguridad | Un valor mayor permite sacrificar más fitness para acercarse al centro |
| **$\epsilon$** | Protección contra divisiones por cero | Constante numérica; no es un parámetro de búsqueda |

### 9.2. Configuración de la tormenta

| Parámetro | Descripción |
|---|---|
| **Storm Phases** (`storm_phases`) | Cantidad de fases discretas de contracción. Menos fases producen cierres más grandes |
| **rMin Factor** (`r_min_factor`) | Fracción del radio inicial usada para calcular el radio mínimo |

### 9.3. Configuración de la población y del problema

| Parámetro | Descripción |
|---|---|
| **Initial Population Size** | Cantidad inicial de jugadores |
| **Maximum Iterations** | Número máximo de rondas |
| **Dimension** | Número de variables del problema |
| **Lower Bound** | Límite inferior por variable del dominio real |
| **Upper Bound** | Límite superior por variable del dominio real |
| **Seed** | Semilla que permite reproducir las ejecuciones |

### 9.4. Variables dinámicas

| Variable | Descripción |
|---|---|
| **Progress** | Progreso normalizado de la ejecución, entre 0 y 1 |
| **Storm Progress** | Progreso discretizado de la tormenta |
| **$R_0$** | Radio inicial: raíz cuadrada de la dimensión |
| **$R_{min}$** | Radio mínimo: `rMinFactor × R0` |
| **$R_t$** | Radio actual de la zona segura |
| **$\alpha_t$** | Intensidad de exploración actual |
| **$\beta_t$** | Intensidad de explotación actual |
| **$\lambda_t$** | Importancia actual de la seguridad |
| **Target Population Size** | Tamaño objetivo de población por ronda |
| **Maximum Storm Deaths** | Máximo de eliminaciones por tormenta permitido por el objetivo poblacional |

### 9.5. Variables de evaluación y seguridad

| Variable | Descripción |
|---|---|
| **Current Risk** | Riesgo de la posición actual según su distancia al centro |
| **Candidate Risk** | Riesgo de la posición candidata |
| **Quality Change** | Cambio relativo en el fitness |
| **$\Delta Risk$** | Diferencia entre el riesgo candidato y el actual |
| **Safety Score** | Combinación de cambio de calidad y riesgo utilizada en la aceptación por seguridad |

## 10. Estado del proyecto

La configuración actual constituye una **versión experimental de SZCO**. Sus parámetros deben evaluarse y calibrarse antes de obtener conclusiones sobre su rendimiento frente a otras metaheurísticas.

La evaluación presentada en el informe final es preliminar: contempla una ejecución independiente de cada benchmark en 30 dimensiones. Como trabajo futuro se consideran múltiples semillas, diferentes dimensionalidades y comparaciones bajo presupuestos de evaluación equivalentes.
