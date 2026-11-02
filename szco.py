import numpy as np

# Normalización
def normalize(x, lower, upper):
    return (x - lower) / (upper - lower)

# Real
def real(z, lower, upper):
  return lower + z * (upper - lower)

# Sphere
def sphere(x):
    return np.sum(x**2)

# Rastrigin
def rastrigin(x):
    return np.sum(x**2 - 10 * np.cos(2 * np.pi * x) + 10)

# Rosenbrock
def rosenbrock(x):
    return np.sum(100.0 * (x[1:] - x[:-1]**2.0)**2.0 + (1 - x[:-1])**2.0)

# Evaluación
def evaluate(z, objFunc, lower, upper):

  realPos = real(z, lower, upper)
  fitness = objFunc(realPos)

  return realPos, fitness

# Inicialización de población
def initialize(
    populationSize,
    dimension,
    objFunc,
    lower,
    upper,
    rng
):

  realPos = rng.uniform(
      low=lower,
      high=upper,
      size=(populationSize, dimension)
  )

  positions = normalize(realPos, lower, upper)
  positions = np.clip(positions, 0.0, 1.0)

  fitness = np.empty(populationSize, dtype=float)

  for i in range(populationSize):
    _, fitness[i] = evaluate(
        z = positions[i],
        objFunc = objFunc,
        lower = lower,
        upper = upper
    )

  return positions, fitness


# Generación de parámetros por iteración
def generateParameters(
    iteration,
    maxIterations,
    dimension,
    alpha0,
    betaMax,
    gamma,
    lambdaMax,
    rMinFactor=0.05,
    stormPhases=30000000
):

  if maxIterations <= 1:
      progress = 1.0
  else:
      progress = (iteration - 1) / (maxIterations - 1)

  r0 = np.sqrt(dimension)
  rMin = rMinFactor * r0

  stormStep = np.floor(progress * stormPhases)
  stormProgress = stormStep / stormPhases

  if iteration == maxIterations:
    stormProgress = 1.0

  alphaT = alpha0 * (1.0 - progress)
  betaT = betaMax * (progress**2)
  radiusT = rMin + (r0 - rMin) * (1.0 - stormProgress)**gamma
  lambdaT = lambdaMax * progress

  return {
      "progress": progress,
      "alpha": alphaT,
      "beta": betaT,
      "radius": radiusT,
      "lambda": lambdaT
      }

# Generar candidato de movimiento en una iteración
def generateCandidate(
    currentPos,
    bestPos,
    alphaT,
    betaT,
    radiusT,
    rng
):

  currentDimension = currentPos.size
  randomVector = rng.uniform(-1.0, 1.0, currentDimension)

  exploration = alphaT * radiusT * randomVector
  exploitation = betaT * (bestPos - currentPos)

  proposedPos = (currentPos + exploration + exploitation)

  return np.clip(proposedPos, 0.0, 1.0) # Para que no se salga de los límites

# Selección del candidato en caso de mejora
def selectCandidate(
    currentPos,
    candidatePos,
    currentFitness,
    candidateFitness,
    bestPos,
    radiusT,
    lambdaT, # Coeficiente de seguridad
    epsilon=1e-12 # Valor para evitar división por 0
):
  currentDistance = np.linalg.norm(currentPos - bestPos)
  candidateDistance = np.linalg.norm(candidatePos - bestPos)

  currentRisk = currentDistance / (radiusT + epsilon)
  candidateRisk = candidateDistance / (radiusT + epsilon)

  if candidateRisk > 1.0:
    return currentPos, currentFitness, "rejected_outside"

  # Greedy
  if candidateFitness < currentFitness: # Minimizar
    return candidatePos, candidateFitness, "accepted_greedy"

  # Basado en calidad/seguridad
  qualityChange = (candidateFitness - currentFitness) / (abs(currentFitness) + epsilon)

  deltaRisk = candidateRisk - currentRisk

  safetyScore = qualityChange + lambdaT * deltaRisk

  if deltaRisk < 0.0 and safetyScore <= 0.0:
    return candidatePos, candidateFitness, "accepted_safety"

  return currentPos, currentFitness, "rejected_selection"

