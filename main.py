import random
from afd import create_random_afd, accepts_input
from genetico import generate_new_population, calculate_population_diversity
from evaluacion import evaluate_afd
from visualizacion import plot_evolution, generate_transition_table
from webScrapting import get_all_conjugations


# Configuración
POPULATION_SIZE = 20
GENERATIONS = 50
ALPHABET = list("abcdefghijklmnopqrstuvwxyzáéíóúñ")


def main():

    print("🔵 El script ha iniciado correctamente.")
    verb = input("Ingrese un verbo en infinitivo: ").strip().lower()


    conjugations = get_all_conjugations(verb)

    if not conjugations:
        print("No se pudieron obtener conjugaciones.")
        return

    print(f"Se encontraron {len(conjugations)} conjugaciones.")

    # Definir el número de estados adaptativo
    num_states = max(3, min(len(conjugations) // 3, 10))  # Entre 3 y 10 estados

    # Crear población inicial de AFDs
    population = [create_random_afd(num_states=num_states, alphabet=ALPHABET) for _ in range(POPULATION_SIZE)]

    best_fitness_history, avg_fitness_history, error_history, diversity_history = [], [], [], []
    best_generation, best_generation_fitness, best_afd = 0, float('-inf'), None
    global_best_fitness = float('-inf')

    # Variables para monitorear estancamiento
    stagnation_counter = 0
    last_best_fitness = -1
    plateau_threshold = 15  # Número de generaciones sin mejora antes de aplicar medidas
    
    # Variables para reinicio parcial
    restart_threshold = 25  # Número de generaciones sin mejora antes de reinicio parcial
    num_restarts = 0
    max_restarts = 3  # Máximo número de reinicios

    for generation in range(GENERATIONS):
        # Evaluar la población considerando diversidad
        fitnesses = [evaluate_afd(afd, conjugations, population) for afd in population]
        
        # Calcular diversidad de la población
        population_diversity = calculate_population_diversity(population)
        diversity_history.append(population_diversity)
        
        # Estadísticas de la generación
        best_fitness = max(fitnesses)
        best_idx = fitnesses.index(best_fitness)
        avg_fitness = sum(fitnesses) / len(fitnesses)
        error = 1 - best_fitness
        
        # Registrar historia
        best_fitness_history.append(best_fitness)
        avg_fitness_history.append(avg_fitness)
        error_history.append(error)
        
        # Actualizar el mejor AFD global
        if best_fitness > global_best_fitness:
            best_generation, global_best_fitness = generation + 1, best_fitness
            best_afd = population[best_idx]
            stagnation_counter = 0
        else:
            stagnation_counter += 1
            
        # Mostrar información de la generación
        print(f"Generación {generation + 1}:")
        print(f"  Mejor fitness = {best_fitness:.4f}")
        print(f"  Promedio = {avg_fitness:.4f}")
        print(f"  Error = {error:.4f}")
        print(f"  Diversidad población = {population_diversity:.4f}")
        print(f"  Palabras aceptadas: {sum(accepts_input(population[best_idx], w) for w in conjugations)}/{len(conjugations)}")
        
        # Verificar estancamiento y aplicar medidas
        if stagnation_counter >= plateau_threshold:
            print(f"Estancamiento detectado: {stagnation_counter} generaciones sin mejora")
            
            # Si llegamos al umbral de reinicio parcial
            if stagnation_counter >= restart_threshold and num_restarts < max_restarts:
                print(f"⚠️ Realizando reinicio parcial de la población (reinicio #{num_restarts+1})")
                
                # Preservar el mejor AFD global
                preserved = [best_afd]
                
                # Crear nuevos individuos aleatorios para el 60% de la población
                replacement_size = int(0.6 * POPULATION_SIZE)
                new_individuals = [
                    create_random_afd(num_states=num_states, alphabet=ALPHABET) 
                    for _ in range(replacement_size)
                ]
                
                # Mantener el 40% restante (los mejores de la población actual)
                keep_size = POPULATION_SIZE - replacement_size - len(preserved)
                remaining_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:keep_size]
                remaining = [population[i] for i in remaining_indices]
                
                # Combinar en la nueva población
                population = preserved + remaining + new_individuals
                
                # Reiniciar contador de estancamiento y actualizar contadores
                stagnation_counter = 0
                num_restarts += 1
                continue  # Saltar a la siguiente generación
        
        # Generar nueva población con mecanismos de diversidad
        population = generate_new_population(population, fitnesses, conjugations)
        
        # Terminar si hemos alcanzado una solución perfecta
        if best_fitness > 0.99:
            print("¡Solución óptima encontrada!")
            break
            
        # Terminar si hemos agotado los reinicios y seguimos estancados
        if num_restarts >= max_restarts and stagnation_counter >= restart_threshold:
            print(f"Terminando después de {num_restarts} reinicios sin mejora significativa.")
            break

    # Resultados finales
    print(f"\nMejor generación: {best_generation} con fitness {global_best_fitness:.4f}")
    correct_words = sum(accepts_input(best_afd, word) for word in conjugations)
    print(f"El mejor AFD acepta {correct_words} de {len(conjugations)} conjugaciones ({correct_words/len(conjugations)*100:.2f}%)")
    
    # Graficar con información de diversidad
    plot_evolution(best_fitness_history, avg_fitness_history, error_history, diversity_history)
    generate_transition_table(best_afd)
    

if __name__ == "__main__":
    main()
