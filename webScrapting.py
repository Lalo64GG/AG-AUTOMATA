from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configura el navegador en modo no headless
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_all_conjugations(verb):
    url = f"https://dle.rae.es/{verb}"
    driver.get(url)

    input("Resuelve el desafío de Cloudflare y presiona Enter para continuar...")

    try:
        wait = WebDriverWait(driver, 20)
        section = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "c-collapse__content")))

        tables = driver.find_elements(By.CLASS_NAME, "c-table")
        
        all_conjugations = {}

        # Iterar sobre todas las tablas
        for table in tables:
            headers = table.find_elements(By.TAG_NAME, "th")
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows[1:]:  # Omitir la cabecera
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 2:
                    # Extraer el tiempo verbal y su conjugación
                    tense = cols[0].text.strip()
                    conjugation = cols[1].text.strip()
                    
                    # Guardar en el diccionario
                    if tense not in all_conjugations:
                        all_conjugations[tense] = []
                    all_conjugations[tense].append(conjugation)

        return all_conjugations

    except Exception as e:
        print("Error:", e)
        return {}

    finally:
        driver.quit()
