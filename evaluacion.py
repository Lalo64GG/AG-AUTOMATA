from afd import accepts_input



def evaluate_afd(afd, correct_conjugations, current_population=None):
    from genetico import diversity_measure

    """Evalúa el AFD con bonus por diversidad si se proporciona la población actual."""
    if not correct_conjugations:
        return 0
    
    accepted_correct = sum(accepts_input(afd, word) for word in correct_conjugations)
    total_correct = len(correct_conjugations)
    

    recall = accepted_correct / total_correct if total_correct > 0 else 0
    
    complexity_penalty = min(0.15, len(afd["states"]) / (3 * total_correct))
    
    score = (0.95 * recall) - complexity_penalty
    
    if current_population and len(current_population) > 0:
        avg_diversity = sum(diversity_measure(afd, other) for other in current_population) / len(current_population)
        diversity_bonus = 0.05 * avg_diversity 
        score += diversity_bonus
    
    return max(0.0, score) 