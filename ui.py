import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from main import main as run_algorithm
from webScrapting import get_all_conjugations
from visualizacion import save_afd_to_jflap

# Variable global para almacenar las conjugaciones obtenidas
conjugations = None

def scrape_conjugations():
    """Ejecuta Selenium en un hilo separado para evitar bloquear la UI."""
    global conjugations
    verb = verb_entry.get().strip().lower()
    if not verb:
        messagebox.showerror("Error", "Ingrese un verbo en infinitivo.")
        return

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "Abriendo navegador...\nResuelva el desafío de Cloudflare y presione Enter en la consola.\n")

    def fetch_data():
        global conjugations
        conjugations = get_all_conjugations(verb)
        if conjugations:
            messagebox.showinfo("Éxito", f"Se encontraron {len(conjugations)} conjugaciones.")
        else:
            messagebox.showerror("Error", "No se pudieron obtener conjugaciones.")

    threading.Thread(target=fetch_data, daemon=True).start()

def start_algorithm():
    """Ejecuta el Algoritmo Genético con los datos obtenidos por web scraping."""
    global conjugations
    if conjugations is None:
        messagebox.showerror("Error", "Primero obtenga las conjugaciones.")
        return

    try:
        result = run_algorithm(verb_entry.get().strip().lower(), conjugations)
        if result:
            best_afd = result["best_afd"]
            output_text.delete(1.0, tk.END)  
            output_text.insert(tk.END, "Tabla de Transiciones:\n")
            output_text.insert(tk.END, result["transition_table"])  
        else:
            messagebox.showerror("Error", "No se pudo generar el AFD.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema: {e}")

root = tk.Tk()
root.title("Algoritmo Genético - AFD")

# Entrada de verbo
tk.Label(root, text="Ingrese un verbo en infinitivo:").pack(pady=5)
verb_entry = tk.Entry(root, width=30)
verb_entry.pack(pady=5)

# Botones
tk.Button(root, text="Obtener Conjugaciones", command=scrape_conjugations).pack(pady=5)
tk.Button(root, text="Ejecutar Algoritmo", command=start_algorithm).pack(pady=5)

# Área de texto para la tabla de transiciones
output_text = scrolledtext.ScrolledText(root, width=60, height=20)
output_text.pack(pady=10)


# Ejecutar la ventana
root.mainloop()
