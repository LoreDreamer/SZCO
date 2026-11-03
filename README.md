
# Safe Zone Contraction Optimization (SZCO)

SZCO es una metaheurística poblacional para la minimización de funciones continuas sujetas a límites conocidos.

Su diseño se inspira en una partida **Battle Royale**, donde un conjunto de jugadores explora el mapa, compite por encontrar mejores posiciones y debe permanecer dentro de una zona segura que se contrae progresivamente.

## 1. Representación de los jugadores

Cada jugador `i` representa una solución candidata mediante el par:

$$
(Z_i, F_i)
$$

Donde:

- **$Z_i$:** Posición normalizada del jugador dentro de `[0,1]^d`.
- **$F_i$:** Valor obtenido al evaluar la función objetivo.
- **$d$:** Dimensión del problema de optimización.

Durante la inicialización, los jugadores se generan en el dominio real del problema y sus posiciones se transforman al dominio normalizado mediante **min-max scaling**.

Para evaluar una solución, la posición normalizada se convierte nuevamente al dominio real definido por los límites de la función objetivo.

## 2. Mejores soluciones

SZCO mantiene dos conceptos relacionados con la mejor solución:

- **Mejor activo:** Jugador con el menor fitness en la población actual.
- **Mejor histórico:** Mejor solución encontrada durante toda la ejecución.

El mejor histórico se protege mediante **elitismo** y se utiliza como centro de la zona segura y como referencia para el movimiento de explotación.

## 3. Movimiento de los jugadores

En cada ronda, los jugadores generan una posición candidata mediante la combinación de dos movimientos.

### 3.1. Exploración (Loot)

Consiste en una perturbación aleatoria cuyo alcance disminuye junto con el radio de la zona segura.

Permite explorar nuevas regiones del espacio de búsqueda.

### 3.2. Explotación (Tormenta)

Consiste en una atracción progresiva hacia el mejor histórico.

Permite concentrar la búsqueda alrededor de las mejores soluciones encontradas.

### 3.3. Generación de candidatos

Las posiciones candidatas se proyectan sobre `[0,1]^d` para impedir que salgan del mapa normalizado.

Posteriormente, se transforman al dominio real y se evalúan mediante la función objetivo.

## 4. Criterios de aceptación

La aceptación de una posición utiliza dos criterios:

### 4.1. Selección Greedy

Se acepta cualquier mejora estricta del fitness.

### 4.2. Selección por seguridad

Una posición de peor fitness puede aceptarse si:

- Permanece dentro de la zona segura.
- Su acercamiento al centro compensa suficientemente la pérdida de calidad.

La influencia de la seguridad está controlada por $\lambda(t)$, que aumenta con el progreso de la ejecución.

De esta forma, los jugadores priorizan gradualmente la supervivencia conforme se contrae la zona.

## 5. Mecanismos de eliminación

Después del movimiento y la selección se aplican dos mecanismos de eliminación irreversible.

### 5.1. Eliminación por tormenta

Remueve jugadores situados fuera de la zona segura.

### 5.2. Eliminación por combate

Si la población excede el máximo permitido en la ronda, sobreviven los jugadores con menor fitness.

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
4. Proyectar los candidatos sobre `[0,1]^d`.
5. Transformar y evaluar los candidatos en el dominio real.
6. Aplicar selección greedy o aceptación por seguridad.
7. Actualizar el mejor histórico.
8. Eliminar jugadores por tormenta.
9. Aplicar reducción competitiva por combate.
10. Registrar las métricas de la ronda.
11. Verificar las condiciones de terminación.

## 8. Resultados devueltos

El algoritmo devuelve un diccionario con la siguiente información:

| Resultado | Descripción |
|---|---|
| Mejor solución real | Mejor posición encontrada en el dominio original |
| Mejor solución normalizada | Mejor posición encontrada en `[0,1]^d` |
| Mejor fitness | Valor de la función objetivo de la mejor solución |
| Evaluaciones | Número total de evaluaciones realizadas |
| Iteraciones | Cantidad de iteraciones completadas |
| Población final | Número de jugadores supervivientes |
| Causa de terminación | Motivo por el cual terminó la ejecución |
| Historial | Registro del comportamiento durante las rondas |