# Ronda de movimiento
def movementRound(
    positions,
    fitness,
    bestPos,
    bestFitness,
    objFunc,
    iteration,
    maxIterations,
    alpha0,
    betaMax,
    gamma,
    lambdaMax,
    rng,
    lowerBound,
    upperBound,
    rMinFactor,
    stormPhases
):

  currentDimension = positions.shape[1]
  populationSize = positions.shape[0]

  parameters = generateParameters(
      iteration=iteration,
      maxIterations=maxIterations,
      dimension=currentDimension,
      alpha0=alpha0,
      betaMax=betaMax,
      gamma=gamma,
      lambdaMax=lambdaMax,
      rMinFactor=rMinFactor,
      stormPhases=stormPhases
      )

  roundBestPos = bestPos.copy()

  candidates = np.array([
      generateCandidate(
          currentPos=positions[i],
          bestPos=roundBestPos,
          alphaT=parameters["alpha"],
          betaT=parameters["beta"],
          radiusT=parameters["radius"],
          rng=rng
      )
      for i in range(populationSize)
  ])

  candidateFitness = np.array([
      evaluate(
          z=candidates[i],
          objFunc=objFunc,
          lower=lowerBound,
          upper=upperBound
      )[1]
      for i in range(populationSize)
  ])

  newPos = positions.copy()
  newFitness = fitness.copy()

  selectionCount = {
      "accepted_greedy": 0,
      "accepted_safety": 0,
      "rejected_outside": 0,
      "rejected_selection": 0

  }

  for i in range(populationSize):
    (selectedPos, selectedFitness, selection) = selectCandidate(
        currentPos=positions[i],
        candidatePos=candidates[i],
        currentFitness=fitness[i],
        candidateFitness=candidateFitness[i],
        bestPos=roundBestPos,
        radiusT=parameters["radius"],
        lambdaT=parameters["lambda"]
    )

    newPos[i] = selectedPos
    newFitness[i] = selectedFitness
    selectionCount[selection] += 1

  roundBestPlayer = np.argmin(newFitness)
  roundBestFitness = newFitness[roundBestPlayer]

  if roundBestFitness < bestFitness:
    bestFitness = roundBestFitness
    bestPos = newPos[roundBestPlayer].copy()

  roundData = {
      "parameters": parameters,
      "selectionCount": selectionCount,
      "evaluations": populationSize
  }

  return newPos, newFitness, bestPos, bestFitness, roundData


# Eliminación por estar fuera de la zona
def eliminationOutside(
    positions,
    fitness,
    bestPos,
    radiusT,
    targetPopSize,
    epsilon=1e-12 # Valor para evitar división por 0
):

  currPopSize = positions.shape[0]
  distances = np.linalg.norm(positions - bestPos, axis=1)

  outsidePlayers = np.where(distances > radiusT + epsilon)[0]

  bestPlayer = np.argmin(fitness)
  outsidePlayers = outsidePlayers[outsidePlayers != bestPlayer]

  maxStormDeaths = max(0, currPopSize - targetPopSize)
  stormDeathCount = min(outsidePlayers.size, maxStormDeaths)

  if stormDeathCount == 0:
    return positions, fitness, 0

  farthestOrder = np.argsort(distances[outsidePlayers])[::-1]
  eliminatedPlayers = outsidePlayers[farthestOrder[:stormDeathCount]]

  survivors = np.ones(currPopSize, dtype=bool)
  survivors[eliminatedPlayers] = False
  survivors[bestPlayer] = True

  survPos = positions[survivors] # NumPy se encarga de filtrar
  survFit = fitness[survivors] # Acá también

  return survPos, survFit, int(stormDeathCount)

# Calcular la cantidad máxima de gente que seguirá viva en la ronda
def calculatePopLimit(
    initPopSize,
    progress,
    eta # Coeficiente de muertes, mientrás más alta + muertes
):

  target = np.ceil(initPopSize * (1 - progress) ** eta)

  return max(1, int(target))

# Si queda más gente viva de lo que debe, se asumen muertes por combate
def eliminationCombat(
    positions,
    fitness,
    targetPopSize
):
  currentPopSize = positions.shape[0]

  # No se tiene que cambiar
  if currentPopSize <= targetPopSize:
    return positions, fitness, 0

  sortPlayers = np.argsort(fitness, kind="stable")
  survPlayers = sortPlayers[:targetPopSize]

  eliminationCount = currentPopSize - targetPopSize

  survPos = positions[survPlayers]
  survFit = fitness[survPlayers]

  return survPos, survFit, eliminationCount


# Ronda de sobrevivencia por tormenta y combate
def survivalRound(
    positions,
    fitness,
    bestPos,
    radiusT,
    initPopSize,
    progress,
    eta,
    finalIteration # Boolean
):
  targetPopSize = calculatePopLimit(
      initPopSize=initPopSize,
      progress=progress,
      eta=eta
  )

  positions, fitness, eliminatedByStorm = eliminationOutside(
      positions=positions,
      fitness=fitness,
      bestPos=bestPos,
      radiusT=radiusT,
      targetPopSize=targetPopSize
  )


  positions, fitness, eliminatedByCombat = eliminationCombat(
      positions=positions,
      fitness=fitness,
      targetPopSize=targetPopSize
  )

  survivalSummary = {
      "targetPopSize": targetPopSize,
      "eliminatedByStorm": eliminatedByStorm,
      "eliminatedByCombat": eliminatedByCombat,
      "survivorsSize": positions.shape[0]
  }

  return positions, fitness, survivalSummary


