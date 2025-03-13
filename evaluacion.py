from afd import accepts_input



def evaluate_afd(afd, correct_conjugations, current_population=None):
    from genetico import diversity_measure

    """Evalúa el AFD con bonus por diversidad si se proporciona la población actual."""
    if not correct_conjugations:
        return 0
    
    # Calcular precisión básica
    accepted_correct = sum(accepts_input(afd, word) for word in correct_conjugations)
    total_correct = len(correct_conjugations)
    
    # Precisión básica
    recall = accepted_correct / total_correct if total_correct > 0 else 0
    
    # Penalización suave por complejidad
    complexity_penalty = min(0.15, len(afd["states"]) / (3 * total_correct))
    
    # Puntaje base
    score = (0.95 * recall) - complexity_penalty
    
    # Bonus por diversidad si tenemos la población actual
    if current_population and len(current_population) > 0:
        avg_diversity = sum(diversity_measure(afd, other) for other in current_population) / len(current_population)
        diversity_bonus = 0.05 * avg_diversity  # Máximo 5% de bonus por diversidad
        score += diversity_bonus
    
    return max(0.0, score)  # Aseguramos que el score no sea negativo