---

## 9. Parámetros y coeficientes de SZCO

### 9.1. Parámetros principales

| Parámetro | Descripción | Efecto |
|---|---|---|
| **$\alpha$** | Intensidad inicial de exploración aleatoria | Un valor mayor genera movimientos exploratorios más amplios |
| **$\beta$** | Atracción hacia el mejor histórico | Un valor mayor acerca más rápidamente los jugadores al centro |
| **$\gamma$** | Forma y velocidad de contracción del radio | Un valor mayor hace que la zona se vuelva pequeña más rápidamente |
| **$\eta$** | Coeficiente de reducción poblacional | Un valor mayor reduce la cantidad de jugadores más rápidamente |
| **$\lambda$** | Coeficiente de calidad y seguridad | Un valor mayor permite sacrificar más fitness para acercarse al centro |
| **$\epsilon$** | Protección contra divisiones por cero | Constante numérica, no es un parámetro de búsqueda |

### 9.2. Configuración de la tormenta

| Parámetro | Descripción |
|---|---|
| **Storm Phases** | Cantidad de fases o cierres discretos de la tormenta. Menos fases producen cierres más grandes; más fases producen cierres menores |
| **rMin Factor** | Factor utilizado para calcular el radio mínimo. Un valor menor produce una zona final más pequeña y peligrosa |

### 9.3. Configuración de la población y del problema

| Parámetro | Descripción |
|---|---|
| **Initial Population Size** | Cantidad inicial de jugadores. Un valor mayor aumenta la diversidad y el costo computacional |
| **Maximum Iterations** | Número máximo de rondas. Un valor menor deja menos tiempo para escapar entre cierres de zona |
| **Dimension** | Número de variables del problema. También afecta las distancias y los radios inicial y mínimo |
| **Lower Bound** | Límite inferior de cada variable del dominio real |
| **Upper Bound** | Límite superior de cada variable del dominio real |
| **Seed** | Semilla del generador aleatorio que permite reproducir exactamente una ejecución |

### 9.4. Variables dinámicas

Estas variables se calculan automáticamente durante la ejecución.

| Variable | Descripción |
|---|---|
| **Progress** | Progreso general de la ejecución entre 0 y 1, calculado a partir de la iteración actual |
| **Storm Progress** | Progreso discretizado de la tormenta, que determina cuándo cambia el radio |
| **$R_0$** | Radio inicial de la zona segura, calculado como la raíz cuadrada de la dimensión |
| **$R_{\min}$** | Radio mínimo, calculado multiplicando R Min Factor por R0 |
| **$R_t$** | Radio actual, dependiente de R0, R Min, Gamma y Storm Progress |
| **$\alpha_t$** | Intensidad de exploración actual, que disminuye progresivamente hasta cero |
| **$\beta_t$** | Intensidad de explotación actual, que aumenta hasta Beta Max |
| **$\lambda_t$** | Importancia actual de la seguridad, que aumenta hasta Lambda Max |
| **Target Population Size** | Población máxima permitida en una ronda, dependiente de la población inicial, el progreso y Eta |
| **Maximum Storm Deaths** | Máximo de jugadores que puede eliminar la tormenta sin reducir la población por debajo del objetivo |

### 9.5. Variables de evaluación y seguridad

| Variable | Descripción |
|---|---|
| **Current Risk** | Riesgo actual de un jugador según su distancia al centro |
| **Candidate Risk** | Riesgo de la posición candidata según su distancia al centro |
| **Quality Change** | Cambio relativo entre el fitness actual y el candidato |
| **$\Delta Risk$** | Diferencia entre el riesgo candidato y el riesgo actual |
| **Safety Score** | Combinación del cambio de calidad y del cambio de riesgo, que determina si una posición peor puede aceptarse por ser más segura |

---

## 10. Estado del proyecto

La configuración actual constituye una **versión experimental de SZCO**.

Sus parámetros deben evaluarse y calibrarse antes de obtener conclusiones sobre su rendimiento frente a otras metaheurísticas.