def szcoAlgorithm(
    objFunc,
    lambdaMax=1.0,
    initPopSize=100,
    alpha0=0.20,
    betaMax=0.80,
    gamma=2.50,
    eta=1.00,
    lower=None,
    upper=None,
    rng=None,
    dimension=2,
    maxIterations=100,
    stormPhases=30000000,
    rMinFactor=0.05,
):
    """Ejecuta SZCO con configuración recibida por parámetros."""
    currentLowerBound = np.asarray(
        np.full(dimension, -100.0) if lower is None else lower, dtype=float
    )
    currentUpperBound = np.asarray(
        np.full(dimension, 100.0) if upper is None else upper, dtype=float
    )
    rng = np.random.default_rng(42) if rng is None else rng
    if stormPhases < 1:
        raise ValueError("stormPhases debe ser >= 1")
    if not 0 < rMinFactor <= 1:
        raise ValueError("rMinFactor debe estar entre 0 y 1")

    # Validar
    if dimension < 1:
        raise ValueError("simulatedDimension debe ser mayor o igual a 1.")

    if initPopSize < 2:
        raise ValueError("initPopSize debe ser al menos 2.")

    if maxIterations < 1:
        raise ValueError("maxSimulationIterations debe ser al menos 1.")

    if currentLowerBound.shape != (dimension,):
        raise ValueError("lowerBound debe contener un límite por cada dimensión.")

    if currentUpperBound.shape != (dimension,):
        raise ValueError("upperBound debe contener un límite por cada dimensión.")

    if np.any(currentLowerBound >= currentUpperBound):
        raise ValueError("Cada límite inferior debe ser menor que su límite superior.")

    if lambdaMax < 0.0:
        raise ValueError("lambdaMax no puede ser negativo.")

    if alpha0 < 0.0:
        raise ValueError("alpha0 no puede ser negativo.")

    if betaMax < 0.0:
        raise ValueError(
            "betaMax no puede ser negativo."
        )

    if gamma <= 0.0:
        raise ValueError("gamma debe ser mayor que cero.")

    if eta <= 0.0:
        raise ValueError("eta debe ser mayor que cero.")

    # Inicialización
    positions, fitness = initialize(
        populationSize=initPopSize,
        dimension=dimension,
        objFunc=objFunc,
        lower=currentLowerBound,
        upper=currentUpperBound,
        rng=rng
    )

    # La inicialización evalúa a todos.
    evaluations = initPopSize

    bestPlayer = np.argmin(fitness)
    bestPos = positions[bestPlayer].copy()
    bestFitness = float(fitness[bestPlayer])

    history = []
    completedIterations = 0
    terminationReason = "max_iterations"

    # Bucle principal
    for iteration in range(1, maxIterations + 1):
        # Movimiento, evaluación y selección.
        (
            positions,
            fitness,
            bestPos,
            bestFitness,
            roundData
        ) = movementRound(
            positions=positions,
            fitness=fitness,
            bestPos=bestPos,
            bestFitness=bestFitness,
            objFunc=objFunc,
            iteration=iteration,
            maxIterations=maxIterations,
            alpha0=alpha0,
            betaMax=betaMax,
            gamma=gamma,
            lambdaMax=lambdaMax,
            rng=rng,
            lowerBound=currentLowerBound,
            upperBound=currentUpperBound,
            rMinFactor=rMinFactor,
            stormPhases=stormPhases
        )

        evaluations += int(roundData["evaluations"])
        parameters = roundData["parameters"]
        finalIteration = (iteration == maxIterations)

        # Tormenta y combate
        (
            positions,
            fitness,
            survivalData
        ) = survivalRound(
            positions=positions,
            fitness=fitness,
            bestPos=bestPos,
            radiusT=parameters["radius"],
            initPopSize=initPopSize,
            progress=parameters["progress"],
            eta=eta,
            finalIteration=finalIteration
        )

        completedIterations = iteration

        # Registro de métricas
        history.append({
            "iteration": int(iteration),
            "evaluations": int(evaluations),
            "bestFitness": float(bestFitness),
            "populationSize": int(positions.shape[0]),
            "progress": float(parameters["progress"]),
            "alpha": float(parameters["alpha"]),
            "beta": float(parameters["beta"]),
            "radius": float(parameters["radius"]),
            "lambda": float(parameters["lambda"]),
            "selectionCount": {
                key: int(value)
                for key, value in roundData[
                    "selectionCount"
                ].items()
            },
            "targetPopSize": int(survivalData["targetPopSize"]),
            "eliminatedByStorm": int(survivalData["eliminatedByStorm"]),
            "eliminatedByCombat": int(survivalData["eliminatedByCombat"]
            )
        })

        # Termination
        if positions.shape[0] == 1:
            if finalIteration:
                terminationReason = (
                    "max_iterations"
                )
            else:
                terminationReason = (
                    "single_survivor"
                )

            break

    # Results
    bestRealPos = real(bestPos, currentLowerBound, currentUpperBound)

    return {
        "best_position": bestRealPos,
        "best_normalized_position": bestPos.copy(),
        "best_fitness": float(bestFitness),
        "evaluations": int(evaluations),
        "iterations": int(completedIterations),
        "final_population_size": int(positions.shape[0]),
        "termination_reason": (terminationReason),
        "history": history
    }

