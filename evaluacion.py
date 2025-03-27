from afd import accepts_input

def evaluate_afd(afd, correct_conjugations, current_population=None):
    """Evalúa el AFD con bonus por diversidad si se proporciona la población actual."""
    if not correct_conjugations:
        return 0
    
    # Peso incrementado para la precisión
    precision_weight = 0.98  # Incrementado de 0.95 a 0.98
    
    # Calcular precisión básica - ahora con pesos para enfatizar eficiencia en el reconocimiento
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
    
    # También calculamos precisión estándar para información y feedback
    standard_recall = sum(accepts_input(afd, word) for word in correct_conjugations) / total_correct if total_correct > 0 else 0
    
    # Reducir la penalización por complejidad (queremos AFDs más grandes si son necesarios)
    complexity_penalty = min(0.10, len(afd["states"]) / (4 * total_correct))
    
    # Puntaje base con más énfasis en precision y menos penalización por complejidad
    score = (precision_weight * weighted_recall) - complexity_penalty
    
    # Bonus por diversidad si tenemos la población actual
    if current_population and len(current_population) > 0:
        from genetico import diversity_measure
        avg_diversity = sum(diversity_measure(afd, other) for other in current_population) / len(current_population)
        diversity_bonus = 0.07 * avg_diversity  # Incrementado a 7% de bonus por diversidad
        score += diversity_bonus
    
    # Aseguramos que el score esté en el rango [0,1]
    return max(0.0, min(1.0, score))