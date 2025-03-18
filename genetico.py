import random
import copy

POPULATION_SIZE = 20
CXPB = 0.85
MUTPB = 0.6
ELITE_RATIO = 0.05
DIVERSITY_THRESHOLD = 0.1

def diversity_measure(afd1, afd2):
    if not afd1["transitions"] or not afd2["transitions"]:
        return 1.0
        
    total_keys = set(afd1["transitions"].keys()).union(set(afd2["transitions"].keys()))
    differences = sum(1 for key in total_keys if afd1["transitions"].get(key) != afd2["transitions"].get(key))
    
    return differences / max(1, len(total_keys))

def mutate(afd, mutation_rate=0.2):
    mutated_afd = copy.deepcopy(afd)
    
    transitions = list(mutated_afd["transitions"].keys())
    num_mutations = max(1, int(len(transitions) * mutation_rate))
    selected_keys = random.sample(transitions, min(num_mutations, len(transitions)))
    
    for key in selected_keys:
        if random.random() < 0.3:
            mutated_afd["transitions"][key] = random.choice(list(mutated_afd["states"]))
        else:
            current = mutated_afd["transitions"][key]
            available_states = [s for s in mutated_afd["states"] if s != current]
            if available_states:
                mutated_afd["transitions"][key] = random.choice(available_states)
    
    if random.random() < 0.05:
        mutated_afd["initial_state"] = random.choice(list(mutated_afd["states"]))
    
    if "final_states" in mutated_afd and random.random() < 0.1:
        final_states = list(mutated_afd["final_states"]) if isinstance(mutated_afd["final_states"], set) else mutated_afd["final_states"]
        
        for state in mutated_afd["states"]:
            if random.random() < 0.2:
                if state in final_states:
                    final_states.remove(state)
                else:
                    final_states.append(state)
        
        mutated_afd["final_states"] = set(final_states) if isinstance(mutated_afd["final_states"], set) else final_states
    
    if "accepting_states" in mutated_afd and random.random() < 0.1:
        accepting_states = list(mutated_afd["accepting_states"]) if isinstance(mutated_afd["accepting_states"], set) else mutated_afd["accepting_states"]
        
        for state in mutated_afd["states"]:
            if random.random() < 0.2:
                if state in accepting_states:
                    accepting_states.remove(state)
                else:
                    accepting_states.append(state)
        
        mutated_afd["accepting_states"] = set(accepting_states) if isinstance(mutated_afd["accepting_states"], set) else accepting_states
    
    return mutated_afd

def select_parents(population, fitnesses, conjugations):
    elite_size = max(1, int(ELITE_RATIO * len(population)))
    elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:elite_size]
    elite = [population[i] for i in elite_indices]
    
    selected = elite.copy()
    
    while len(selected) < POPULATION_SIZE:
        tournament_size = min(4, len(population))
        candidates = random.sample(range(len(population)), tournament_size)
        tournament_winner = max(candidates, key=lambda i: fitnesses[i])
        candidate = population[tournament_winner]
        
        is_diverse = all(diversity_measure(candidate, existing) >= DIVERSITY_THRESHOLD for existing in selected)
        
        if is_diverse or random.random() < 0.3:
            selected.append(candidate)
    
    return selected

def improved_crossover(afd1, afd2):
    strategy = random.choice(["one_point", "uniform", "state_swap"])
    
    child1, child2 = copy.deepcopy(afd1), copy.deepcopy(afd2)
    
    if strategy == "one_point":
        keys = list(afd1["transitions"].keys())
        if keys:
            point = random.randint(0, len(keys))
            for i, key in enumerate(keys):
                if i >= point:
                    child1["transitions"][key], child2["transitions"][key] = child2["transitions"][key], child1["transitions"][key]
    
    elif strategy == "uniform":
        for key in afd1["transitions"]:
            if random.random() < 0.5:
                child1["transitions"][key], child2["transitions"][key] = child2["transitions"][key], child1["transitions"][key]
    
    else:
        swap_state1 = random.choice(list(afd1["states"]))
        swap_state2 = random.choice(list(afd2["states"]))
        
        for key in child1["transitions"]:
            if child1["transitions"][key] == swap_state1:
                child1["transitions"][key] = swap_state2
        
        for key in child2["transitions"]:
            if child2["transitions"][key] == swap_state2:
                child2["transitions"][key] = swap_state1
    
    if "final_states" in child1 and "final_states" in child2 and random.random() < 0.5:
        child1["final_states"], child2["final_states"] = child2["final_states"], child1["final_states"]
    
    if "accepting_states" in child1 and "accepting_states" in child2 and random.random() < 0.5:
        child1["accepting_states"], child2["accepting_states"] = child2["accepting_states"], child1["accepting_states"]
    
    return child1, child2

def generate_new_population(population, fitnesses, conjugations):
    parents = select_parents(population, fitnesses, conjugations)
    
    new_population = []
    
    elite_size = max(1, int(ELITE_RATIO * len(population)))
    elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:elite_size]
    new_population.extend([population[i] for i in elite_indices])
    
    while len(new_population) < POPULATION_SIZE:
        parent1, parent2 = random.sample(parents, 2)
        
        if random.random() < CXPB:
            child1, child2 = improved_crossover(parent1, parent2)
        else:
            child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        if random.random() < MUTPB:
            diversity = diversity_measure(child1, parent1)
            mutation_rate = max(0.1, 0.5 - diversity)
            child1 = mutate(child1, mutation_rate)
            
        if random.random() < MUTPB:
            diversity = diversity_measure(child2, parent2)
            mutation_rate = max(0.1, 0.5 - diversity)
            child2 = mutate(child2, mutation_rate)
        
        new_population.append(child1)
        if len(new_population) < POPULATION_SIZE:
            new_population.append(child2)
    
    population_diversity = calculate_population_diversity(new_population)
    
    if population_diversity < 0.1:
        for i in range(elite_size, len(new_population)):
            if random.random() < 0.3:
                new_population[i] = mutate(new_population[i], mutation_rate=0.5)
    
    return new_population[:POPULATION_SIZE]

def calculate_population_diversity(population):
    if len(population) <= 1:
        return 0.0
    
    total_diversity = 0.0
    comparisons = 0
    
    for i in range(len(population)):
        for j in range(i+1, len(population)):
            total_diversity += diversity_measure(population[i], population[j])
            comparisons += 1
    
    return total_diversity / max(1, comparisons)