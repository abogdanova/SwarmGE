from algorithm.parameters import params

class string_match:
    """Fitness function for matching a string. Takes a string and returns
    fitness. Penalises output that is not the same length as the target.
    Usage: StringMatch("golden") returns a *callable object*, ie the fitness
    function."""

    maximise = False

    def __init__(self):
        self.target = params['STRING_MATCH_TARGET']

    def __call__(self, guess):
        fitness = max(len(self.target), len(guess))
        # Loops as long as the shorter of two strings
        for (t_p, g_p) in zip(self.target, guess):
            if t_p == g_p:
                fitness -= 1
        return fitness
