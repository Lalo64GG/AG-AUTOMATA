from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def get_all_conjugations(verb):
    url = f"https://dle.rae.es/{verb}"
    
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)

        input("Resuelve el desafío de Cloudflare y presiona Enter para continuar...")

        wait = WebDriverWait(driver, 20)
        section = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "c-collapse__content")))

        # Buscar todas las tablas
        tables = driver.find_elements(By.CLASS_NAME, "c-table")
        
        all_conjugations = set()

        # Extraer conjugaciones de cada tabla
        for table in tables:
            # Encontrar todas las filas de la tabla
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            # Iterar por las filas de datos
            for row in rows[1:]:
                # Obtener todas las celdas de datos (td)
                data_cells = row.find_elements(By.TAG_NAME, "td")
                
                # Si hay celdas de datos
                if data_cells:
                    # Iterar por cada celda de datos
                    for cell in data_cells:
                        # Obtener el texto de la celda
                        conjugations = cell.text.strip()
                        
                        # Primero, eliminar paréntesis y su contenido
                        conjugations = re.sub(r'\s*\(.*?\)', '', conjugations).strip()
                        
                        # Procesar diferentes patrones de separación
                        
                        # 1. Separar por " / " (slash con espacios)
                        forms = []
                        for form in re.split(r'\s*/\s*', conjugations):
                            forms.append(form.strip())
                        
                        # 2. Separar por " o " (separador "o" con espacios)
                        new_forms = []
                        for form in forms:
                            # Dividir por " o " pero mantener los espacios dentro de las palabras
                            split_forms = re.split(r'\s+o\s+', form)
                            new_forms.extend([f.strip() for f in split_forms])
                        
                        # Procesar cada forma individual
                        for conj in new_forms:
                            # Limpiar y procesar
                            conj = conj.strip().lower()
                            
                            # Filtrar conjugaciones válidas
                            if conj and len(conj) > 1 and not conj.isdigit():
                                all_conjugations.add(conj)

        # Convertir a lista, ordenar y filtrar
        conjugations_list = sorted(list(all_conjugations))
        
        # Filtrar para eliminar infinitivos, participios y formas no conjugadas
        conjugations_list = [
            conj for conj in conjugations_list 
            if not (conj == verb or conj in [f'{verb}do', f'{verb}ndo'])
        ]
        
        print(f"Número total de conjugaciones encontradas: {len(conjugations_list)}")
        
        # Imprimir las conjugaciones encontradas
        for conj in conjugations_list:
            print(conj)
        
        return conjugations_list

    except Exception as e:
        print("Error:", e)
        return []

    finally:
        driver.quit()