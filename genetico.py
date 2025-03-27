import random
import copy
from afd import create_random_afd
from evaluacion import evaluate_afd

# Parámetros optimizados
POPULATION_SIZE = 40
CXPB = 0.90          # Incrementada la probabilidad de cruce
MUTPB = 0.75         # Incrementada la probabilidad de mutación
ELITE_RATIO = 0.10   # Incrementado el elitismo al 10%
DIVERSITY_THRESHOLD = 0.15  # Incrementado el umbral de diversidad

# Función para medir la diversidad entre dos AFDs
def diversity_measure(afd1, afd2):
    """Calcula qué tan diferentes son dos AFDs basado en sus transiciones."""
    if not afd1["transitions"] or not afd2["transitions"]:
        return 1.0  # Máxima diversidad si no hay transiciones
        
    # Contar diferencias en las transiciones
    total_keys = set(afd1["transitions"].keys()).union(set(afd2["transitions"].keys()))
    differences = 0
    
    for key in total_keys:
        val1 = afd1["transitions"].get(key, None)
        val2 = afd2["transitions"].get(key, None)
        if val1 != val2:
            differences += 1
    
    # Normalizar por el número total de transiciones
    return differences / max(1, len(total_keys))

# Mutación más agresiva para explorar más el espacio de soluciones
def mutate(afd, mutation_rate=0.3):  # Incrementada la tasa base de mutación
    """Realiza mutación con intensidad variable según el contexto."""
    # Copia profunda para evitar modificar el original
    mutated_afd = copy.deepcopy(afd)
    
    # Número de mutaciones basado en el tamaño del AFD y la tasa de mutación
    transitions = list(mutated_afd["transitions"].keys())
    num_mutations = max(2, int(len(transitions) * mutation_rate))  # Mínimo 2 mutaciones
    
    # Seleccionar transiciones a mutar
    selected_keys = random.sample(transitions, min(num_mutations, len(transitions)))
    
    for key in selected_keys:
        # 40% del tiempo: mutación completamente aleatoria
        if random.random() < 0.4:  # Incrementado de 30% a 40%
            mutated_afd["transitions"][key] = random.choice(list(mutated_afd["states"]))
        else:
            # 60% del tiempo: cambio inteligente que evita el estado actual
            current = mutated_afd["transitions"][key]
            available_states = [s for s in mutated_afd["states"] if s != current]
            if available_states:  # Si hay otros estados disponibles
                mutated_afd["transitions"][key] = random.choice(available_states)
    
    # Probabilidad incrementada de mutar el estado inicial
    if random.random() < 0.10:  # Incrementado de 5% a 10%
        mutated_afd["initial_state"] = random.choice(list(mutated_afd["states"]))
    
    # Probabilidad incrementada de cambiar estados de aceptación/finales
    if "final_states" in mutated_afd and random.random() < 0.15:  # Incrementado de 10% a 15%
        # Convertir a lista si es un conjunto para poder modificarlo
        final_states = list(mutated_afd["final_states"]) if isinstance(mutated_afd["final_states"], set) else mutated_afd["final_states"]
        
        for state in mutated_afd["states"]:
            if random.random() < 0.25:  # Incrementado de 20% a 25%
                if state in final_states:
                    final_states.remove(state)
                else:
                    final_states.append(state)
        
        # Asegurarnos de que haya al menos un estado final
        if not final_states:
            final_states.append(random.choice(list(mutated_afd["states"])))
            
        # Volver a guardar el conjunto actualizado
        mutated_afd["final_states"] = set(final_states) if isinstance(mutated_afd["final_states"], set) else final_states
    
    # Lo mismo para accepting_states si existe
    if "accepting_states" in mutated_afd and random.random() < 0.15:  # Incrementado de 10% a 15%
        accepting_states = list(mutated_afd["accepting_states"]) if isinstance(mutated_afd["accepting_states"], set) else mutated_afd["accepting_states"]
        
        for state in mutated_afd["states"]:
            if random.random() < 0.25:  # Incrementado de 20% a 25%
                if state in accepting_states:
                    accepting_states.remove(state)
                else:
                    accepting_states.append(state)
        
        # Asegurarnos de que haya al menos un estado de aceptación
        if not accepting_states:
            accepting_states.append(random.choice(list(mutated_afd["states"])))
            
        mutated_afd["accepting_states"] = set(accepting_states) if isinstance(mutated_afd["accepting_states"], set) else accepting_states
    
    return mutated_afd

# Mejorar selección de padres con diversidad
def select_parents(population, fitnesses, conjugations):
    """Selecciona padres priorizando fitness pero manteniendo diversidad."""
    # Primero seleccionamos la élite por fitness
    elite_size = max(1, int(ELITE_RATIO * len(population)))
    elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:elite_size]
    elite = [population[i] for i in elite_indices]
    
    # Seleccionamos el resto mediante torneo con presión por diversidad
    selected = elite.copy()
    
    # Aseguramos que elegimos suficientes padres
    while len(selected) < POPULATION_SIZE:
        # Selección por torneo
        tournament_size = min(5, len(population))  # Incrementado de 4 a 5
        candidates = random.sample(range(len(population)), tournament_size)
        
        # Elegimos el mejor de los candidatos
        tournament_winner = max(candidates, key=lambda i: fitnesses[i])
        candidate = population[tournament_winner]
        
        # Verificar diversidad con respecto a los ya seleccionados
        is_diverse = True
        for existing in selected:
            if diversity_measure(candidate, existing) < DIVERSITY_THRESHOLD:
                is_diverse = False
                break
        
        # Aceptar si es diverso o con probabilidad decreciente
        if is_diverse or random.random() < 0.4:  # Incrementado de 30% a 40% para aceptar más variedad
            selected.append(candidate)
    
    return selected

