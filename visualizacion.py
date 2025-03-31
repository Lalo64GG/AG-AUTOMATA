import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
import tkinter as tk
from tkinter import ttk, scrolledtext
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

def generate_transition_table(afd, conjugations=None):
    """Genera una tabla de transiciones legible con tabulate y la muestra en una ventana."""
    states = sorted(list(afd["states"]))
    
    # Determinar el alfabeto utilizado
    alphabet = sorted(set(symbol for state, symbol in afd["transitions"].keys()))
    
    # Crear ventana Tkinter
    table_window = tk.Toplevel()
    table_window.title("Detalles del Mejor AFD")
    table_window.geometry("900x700")
    
    # Crear un notebook para organizar la información en pestañas
    notebook = ttk.Notebook(table_window)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # ----- PESTAÑA 1: INFORMACIÓN GENERAL -----
    tab_info = ttk.Frame(notebook)
    notebook.add(tab_info, text="Información General")
    
    # Marco para la información principal
    info_frame = ttk.LabelFrame(tab_info, text="Datos del AFD", padding=15)
    info_frame.pack(fill=tk.X, padx=20, pady=15, anchor=tk.N)
    
    # Título
    title_label = ttk.Label(info_frame, text="AUTÓMATA FINITO DETERMINISTA", 
                           font=("Arial", 16, "bold"))
    title_label.pack(pady=10)
    
    # Información general
    ttk.Label(info_frame, text=f"Número total de estados: {len(afd['states'])}", 
             font=("Arial", 12)).pack(anchor=tk.W, pady=3)
    
    # Conjunto de todos los estados
    all_states_text = ", ".join([f'q{s}' for s in sorted(afd['states'])])
    ttk.Label(info_frame, text=f"Conjunto de estados: {all_states_text}", 
             font=("Arial", 12)).pack(anchor=tk.W, pady=3)
    
    ttk.Label(info_frame, text=f"Estado inicial: q{afd['initial_state']}", 
             font=("Arial", 12)).pack(anchor=tk.W, pady=3)
    
    final_states_text = ", ".join([f'q{s}' for s in sorted(afd['final_states'])])
    ttk.Label(info_frame, text=f"Estados finales: {final_states_text}", 
             font=("Arial", 12)).pack(anchor=tk.W, pady=3)
    
    alphabet_text = ", ".join([f"'{s}'" if s != " " else "'␣'" for s in alphabet])
    ttk.Label(info_frame, text=f"Alfabeto: {alphabet_text}", 
             font=("Arial", 12)).pack(anchor=tk.W, pady=3)
    
    # Marco para estadísticas de aceptación
    if conjugations:
        from afd import accepts_input
        
        stats_frame = ttk.LabelFrame(tab_info, text="Estadísticas de Reconocimiento", padding=15)
        stats_frame.pack(fill=tk.X, padx=20, pady=15, anchor=tk.N)
        
        # Calcular palabras aceptadas
        accepted_words = [word for word in conjugations if accepts_input(afd, word)]
        acceptance_rate = (len(accepted_words) / len(conjugations)) * 100 if conjugations else 0
        
        ttk.Label(stats_frame, text=f"Conjugaciones aceptadas: {len(accepted_words)}/{len(conjugations)}", 
                 font=("Arial", 12)).pack(anchor=tk.W, pady=3)
        
        ttk.Label(stats_frame, text=f"Tasa de aceptación: {acceptance_rate:.2f}%", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=3)
        
        # Mostrar ejemplos de palabras aceptadas y rechazadas
        examples_frame = ttk.Frame(tab_info)
        examples_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Ejemplos aceptados
        accepted_frame = ttk.LabelFrame(examples_frame, text="Ejemplos de conjugaciones aceptadas", padding=10)
        accepted_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        accepted_text = scrolledtext.ScrolledText(accepted_frame, wrap=tk.WORD, width=30, height=10)
        accepted_text.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar hasta 20 ejemplos
        for word in accepted_words[:20]:
            accepted_text.insert(tk.END, f"{word}\n")
        
        if len(accepted_words) > 20:
            accepted_text.insert(tk.END, "...\n")
        
        accepted_text.config(state=tk.DISABLED)
        
        # Ejemplos rechazados
        rejected_words = [word for word in conjugations if word not in accepted_words]
        
        rejected_frame = ttk.LabelFrame(examples_frame, text="Ejemplos de conjugaciones rechazadas", padding=10)
        rejected_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        rejected_text = scrolledtext.ScrolledText(rejected_frame, wrap=tk.WORD, width=30, height=10)
        rejected_text.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar hasta 20 ejemplos
        for word in rejected_words[:20]:
            rejected_text.insert(tk.END, f"{word}\n")
        
        if len(rejected_words) > 20:
            rejected_text.insert(tk.END, "...\n")
        
        rejected_text.config(state=tk.DISABLED)
    
    # ----- PESTAÑA 2: TABLA DE TRANSICIONES -----
    tab_table = ttk.Frame(notebook)
    notebook.add(tab_table, text="Tabla de Transiciones")
    
    # Crear tabla
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
        is_final = "✓" if state in afd["final_states"] else "✗"
        row.append(is_final)
        
        table_data.append(row)
    
    # Crear tabla con tabulate
    table_str = tabulate(table_data, headers=header, tablefmt="fancy_grid")
    
    # Mostrar tabla en un widget de texto
    table_frame = ttk.Frame(tab_table, padding=15)
    table_frame.pack(fill=tk.BOTH, expand=True)
    
    # Área de texto con scroll
    table_text = scrolledtext.ScrolledText(table_frame, wrap=tk.NONE, 
                                         font=("Courier New", 12), width=80, height=25)
    table_text.pack(fill=tk.BOTH, expand=True)
    
    # Insertar la tabla
    table_text.insert(tk.END, table_str)
    table_text.config(state=tk.DISABLED)  # Hacer de solo lectura
    
    # ----- PESTAÑA 3: LISTADO DE TRANSICIONES -----
    tab_transitions = ttk.Frame(notebook)
    notebook.add(tab_transitions, text="Listado de Transiciones")
    
    # Marco para las transiciones
    trans_frame = ttk.Frame(tab_transitions, padding=15)
    trans_frame.pack(fill=tk.BOTH, expand=True)
    
    # Área de texto con scroll
    trans_text = scrolledtext.ScrolledText(trans_frame, wrap=tk.WORD, 
                                         font=("Consolas", 12), width=80, height=25)
    trans_text.pack(fill=tk.BOTH, expand=True)
    
    # Formatear y mostrar cada transición
    trans_text.insert(tk.END, "LISTADO DETALLADO DE TRANSICIONES\n")
    trans_text.insert(tk.END, "═══════════════════════════════════\n\n")
    
    # Ordenar transiciones para mejor visualización
    transiciones_ordenadas = sorted(afd['transitions'].items(), 
                                  key=lambda x: (x[0][0], x[0][1]))
    
    for (estado_actual, simbolo), siguiente_estado in transiciones_ordenadas:
        # Formato especial para espacio
        simbolo_mostrar = simbolo if simbolo != " " else "␣"
        
        # Añadir marca si el estado siguiente es final
        es_final = " (FINAL)" if siguiente_estado in afd["final_states"] else ""
        
        linea = f"δ(q{estado_actual}, '{simbolo_mostrar}') = q{siguiente_estado}{es_final}\n"
        trans_text.insert(tk.END, linea)
    
    trans_text.config(state=tk.DISABLED)  # Hacer de solo lectura

