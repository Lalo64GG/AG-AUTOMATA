import random
from afd import create_random_afd
from genetico import ranked_crossover, rank_population
from evaluacion import evaluate_afd
from visualizacion import draw_afd, plot_evolution, save_afd_to_jflap
from webScrapting import get_all_conjugations

# Configuración
POPULATION_SIZE = 20
GENERATIONS = 50
ALPHABET = list("abcdefghijklmnopqrstuvwxyzáéíóúñ")


def main():
    verb = input("Ingrese un verbo en infinitivo: ").strip().lower()
    conjugations = get_all_conjugations(verb)
    
    if not conjugations:
        print("No se pudieron obtener conjugaciones.")
        return

    print(f"Se encontraron {len(conjugations)} conjugaciones.")
    
    # Cargar las conjugaciones correctas e incorrectas
    correct_conjugations = conjugations
    incorrect_conjugations = {}

    # Definir el número de estados en función de las conjugaciones
    num_states = len(conjugations) // 2

    # Crear población inicial de AFDs
    population = [create_random_afd(num_states=num_states, alphabet=ALPHABET) for _ in range(POPULATION_SIZE)]

    best_fitness_history, avg_fitness_history, error_history = [], [], []
    best_generation, best_generation_fitness, best_afd = 0, 0, None

    for generation in range(GENERATIONS):
        fitnesses = [evaluate_afd(afd, correct_conjugations, incorrect_conjugations) for afd in population]

        best_fitness = max(fitnesses)
        avg_fitness = sum(fitnesses) / len(fitnesses)
        error = len(correct_conjugations) + len(incorrect_conjugations) - best_fitness

        best_fitness_history.append(best_fitness)
        avg_fitness_history.append(avg_fitness)
        error_history.append(error)

        if best_fitness > best_generation_fitness:
            best_generation, best_generation_fitness = generation + 1, best_fitness
            best_afd = population[fitnesses.index(best_fitness)]

        best, medium, worst = rank_population(population, fitnesses)
        population = ranked_crossover(best, medium, worst)

        print(f"Generación {generation + 1}: Mejor fitness = {best_fitness}, Promedio = {avg_fitness}, Error = {error}")

    # Visualizar el mejor AFD encontrado
    draw_afd(best_afd, filename="mejor_afd")
    save_afd_to_jflap(best_afd, filename="mejor_afd.jff")
    plot_evolution(best_fitness_history, avg_fitness_history, error_history)

if __name__ == "__main__":
    main()
