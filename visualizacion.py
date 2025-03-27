import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def plot_evolution(best_fitness_history, avg_fitness_history, error_history, diversity_history=None):
    """Grafica la evolución del fitness y error a lo largo de las generaciones en una ventana."""
    # Crear ventana Tkinter
    evolution_window = tk.Toplevel()
    evolution_window.title("Evolución del AFD")
    evolution_window.geometry("800x600")
    
    # Crear figura para matplotlib
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    generations = range(1, len(best_fitness_history) + 1)
    
    # Fitness (eje izquierdo)
    ax1.set_xlabel('Generación')
    ax1.set_ylabel('Fitness', color='tab:blue')
    ax1.plot(generations, best_fitness_history, 'b-', label='Mejor Fitness')
    ax1.plot(generations, avg_fitness_history, 'g-', label='Fitness Promedio')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    
    # Error (eje derecho)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Error', color='tab:red')
    ax2.plot(generations, error_history, 'r-', label='Error')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    
    # Diversidad (si está disponible)
    if diversity_history:
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position(("axes", 1.1))  # Desplazamiento del eje
        ax3.set_ylabel('Diversidad', color='tab:purple')
        ax3.plot(generations, diversity_history, 'purple', linestyle='--', label='Diversidad')
        ax3.tick_params(axis='y', labelcolor='tab:purple')
    
    # Leyenda combinada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    
    if diversity_history:
        lines3, labels3 = ax3.get_legend_handles_labels()
        ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='upper center', 
                 bbox_to_anchor=(0.5, -0.15), ncol=4)
    else:
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper center', 
                 bbox_to_anchor=(0.5, -0.15), ncol=3)
    
    plt.title('Evolución del Fitness, Error y Diversidad')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Incorporar gráfico en ventana Tkinter
    canvas = FigureCanvasTkAgg(fig, master=evolution_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def generate_transition_table(afd):
    """Genera una tabla de transiciones legible con tabulate y la muestra en una ventana."""
    states = sorted(list(afd["states"]))
    
    # Determinar el alfabeto utilizado
    alphabet = sorted(set(symbol for state, symbol in afd["transitions"].keys()))
    
    # Crear ventana Tkinter
    table_window = tk.Toplevel()
    table_window.title("Tabla de Transiciones del AFD")
    table_window.geometry("800x600")
    
    # Marco principal con scroll
    main_frame = tk.Frame(table_window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Información del AFD
    info_frame = tk.Frame(main_frame)
    info_frame.pack(fill=tk.X, pady=10)
    
    # Título
    title_label = tk.Label(info_frame, text="TABLA DE TRANSICIONES DEL AFD", 
                           font=("Arial", 16, "bold"))
    title_label.pack(pady=5)
    
    # Estado inicial y estados finales
    initial_state_label = tk.Label(info_frame, 
                                  text=f"Estado inicial: q{afd['initial_state']}", 
                                  font=("Arial", 12))
    initial_state_label.pack(anchor=tk.W)
    
    final_states_text = ", ".join([f'q{s}' for s in afd['final_states']])
    final_states_label = tk.Label(info_frame, 
                                 text=f"Estados finales: {final_states_text}", 
                                 font=("Arial", 12))
    final_states_label.pack(anchor=tk.W)
    
    alphabet_text = ", ".join([f"'{s}'" if s != " " else "'␣'" for s in alphabet])
    alphabet_label = tk.Label(info_frame, 
                             text=f"Alfabeto: {alphabet_text}", 
                             font=("Arial", 12))
    alphabet_label.pack(anchor=tk.W)
    
    # Preparar los datos para tabulate
    table_data = []
    header = ["Estado"] + alphabet + ["Estado Final"]
    
    for state in states:
        row = [f"q{state}"]
        
        # Añadir transiciones para cada símbolo
        for symbol in alphabet:
            next_state = afd["transitions"].get((state, symbol), "-")
            if next_state != "-":
                next_state = f"q{next_state}"
            row.append(next_state)
        
        # Marcar si es estado final
        is_final = "Sí" if state in afd["final_states"] else "No"
        row.append(is_final)
        
        table_data.append(row)
    
    # Crear tabla con tabulate
    table_str = tabulate(table_data, headers=header, tablefmt="fancy_grid")
    
    # Mostrar tabla en un widget de texto
    text_frame = tk.Frame(main_frame)
    text_frame.pack(fill=tk.BOTH, expand=True)
    
    # Scroll vertical
    scrollbar_y = tk.Scrollbar(text_frame)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Scroll horizontal
    scrollbar_x = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Área de texto con fuente monoespaciada para mantener el formato de tabulate
    text_area = tk.Text(text_frame, wrap=tk.NONE, 
                       font=("Courier New", 12),
                       yscrollcommand=scrollbar_y.set,
                       xscrollcommand=scrollbar_x.set)
    text_area.pack(fill=tk.BOTH, expand=True)
    
    # Vincular scrollbars
    scrollbar_y.config(command=text_area.yview)
    scrollbar_x.config(command=text_area.xview)
    
    # Insertar la tabla
    text_area.insert(tk.END, table_str)
    text_area.config(state=tk.DISABLED)  # Hacer de solo lectura

def visualize_afd(afd, best_fitness_history=None, avg_fitness_history=None, 
                 error_history=None, diversity_history=None):
    """Visualiza el AFD en ventanas de interfaz gráfica."""
    # Crear ventana principal
    root = tk.Tk()
    root.title("Visualización del AFD")
    root.geometry("300x200")
    
    # Etiqueta informativa
    tk.Label(root, text="Visualización del AFD", font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(root, text="Se han abierto ventanas adicionales\ncon la tabla y la gráfica de evolución").pack(pady=10)
    
    # Botones para abrir visualizaciones
    tk.Button(root, text="Ver Tabla de Transiciones", 
             command=lambda: generate_transition_table(afd)).pack(pady=5, fill=tk.X, padx=50)
    
    if all(x is not None for x in [best_fitness_history, avg_fitness_history, error_history]):
        tk.Button(root, text="Ver Gráfica de Evolución", 
                 command=lambda: plot_evolution(best_fitness_history, avg_fitness_history, 
                                              error_history, diversity_history)).pack(pady=5, fill=tk.X, padx=50)
    
    # Mostrar ventanas iniciales
    generate_transition_table(afd)
    if all(x is not None for x in [best_fitness_history, avg_fitness_history, error_history]):
        plot_evolution(best_fitness_history, avg_fitness_history, error_history, diversity_history)
    
    # Mantener la interfaz ejecutándose
    root.mainloop()

# Para cuando solo quieres mostrar la tabla de transiciones sin interfaz gráfica
def print_transition_table(afd):
    """Imprime la tabla de transiciones usando tabulate en la consola."""
    states = sorted(list(afd["states"]))
    alphabet = sorted(set(symbol for state, symbol in afd["transitions"].keys()))
    
    table_data = []
    header = ["Estado"] + alphabet + ["Estado Final"]
    
    for state in states:
        row = [f"q{state}"]
        
        # Añadir transiciones para cada símbolo
        for symbol in alphabet:
            next_state = afd["transitions"].get((state, symbol), "-")
            if next_state != "-":
                next_state = f"q{next_state}"
            row.append(next_state)
        
        # Marcar si es estado final
        is_final = "Sí" if state in afd["final_states"] else "No"
        row.append(is_final)
        
        table_data.append(row)