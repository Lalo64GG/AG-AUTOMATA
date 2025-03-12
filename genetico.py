import random
from afd import create_random_afd
from evaluacion import evaluate_afd

POPULATION_SIZE = 20
CXPB = 0.7  # Probabilidad de cruce
MUTPB = 0.2  # Probabilidad de mutación

def uniform_crossover(afd1, afd2):
    """Realiza un cruce uniforme entre dos AFDs."""
    child1, child2 = afd1.copy(), afd2.copy()
    for key in afd1["transitions"]:
        if random.random() < 0.5:
            child1["transitions"][key] = afd2["transitions"][key]
            child2["transitions"][key] = afd1["transitions"][key]
    return child1, child2

def mutate(afd):
    """Realiza una mutación en un AFD."""
    for key in afd["transitions"]:
        if random.random() < MUTPB:
            afd["transitions"][key] = random.choice(list(afd["states"]))
    return afd

def rank_population(population, fitnesses):
    """Ordena la población por fitness y la divide en grupos."""
    ranked = list(zip(population, fitnesses))
    ranked.sort(key=lambda x: x[1], reverse=True)

    size = len(ranked)
    best = ranked[:size // 3]
    medium = ranked[size // 3: 2 * size // 3]
    worst = ranked[2 * size // 3:]

    return best, medium, worst

def ranked_crossover(best, medium, worst):
    """Realiza cruces entre los mejores, medios y peores individuos."""
    new_population = []
    groups = [best, medium, worst]

    for group in groups:
        for i in range(0, len(group) - 1, 2):
            parent1, parent2 = group[i][0], group[i + 1][0]
            if random.random() < CXPB:
                child1, child2 = uniform_crossover(parent1, parent2)
                new_population.extend([child1, child2])
            else:
                new_population.extend([parent1, parent2])
    return new_population
