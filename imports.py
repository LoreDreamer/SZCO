"""Ejecuta las pruebas de SZCO. Edita los parámetros en main()."""
import numpy as np
from szco import szcoAlgorithm, sphere, rastrigin, rosenbrock


def main():
    # ============ PARÁMETROS EDITABLES ============
    dimension = 2
    max_iterations = 100
    population_size = 100
    seed = 42
    alpha0 = 0.20
    beta_max = 0.80
    gamma = 2.50
    eta = 1.00
    lambda_max = 1.0
    storm_phases = 300
    r_min_factor = 0.05

    # Cada benchmark usa sus propios límites reales.
    pruebas = [
        ("Sphere", sphere, -100.0, 100.0),
        ("Rastrigin", rastrigin, -5.12, 5.12),
        ("Rosenbrock", rosenbrock, -30.0, 30.0),
    ]

    for nombre, objetivo, minimo, maximo in pruebas:
        resultado = szcoAlgorithm(
            objFunc=objetivo,
            dimension=dimension,
            maxIterations=max_iterations,
            initPopSize=population_size,
            alpha0=alpha0,
            betaMax=beta_max,
            gamma=gamma,
            eta=eta,
            lambdaMax=lambda_max,
            stormPhases=storm_phases,
            rMinFactor=r_min_factor,
            lower=np.full(dimension, minimo),
            upper=np.full(dimension, maximo),
            rng=np.random.default_rng(seed),
        )
        historial = resultado["history"]
        suma = lambda key: sum(h[key] for h in historial)
        greedy = sum(h["selectionCount"]["accepted_greedy"] for h in historial)
        safety = sum(h["selectionCount"]["accepted_safety"] for h in historial)
        print(f"\n--- {nombre} ---")
        print(f"Mejor fitness: {resultado['best_fitness']:.12e}")
        print(f"Mejor posición: {resultado['best_position']}")
        print(f"Evaluaciones: {resultado['evaluations']}")
        print(f"Iteraciones: {resultado['iterations']}")
        print(f"Población final: {resultado['final_population_size']}")
        print(f"Terminación: {resultado['termination_reason']}")
        print(f"Greedy: {greedy}; Seguridad: {safety}")
        print(f"Tormenta: {suma('eliminatedByStorm')}; Combate: {suma('eliminatedByCombat')}")


if __name__ == "__main__":
    main()