# Mejorar el cruce con más variedad
def improved_crossover(afd1, afd2):
    """Implementa múltiples estrategias de cruce y elige una aleatoriamente."""
    # Más peso a estrategias que producen mayor diversidad
    strategy_weights = {"one_point": 20, "uniform": 50, "state_swap": 30}
    strategies = list(strategy_weights.keys())
    weights = [strategy_weights[s] for s in strategies]
    
    # Selección ponderada de estrategia
    strategy = random.choices(strategies, weights=weights, k=1)[0]
    
    child1, child2 = copy.deepcopy(afd1), copy.deepcopy(afd2)
    
    if strategy == "one_point":
        # Cruce de un punto tradicional
        keys = list(afd1["transitions"].keys())
        if keys:
            point = random.randint(0, len(keys))
            for i, key in enumerate(keys):
                if i >= point:
                    child1["transitions"][key], child2["transitions"][key] = child2["transitions"][key], child1["transitions"][key]
    
    elif strategy == "uniform":
        # Cruce uniforme mejorado con probabilidad variable
        exchange_prob = random.uniform(0.4, 0.6)  # Probabilidad de intercambio variable
        for key in afd1["transitions"]:
            if random.random() < exchange_prob:
                child1["transitions"][key], child2["transitions"][key] = child2["transitions"][key], child1["transitions"][key]
    
    else:  # state_swap
        # Intercambio de estados completos (más disruptivo)
        # Ahora intercambiamos varios estados en lugar de solo uno
        num_states_to_swap = random.randint(1, min(3, len(afd1["states"]) // 3))
        
        for _ in range(num_states_to_swap):
            swap_state1 = random.choice(list(afd1["states"]))
            swap_state2 = random.choice(list(afd2["states"]))
            
            # Intercambiar todas las transiciones que van a estos estados
            for key in child1["transitions"]:
                if child1["transitions"][key] == swap_state1:
                    child1["transitions"][key] = swap_state2
            
            for key in child2["transitions"]:
                if child2["transitions"][key] == swap_state2:
                    child2["transitions"][key] = swap_state1
    
    # Intercambiar estados finales con probabilidad incrementada
    if "final_states" in child1 and "final_states" in child2 and random.random() < 0.7:  # Incrementado de 50% a 70%
        child1["final_states"], child2["final_states"] = child2["final_states"], child1["final_states"]
    
    # Alternativa si usa accepting_states
    if "accepting_states" in child1 and "accepting_states" in child2 and random.random() < 0.7:  # Incrementado de 50% a 70%
        child1["accepting_states"], child2["accepting_states"] = child2["accepting_states"], child1["accepting_states"]
    
    return child1, child2

# Función principal de generación de población mejorada
def generate_new_population(population, fitnesses, conjugations):
    """Crea una nueva población con mecanismos mejorados para mantener diversidad."""
    # 1. Seleccionar padres
    parents = select_parents(population, fitnesses, conjugations)
    
    # 2. Crear nueva población
    new_population = []
    
    # Preservar la élite
    elite_size = max(1, int(ELITE_RATIO * len(population)))
    elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:elite_size]
    new_population.extend([population[i] for i in elite_indices])
    
    # Crear nuevos individuos mediante cruce y mutación
    while len(new_population) < POPULATION_SIZE:
        # Seleccionar dos padres diferentes
        parent1, parent2 = random.sample(parents, 2)
        
        # Aplicar cruce con alta probabilidad
        if random.random() < CXPB:
            child1, child2 = improved_crossover(parent1, parent2)
        else:
            child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        # Aplicar mutación con probabilidad variable
        if random.random() < MUTPB:
            # Mayor tasa de mutación si hay poca diversidad
            diversity = diversity_measure(child1, parent1)
            mutation_rate = max(0.15, 0.6 - diversity)  # Entre 15% y 60% (incrementado)
            child1 = mutate(child1, mutation_rate)
            
        if random.random() < MUTPB:
            diversity = diversity_measure(child2, parent2)
            mutation_rate = max(0.15, 0.6 - diversity)  # Entre 15% y 60% (incrementado)
            child2 = mutate(child2, mutation_rate)
        
        # Añadir hijos a la nueva población
        new_population.append(child1)
        if len(new_population) < POPULATION_SIZE:
            new_population.append(child2)
    
    # Asegurar diversidad en la población final
    population_diversity = calculate_population_diversity(new_population)
    
    # Si la diversidad es muy baja, introducir mutaciones más agresivas
    if population_diversity < 0.15:  # Umbral de diversidad crítica incrementado
        # Reemplazar algunos individuos (excepto la élite) con mutaciones agresivas
        for i in range(elite_size, len(new_population)):
            if random.random() < 0.4:  # Incrementado de 30% a 40% para más intervenciones
                new_population[i] = mutate(new_population[i], mutation_rate=0.7)  # Incrementado a 70%
    
    return new_population[:POPULATION_SIZE]

# Función para calcular la diversidad de toda la población
def calculate_population_diversity(population):
    """Calcula la diversidad promedio entre todos los pares de individuos."""
    if len(population) <= 1:
        return 0.0
    
    total_diversity = 0.0
    comparisons = 0
    
    # Comparar cada par de individuos
    for i in range(len(population)):
        for j in range(i+1, len(population)):
            total_diversity += diversity_measure(population[i], population[j])
            comparisons += 1
    
    return total_diversity / max(1, comparisons)