from afd import accepts_input

def evaluate_afd(afd, correct_conjugations, incorrect_conjugations):
    """Evalúa el AFD en función de su capacidad para aceptar/rechazar conjugaciones."""
    score = sum(accepts_input(afd, word) for word in correct_conjugations)
    score += sum(not accepts_input(afd, word) for word in incorrect_conjugations)
    return score
