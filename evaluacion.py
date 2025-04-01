from afd import accepts_input

def validate_final_states(afd, conjugations):
    """
    Verifica si los estados finales del AFD son realmente estados de conjugaciones completas.
    
    Parámetros:
    - afd: Diccionario que representa el Autómata Finito Determinista
    - conjugations: Lista de conjugaciones correctas
    
    Retorna:
    - penalty: Un valor de penalización entre 0 y 1
    """
    total_conjugations = len(conjugations)
    if total_conjugations == 0:
        return 1.0  # Sin conjugaciones, máxima penalización
    
    # Rastrear estados que realmente llevan a conjugaciones completas
    valid_final_states = set()
    
    # Verificar cada conjugación
    for word in conjugations:
        current_state = afd["initial_state"]
        for i, symbol in enumerate(word):
            # Transición al siguiente estado
            current_state = afd["transitions"].get((current_state, symbol), -1)
            
            # Si no hay transición, la palabra no es válida
            if current_state == -1:
                break
            
            # Si es el último símbolo y es un estado final, marcarlo como válido
            if i == len(word) - 1 and current_state in afd["final_states"]:
                valid_final_states.add(current_state)
    
    # Calcular porcentaje de estados finales inválidos
    invalid_final_states = afd["final_states"] - valid_final_states
    
    # Penalización basada en estados finales inválidos
    if len(afd["final_states"]) == 0:
        return 1.0  # Si no hay estados finales, máxima penalización
    
    # Calcular la penalización
    invalid_ratio = len(invalid_final_states) / len(afd["final_states"])
    
    # Convertir la penalización a un valor entre 0 y 1
    # Cuantos más estados finales inválidos, mayor la penalización
    return min(1.0, invalid_ratio * 1.5)  # Máximo 1.0

def evaluate_afd(afd, correct_conjugations, current_population=None):
    """Evalúa el AFD con bonus por diversidad si se proporciona la población actual."""
    if not correct_conjugations:
        return 0
    
    # Peso incrementado para la precisión
    precision_weight = 0.95  # Ligero ajuste
    
    # Calcular precisión básica
    total_correct = len(correct_conjugations)
    
    # Introducir peso por longitud para favorecer palabras largas y complejas
    weighted_correct = 0
    total_weights = 0
    
    for word in correct_conjugations:
        # Peso basado en longitud: palabras más largas valen más
        weight = 1.0 + min(0.5, len(word) / 20)  # Máximo 50% extra de peso
        
        # Peso adicional para conjugaciones con espacio (más complejas)
        if " " in word:
            weight *= 1.2  # 20% extra para conjugaciones compuestas
        
        total_weights += weight
        if accepts_input(afd, word):
            weighted_correct += weight
    
    # Precisión ponderada
    weighted_recall = weighted_correct / total_weights if total_weights > 0 else 0
    
    # Penalización por estados finales inválidos
    final_states_penalty = validate_final_states(afd, correct_conjugations)
    
    # Reducir la penalización por complejidad
    complexity_penalty = min(0.15, len(afd["states"]) / (4 * total_correct))
    
    # Calcular puntaje base
    score = (precision_weight * weighted_recall) - complexity_penalty - final_states_penalty
    
    # Bonus por diversidad si tenemos la población actual
    if current_population and len(current_population) > 0:
        from genetico import diversity_measure
        avg_diversity = sum(diversity_measure(afd, other) for other in current_population) / len(current_population)
        diversity_bonus = 0.05 * avg_diversity  # Bonus por diversidad
        score += diversity_bonus
    
    # Asegurar que el score esté en el rango [0,1]
    return max(0.0, min(1.0, score))