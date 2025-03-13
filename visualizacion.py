import matplotlib.pyplot as plt
# from graphviz import Digraph
import xml.etree.ElementTree as ET
import pandas as pd


# def draw_afd(afd, filename="afd"):
#     print("Generando gráfico del AFD...", afd)

#     dot = Digraph(comment="AFD Generado", format="png")
#     dot.attr(rankdir="LR")  # Orientación de izquierda a derecha

#     # Agregar estados
#     for state in afd["states"]:
#         if state == afd["initial_state"]:
#             dot.node(str(state), str(state), shape="circle", style="filled", fillcolor="lightblue")
#         elif state in afd["final_states"]:
#             dot.node(str(state), str(state), shape="doublecircle", style="filled", fillcolor="lightgreen")
#         else:
#             dot.node(str(state), str(state), shape="circle")

#     # Marcar el estado inicial con una flecha
#     dot.node("start", shape="plaintext", label="")
#     dot.edge("start", str(afd["initial_state"]), style="bold")

#     # Agregar transiciones
#     for (state, symbol), next_state in afd["transitions"].items():
#         dot.edge(str(state), str(next_state), label=symbol, fontsize="10", fontcolor="blue")

#     # Guardar y mostrar el gráfico
#     dot.render(filename, cleanup=True)
#     print(f"AFD guardado como {filename}.png")

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
    
    # Crear una figura con dos subplots
    if diversity_history is not None:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    else:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Graficar el fitness
    generations = range(1, len(best_fitness_history) + 1)
    ax1.plot(generations, best_fitness_history, 'b-', label='Mejor Fitness')
    ax1.plot(generations, avg_fitness_history, 'g-', label='Fitness Promedio')
    ax1.set_ylabel('Fitness')
    ax1.set_title('Evolución del Fitness')
    ax1.legend()
    ax1.grid(True)
    
    # Graficar el error
    ax2.plot(generations, error_history, 'r-', label='Error')
    ax2.set_ylabel('Error')
    ax2.set_title('Evolución del Error')
    ax2.legend()
    ax2.grid(True)
    
    # Graficar la diversidad si está disponible
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
    states = sorted(afd["states"])  # Ordenar estados para mejor visualización
    symbols = sorted(set(symbol for _, symbol in afd["transitions"]))  # Obtener símbolos únicos

    # Crear DataFrame con los datos de la tabla
    table_data = []
    for state in states:
        row = [f"→ {state}" if state == afd["initial_state"] else 
               f"*{state}" if state in afd["final_states"] else 
               str(state)]  # Estado inicial con "→", finales con "*"
        
        for symbol in symbols:
            next_state = afd["transitions"].get((state, symbol), "-")  # "-" si no hay transición
            row.append(next_state)
        table_data.append(row)

    df = pd.DataFrame(table_data, columns=["Estado"] + symbols)

    # Crear la figura de Matplotlib
    fig, ax = plt.subplots(figsize=(len(symbols) + 4, len(states) + 3))
    ax.axis('tight')
    ax.axis('off')

    # Dibujar la tabla
    ax.table(cellText=df.values, colLabels=df.columns, cellLoc="center", loc="center")

    # Agregar información de los estados como texto dentro de la imagen
    info_text = (
        f"Conjunto de Estados: {', '.join(map(str, afd['states']))}\n"
        f"Estados Finales: {', '.join(map(str, afd['final_states']))}\n"
        f"Estado Inicial: {afd['initial_state']}"
    )
    
    plt.figtext(0.5, 0.02, info_text, fontsize=10, ha="center", bbox={"facecolor":"white", "alpha":0.6, "pad":5})

    # Agregar título
    plt.title("Tabla de Transiciones del AFD", fontsize=14, fontweight="bold")

    # Mostrar la tabla visualmente
    plt.show()