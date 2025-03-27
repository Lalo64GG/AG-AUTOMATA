import random
import tkinter as tk
from tkinter import ttk, messagebox, StringVar
from threading import Thread
import time

from afd import create_random_afd, accepts_input
from genetico import generate_new_population, calculate_population_diversity
from evaluacion import evaluate_afd
from visualizacion import visualize_afd
from webScrapting import get_all_conjugations


# Configuración optimizada
POPULATION_SIZE = 40
GENERATIONS = 150
ALPHABET = list("abcdefghijklmnopqrstuvwxyzáéíóúñ ")


class AFDGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador AFD para Verbos")
        self.root.geometry("500x300")
        self.root.resizable(True, True)
        
        self.setup_ui()
        
        # Variables para el algoritmo
        self.conjugations = []
        self.best_afd = None
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.error_history = []
        self.diversity_history = []
        
        # Variable para controlar actualizaciones de estado
        self.is_running = False
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Generador de AFD para Verbos", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Área de entrada
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        verb_label = ttk.Label(input_frame, text="Ingrese un verbo en infinitivo:", 
                             font=("Arial", 12))
        verb_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.verb_var = StringVar()
        self.verb_entry = ttk.Entry(input_frame, textvariable=self.verb_var, 
                                  font=("Arial", 12), width=20)
        self.verb_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.verb_entry.focus()
        
        # Botón de inicio
        start_button = ttk.Button(main_frame, text="Generar AFD", 
                                command=self.start_afd_generation)
        start_button.pack(pady=20)
        
        # Área de estado
        self.status_frame = ttk.LabelFrame(main_frame, text="Estado", padding=10)
        self.status_frame.pack(fill=tk.X, pady=10, expand=True)
        
        self.status_label = ttk.Label(self.status_frame, 
                                    text="Esperando inicio...", 
                                    font=("Arial", 10))
        self.status_label.pack(fill=tk.X)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_frame, 
                                          orient=tk.HORIZONTAL, 
                                          length=300, 
                                          mode='determinate',
                                          variable=self.progress_var)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Vincular Enter a la generación del AFD
        self.verb_entry.bind('<Return>', lambda event: self.start_afd_generation())
        
    def start_afd_generation(self):
        # Verificar que no esté ya en ejecución
        if self.is_running:
            return
            
        # Obtener el verbo
        verb = self.verb_var.get().strip().lower()
        
        if not verb:
            messagebox.showerror("Error", "Por favor ingrese un verbo")
            return
            
        if not verb.endswith(('ar', 'er', 'ir')):
            messagebox.showwarning("Advertencia", 
                                 "El texto ingresado no parece ser un verbo en infinitivo.\n"
                                 "Debe terminar en 'ar', 'er' o 'ir'.")
            return
        
        # Iniciar proceso en un hilo separado
        self.is_running = True
        self.progress_var.set(0)
        self.update_status("Iniciando proceso de generación...")
        
        # Deshabilitar entrada y botón
        self.verb_entry.config(state="disabled")
        
        # Iniciar hilo
        thread = Thread(target=self.run_afd_generation, args=(verb,))
        thread.daemon = True
        thread.start()
    
    def run_afd_generation(self, verb):
        try:
            self.update_status(f"Obteniendo conjugaciones para '{verb}'...")
            
            # Obtener conjugaciones
            self.conjugations = get_all_conjugations(verb)
            
            if not self.conjugations:
                self.update_status("No se pudieron obtener conjugaciones.")
                messagebox.showerror("Error", "No se pudieron obtener conjugaciones para este verbo.")
                self.is_running = False
                self.verb_entry.config(state="normal")
                return
            
            self.update_status(f"Se encontraron {len(self.conjugations)} conjugaciones.")
            time.sleep(0.5)  # Dar tiempo para leer el mensaje
            
            # Configurar el número de estados
            num_states = max(8, min(len(self.conjugations) // 2, 20))
            self.update_status(f"Configurando AFD con {num_states} estados.")
            
            # Inicializar variables para el algoritmo
            self.best_fitness_history = []
            self.avg_fitness_history = []
            self.error_history = []
            self.diversity_history = []
            
            # Crear población inicial
            self.update_status("Creando población inicial...")
            initial_population_size = int(POPULATION_SIZE * 1.3)
            initial_population = [create_random_afd(num_states=num_states, alphabet=ALPHABET) 
                                for _ in range(initial_population_size)]
            
            # Evaluar población inicial
            self.update_status("Evaluando población inicial...")
            initial_fitnesses = [evaluate_afd(afd, self.conjugations) for afd in initial_population]
            
            # Seleccionar mejores individuos
            selected_indices = sorted(range(len(initial_fitnesses)), 
                                    key=lambda i: initial_fitnesses[i], 
                                    reverse=True)[:POPULATION_SIZE]
            population = [initial_population[i] for i in selected_indices]
            
            # Variables de seguimiento
            best_generation, global_best_fitness, self.best_afd = 0, float('-inf'), None
            stagnation_counter = 0
            plateau_threshold = 15
            restart_threshold = 25
            num_restarts = 0
            max_restarts = 7
            
            # Ejecutar algoritmo genético
            for generation in range(GENERATIONS):
                # Actualizar barra de progreso
                progress = (generation + 1) / GENERATIONS * 100
                self.progress_var.set(progress)
                
                # Evaluar población
                fitnesses = [evaluate_afd(afd, self.conjugations, population) for afd in population]
                
                # Calcular diversidad
                population_diversity = calculate_population_diversity(population)
                self.diversity_history.append(population_diversity)
                
                # Estadísticas
                best_fitness = max(fitnesses)
                best_idx = fitnesses.index(best_fitness)
                avg_fitness = sum(fitnesses) / len(fitnesses)
                error = 1 - best_fitness
                
                # Registrar historia
                self.best_fitness_history.append(best_fitness)
                self.avg_fitness_history.append(avg_fitness)
                self.error_history.append(error)
                
                # Actualizar el mejor AFD global
                if best_fitness > global_best_fitness:
                    best_generation, global_best_fitness = generation + 1, best_fitness
                    self.best_afd = population[best_idx]
                    stagnation_counter = 0
                else:
                    stagnation_counter += 1
                
                # Contar palabras aceptadas
                correct_words = sum(accepts_input(population[best_idx], w) for w in self.conjugations)
                acceptance_rate = (correct_words / len(self.conjugations)) * 100
                
                # Actualizar estado
                self.update_status(f"Generación {generation + 1}/{GENERATIONS}: "
                                 f"Fitness={best_fitness:.4f}, "
                                 f"Aceptación={acceptance_rate:.2f}%")
                
                # Si alcanzamos el 100%, terminar
                if acceptance_rate == 100.0:
                    self.update_status("¡Solución perfecta encontrada con 100% de acierto!")
                    best_generation, global_best_fitness = generation + 1, best_fitness
                    self.best_afd = population[best_idx]
                    break
                
                # Verificar estancamiento
                if stagnation_counter >= plateau_threshold:
                    self.update_status(f"Estancamiento: {stagnation_counter} generaciones sin mejora")
                    
                    if stagnation_counter >= restart_threshold and num_restarts < max_restarts:
                        self.update_status(f"Realizando reinicio parcial #{num_restarts+1}")
                        
                        # Preservar el mejor AFD
                        preserved = [self.best_afd]
                        
                        # Estrategia agresiva: nuevo 70% de la población
                        replacement_size = int(0.7 * POPULATION_SIZE)
                        
                        # Nuevos individuos con estados variables
                        new_individuals = []
                        for _ in range(replacement_size):
                            state_variation = random.randint(-2, 4)
                            new_num_states = max(5, min(num_states + state_variation, 25))
                            new_individuals.append(
                                create_random_afd(num_states=new_num_states, alphabet=ALPHABET)
                            )
                        
                        # Mantener mejores 30%
                        keep_size = POPULATION_SIZE - replacement_size - len(preserved)
                        remaining_indices = sorted(range(len(fitnesses)), 
                                                key=lambda i: fitnesses[i], 
                                                reverse=True)[:keep_size]
                        remaining = [population[i] for i in remaining_indices]
                        
                        # Nueva población
                        population = preserved + remaining + new_individuals
                        
                        # Reiniciar contador
                        stagnation_counter = 0
                        num_restarts += 1
                        continue
                
                # Generar nueva población
                population = generate_new_population(population, fitnesses, self.conjugations)
                
                # Terminar si fitness excepcional
                if best_fitness > 0.995:
                    self.update_status("¡Solución óptima encontrada con fitness excepcional!")
                    break
                
                # Terminar si agotamos reinicios y seguimos estancados
                if num_restarts >= max_restarts and stagnation_counter >= restart_threshold:
                    self.update_status("Intentando una última estrategia con más estados...")
                    
                    # Preservar mejor AFD
                    best_so_far = self.best_afd
                    
                    # Nuevos AFDs con más estados
                    increased_states = num_states + 5
                    new_population = [create_random_afd(num_states=increased_states, alphabet=ALPHABET) 
                                    for _ in range(POPULATION_SIZE-1)]
                    
                    # Añadir el mejor AFD
                    new_population.insert(0, best_so_far)
                    
                    # Reemplazar población
                    population = new_population
                    stagnation_counter = 0
                    num_restarts = max_restarts
                    continue
            
            # Resultados finales
            self.progress_var.set(100)
            correct_words = sum(accepts_input(self.best_afd, w) for w in self.conjugations)
            acceptance_rate = (correct_words / len(self.conjugations)) * 100
            
            final_message = (f"Mejor generación: {best_generation} con fitness {global_best_fitness:.4f}\n"
                           f"Aceptación: {correct_words}/{len(self.conjugations)} conjugaciones ({acceptance_rate:.2f}%)")
            
            self.update_status(final_message)
            
            # Mostrar tablas y gráficas
            self.root.after(500, lambda: self.show_visualizations())
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Se produjo un error durante la generación:\n{str(e)}")
        finally:
            self.is_running = False
            self.verb_entry.config(state="normal")
    
    def update_status(self, message):
        """Actualiza el mensaje de estado desde cualquier hilo"""
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def show_visualizations(self):
        """Muestra las visualizaciones del AFD"""
        if not self.best_afd:
            messagebox.showerror("Error", "No se generó ningún AFD válido")
            return
            
        visualize_afd(self.best_afd, 
                     self.best_fitness_history, 
                     self.avg_fitness_history, 
                     self.error_history, 
                     self.diversity_history)


def main():
    root = tk.Tk()
    app = AFDGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()