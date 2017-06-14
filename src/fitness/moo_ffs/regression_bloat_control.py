from fitness.supervised_learning.regression import regression


class regression_bloat_control(regression):
    """
    Fitness function for regression using a multiobjective approach
    to control bloat by setting the number of nodes in the derivation tree
    as a second objective. We slightly specialise the function for
    supervised_learning.
    """

    def __init__(self):
        super().__init__()
                
        # Over-write default fitness to account for multiple objectives.
        regression_bloat_control.default_fitness = [super().default_fitness,
                                                    super().default_fitness]

    def __call__(self, ind, dist="training"):
        objective_1 = super().__call__(ind, dist)
        objective_1 = float(objective_1)
        objective_2 = ind.nodes
        
        return [objective_1, objective_2]

    @staticmethod
    def value(fitness_vector, objective_index):
        if not isinstance(fitness_vector, list):
            return float("inf")
        return fitness_vector[objective_index]

    @staticmethod
    def num_objectives():
        return 2
