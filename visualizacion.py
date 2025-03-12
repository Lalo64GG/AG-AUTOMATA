import matplotlib.pyplot as plt
from graphviz import Digraph

def draw_afd(afd, filename="afd"):
    dot = Digraph(comment="AFD Generado", format="png")
    dot.attr(rankdir="LR")  # Orientación de izquierda a derecha

    # Agregar estados
    for state in afd["states"]:
        if state == afd["initial_state"]:
            # Estado inicial con un color diferente
            dot.node(str(state), str(state), shape="circle", style="filled", fillcolor="lightblue")
        elif state in afd["final_states"]:
            # Estado final con un color diferente
            dot.node(str(state), str(state), shape="doublecircle", style="filled", fillcolor="lightgreen")
        else:
            # Estado normal
            dot.node(str(state), str(state), shape="circle")

    # Marcar el estado inicial con una flecha
    dot.node("start", shape="plaintext", label="")
    dot.edge("start", str(afd["initial_state"]), style="bold")

    # Agregar transiciones
    for (state, symbol), next_state in afd["transitions"].items():
        dot.edge(str(state), str(next_state), label=symbol, fontsize="10", fontcolor="blue")

    # Guardar y mostrar el gráfico
    dot.render(filename, cleanup=True)
    print(f"AFD guardado como {filename}.png")

def plot_evolution(best_fitness, avg_fitness, error):
    """Grafica la evolución del fitness y error."""
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.plot(best_fitness, label="Mejor Fitness")
    plt.plot(avg_fitness, label="Fitness Promedio")
    plt.xlabel("Generación")
    plt.ylabel("Fitness")
    plt.title("Evolución del Fitness")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(error, label="Error", color="red")
    plt.xlabel("Generación")
    plt.ylabel("Error")
    plt.title("Evolución del Error")
    plt.legend()

    plt.tight_layout()
    plt.show()

import xml.etree.ElementTree as ET

def save_afd_to_jflap(afd, filename="afd.jff"):
    # Crear la estructura XML
    structure = ET.Element('structure')
    ET.SubElement(structure, 'type').text = 'fa'
    automaton = ET.SubElement(structure, 'automaton')

    # Agregar estados
    for state in afd["states"]:
        state_element = ET.SubElement(automaton, 'state', id=str(state), name=str(state))
        if state == afd["initial_state"]:
            ET.SubElement(state_element, 'initial')
        if state in afd["final_states"]:
            ET.SubElement(state_element, 'final')

    # Agregar transiciones
    for (state, symbol), next_state in afd["transitions"].items():
        transition = ET.SubElement(automaton, 'transition')
        ET.SubElement(transition, 'from').text = str(state)
        ET.SubElement(transition, 'to').text = str(next_state)
        ET.SubElement(transition, 'read').text = symbol

    # Guardar el archivo
    tree = ET.ElementTree(structure)
    tree.write(filename, encoding='utf-8', xml_declaration=True)
    print(f"AFD guardado como {filename}")