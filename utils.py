def load_conjugations(file_path):
    """Carga conjugaciones correctas e incorrectas desde un archivo."""
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file]
