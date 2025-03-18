import matplotlib.pyplot as plt
# from graphviz import Digraph
import xml.etree.ElementTree as ET
import pandas as pd


def plot_evolution(best_fitness_history, avg_fitness_history, error_history, diversity_history=None):
    """
    Grafica la evolución del fitness y el error a lo largo de las generaciones.
    
    Args:
        best_fitness_history: Lista con el mejor fitness de cada generación
        avg_fitness_history: Lista con el fitness promedio de cada generación
        error_history: Lista con el error de cada generación
        diversity_history: Lista con la diversidad de la población de cada generación (opcional)
    """
    import matplotlib.pyplot as plt
    
    if diversity_history is not None:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    else:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    generations = range(1, len(best_fitness_history) + 1)
    ax1.plot(generations, best_fitness_history, 'b-', label='Mejor Fitness')
    ax1.plot(generations, avg_fitness_history, 'g-', label='Fitness Promedio')
    ax1.set_ylabel('Fitness')
    ax1.set_title('Evolución del Fitness')
    ax1.legend()
    ax1.grid(True)
    
    ax2.plot(generations, error_history, 'r-', label='Error')
    ax2.set_ylabel('Error')
    ax2.set_title('Evolución del Error')
    ax2.legend()
    ax2.grid(True)
    
    if diversity_history is not None:
        ax3.plot(generations, diversity_history, 'm-', label='Diversidad')
        ax3.set_ylabel('Diversidad')
        ax3.set_xlabel('Generación')
        ax3.set_title('Evolución de la Diversidad')
        ax3.legend()
        ax3.grid(True)
    else:
        ax2.set_xlabel('Generación')
    
    plt.tight_layout()
    plt.savefig('evolucion.png')
    plt.show()

def generate_transition_table(afd):
    """Genera una tabla de transiciones visual usando Matplotlib e incluye los estados en texto."""
    states = sorted(afd["states"])
    symbols = sorted(set(symbol for _, symbol in afd["transitions"]))


    table_data = []
    for state in states:
        row = [f"→ {state}" if state == afd["initial_state"] else 
               f"*{state}" if state in afd["final_states"] else 
               str(state)] 
        
        for symbol in symbols:
            next_state = afd["transitions"].get((state, symbol), "-") 
            row.append(next_state)
        table_data.append(row)

    df = pd.DataFrame(table_data, columns=["Estado"] + symbols)

    fig, ax = plt.subplots(figsize=(len(symbols) + 4, len(states) + 3))
    ax.axis('tight')
    ax.axis('off')

    ax.table(cellText=df.values, colLabels=df.columns, cellLoc="center", loc="center")

    info_text = (
        f"Conjunto de Estados: {', '.join(map(str, afd['states']))}\n"
        f"Estados Finales: {', '.join(map(str, afd['final_states']))}\n"
        f"Estado Inicial: {afd['initial_state']}"
    )
    
    plt.figtext(0.5, 0.02, info_text, fontsize=10, ha="center", bbox={"facecolor":"white", "alpha":0.6, "pad":5})

    plt.title("Tabla de Transiciones del AFD", fontsize=14, fontweight="bold")

    plt.show()