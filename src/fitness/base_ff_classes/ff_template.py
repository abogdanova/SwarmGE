from fitness.base_ff_classes.base_ff import base_ff


class ff_template(base_ff):
    """
    Basic fitness function template for writing new fitness functions. This
    basic template inherits from the base fitness function class,
    which contains various checks and balances.
    """

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()
    
    def evaluate(self, ind, **kwargs):
        """
        Default fitness execution call for all fitness functions. When
        implementing a new fitness function, this is where code should be added
        to evaluate target phenotypes.
                
        :param ind: An individual to be evaluated.
        :param kwargs: Optional extra arguments.
        :return: The fitness of the evaluated individual.
        """
        
        # Evaluate the fitness of the phenotype
        fitness = eval(ind.phenotype)
        
        return fitness
