from algorithm.parameters import params


class regex_string_match:
    """Fitness function for matching a string. Takes a string and returns
    fitness. Penalises output that is not the same length as the target."""

    maximise = False

    def __init__(self):
        # Set target string.
        self.target = params['TARGET']

    def __call__(self, ind):
        guess = ind.phenotype
        
        # print("Guess: ", guess)
        # print("Target:", self.target)
        
        fitness = float(max(len(self.target), len(guess)))
        #
        # print("Fitnes:", fitness)
        #
        # lengths = [len(self.target), len(guess)]
        #
        #
        # for i, item in zip(self.target, guess):
        #     print(t_p)
        #     print(g_p)
        #     fitness += abs(ord(t_p) - ord(g_p))
        #
        # print(fitness)
        #
        # quit()
            
        # Loops as long as the shorter of two strings
        for (t_p, g_p) in zip(self.target, guess):
            if t_p == g_p:
                fitness -= 1
            else:
                fitness -= 1 / (1 + (abs(ord(t_p) - ord(g_p))))
        #
        # if diff > 0:
        #     fitness *= diff

        return fitness
