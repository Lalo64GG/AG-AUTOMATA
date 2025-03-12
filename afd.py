import random

def create_random_afd(num_states, alphabet):
    """Crea un AFD aleatorio."""
    states = set(range(num_states))
    initial_state = 0
    final_states = set(random.sample(list(states), random.randint(1, num_states)))
    transitions = {}

    for state in states:
        for symbol in alphabet:
            transitions[(state, symbol)] = random.choice(list(states))

    return {
        "states": states,
        "initial_state": initial_state,
        "final_states": final_states,
        "transitions": transitions,
    }

def accepts_input(afd, input_string):
    """Evalúa si el AFD acepta una cadena."""
    current_state = afd["initial_state"]
    for symbol in input_string:
        if (current_state, symbol) not in afd["transitions"]:
            return False
        current_state = afd["transitions"][(current_state, symbol)]
    return current_state in afd["final_states"]