def visualize_afd(afd, best_fitness_history=None, avg_fitness_history=None, 
                 error_history=None, diversity_history=None, conjugations=None):
    """Visualiza el AFD en ventanas de interfaz gráfica."""
    # Crear ventana principal
    root = tk.Tk()
    root.title("Visualización del AFD")
    root.geometry("400x300")
    
    # Frame principal con padding
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Etiqueta informativa
    ttk.Label(main_frame, text="Visualización del Mejor AFD", 
             font=("Arial", 16, "bold")).pack(pady=10)
    
    # Información sobre el mejor AFD
    info_text = f"Autómata con {len(afd['states'])} estados y {len(afd['final_states'])} estados finales"
    ttk.Label(main_frame, text=info_text, font=("Arial", 12)).pack(pady=5)
    
    # Frame para botones
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=20, fill=tk.X)
    
    # Botones para abrir visualizaciones
    ttk.Button(button_frame, text="Ver Detalles del AFD", 
              command=lambda: generate_transition_table(afd, conjugations)).pack(pady=10, fill=tk.X)
    
    if all(x is not None for x in [best_fitness_history, avg_fitness_history, error_history]):
        ttk.Button(button_frame, text="Ver Gráfica de Evolución", 
                  command=lambda: plot_evolution(best_fitness_history, avg_fitness_history, 
                                               error_history, diversity_history)).pack(pady=10, fill=tk.X)
    
    # Mostrar ventana de detalles automáticamente
    root.after(100, lambda: generate_transition_table(afd, conjugations))
    
    # Mostrar gráfica automáticamente si hay datos
    if all(x is not None for x in [best_fitness_history, avg_fitness_history, error_history]):
        root.after(200, lambda: plot_evolution(best_fitness_history, avg_fitness_history, 
                                             error_history, diversity_history))
    
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
    
    return tabulate(table_data, headers=header, tablefmt="fancy_grid")