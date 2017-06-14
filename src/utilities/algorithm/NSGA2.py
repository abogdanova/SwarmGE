from collections import defaultdict

from algorithm.parameters import params
from utilities.fitness.math_functions import percentile


def compute_pareto_metrics(population):
    """
    Compute the pareto fronts using NSGA-II.
    
    :param population: A population to be sorted into fronts using NSGA-II.
    :return: The pareto fronts.
    """
    
    # Calculate the pareto fronts using Non-Dominated Sorting.
    pareto = sort_non_dominated(population)
    
    # Calculate the crowding distance
    calculate_crowding_distance(pareto)
    
    return pareto


def sort_non_dominated(population):
    """Sort the first *k* *population* into different nondomination levels
    using the "Fast Nondominated Sorting Approach" proposed by Deb et al.,
    see [Deb2002]_. This algorithm has a time complexity of :math:`O(MN^2)`,
    where :math:`M` is the number of objectives and :math:`N` the number of
    individuals.
    
    :param population: A list of individuals to select from.

    :returns: A list of Pareto fronts (lists), the first list includes
              nondominated individuals.
    
    .. [Deb2002] Deb, Pratab, Agarwal, and Meyarivan, "A fast elitist
       non-dominated sorting genetic algorithm for multi-objective
       optimization: NSGA-II", 2002.

    """
    
    # Initialise empty pareto class instance.
    pareto = ParetoInfo()
    
    # Compute the Inter-Quartile Range (+1) value used to normalize the
    # crowding distance
    pareto.compute_iqr(population)
    
    # The naming *p* and *q* is the same adopted in [Deb2002]_
    for p in population:
        
        # Compute the domination counter of p
        for q in population:
            if dominates(p, q):
                # Add *q* to the set of solutions dominated by *p*
                pareto.dominated_solutions[p].append(q)
        
            elif dominates(q, p):
                # Increment the domination counter of p
                pareto.update_domination_count(p, True)
        
        # *p* belongs to the first front
        if pareto.get_domination_count(p) == 0:
            pareto.fronts[0].append(p)
            pareto.rank[p] = 0
        
    # Initialize the front counter
    i = 0
    
    # Count the fronts.
    while len(pareto.fronts[i]) > 0:
        big_q = []
        for p in pareto.fronts[i]:
            for q in pareto.dominated_solutions[p]:
                pareto.update_domination_count(q, False)
                if pareto.get_domination_count(q) == 0:
                    pareto.rank[q] = i + 1
                    big_q.append(q)
        i += 1
        pareto.fronts.append(big_q)
    
    return pareto


def dominates(individual1, individual2):
    """
    Returns whether or not *indvidual1* dominates *indvidual2*.
    
    :param individual1: The individual that would be dominated.
    :param individual2: The individual dominant.
    :returns: :obj:`True` if indvidual_1 dominates indvidual_2,
              :obj:`False` otherwise.
    """
    
    # Initialise dominating value.
    not_equal = False
    
    if not isinstance(individual1.fitness, list):
        # Individual 1 is invalid.
        return False
    
    if not isinstance(individual2.fitness, list):
        # Individual 2 is invalid.
        return True
    
    for ind1_value, ind2_value in zip(individual1.fitness,
                                      individual2.fitness):
        if ind1_value > ind2_value:
            # Individual 1 dominates Individual 2 on this objective.
            return False
        
        elif ind1_value < ind2_value:
            # Individual 2 dominates Individual 1 on this objective.
            not_equal = True
    
    return not_equal


def calculate_crowding_distance(pareto):
    """
    Compute the crowding distance of each individual in each Pareto front.
    The value is stored inside the dictionary *crowding_distance* kept by
    the *pareto_fronts*.

    :param pareto:
    :return: Nothing
    """
    
    for front in pareto.fronts:
        if len(front) > 0:
            solutions_num = len(front)
            
            for individual in front:
                pareto.crowding_distance[individual] = 0
            
            for m in range(pareto.n_objectives):
                front = sorted(front, key=lambda item: params[
                    'FITNESS_FUNCTION'].value(item.fitness, m))
                pareto.crowding_distance[front[0]] = float("inf")
                pareto.crowding_distance[front[solutions_num - 1]] = float(
                    "inf")
                for index in range(1, solutions_num - 1):
                    pareto.crowding_distance[front[index]] += \
                        (params['FITNESS_FUNCTION'].value(
                            front[index + 1].fitness, m) -
                         params['FITNESS_FUNCTION'].value(
                             front[index - 1].fitness, m)) / \
                        pareto.fitness_iqr[m]


def crowded_comparison_operator(individual, other_individual, pareto):
    """
    TODO
    
    :param individual:
    :param other_individual:
    :param pareto:
    :return: True if ___, else False.
    """
    
    if (pareto.rank[individual] < pareto.rank[other_individual]) or \
            (pareto.rank[individual] == pareto.rank[other_individual] and
             pareto.crowding_distance[individual] >
             pareto.crowding_distance[other_individual]):
        return True
    
    else:
        return False


def first_pareto_front(population):
    """
    TODO
    
    :param population:
    :return:
    """
    
    non_dominated_pop = []
    dominated_pop = []

    for i in range(len(population)):
        non_dominated = True
        for j in range(len(population)):
            if i != j and dominates(population[j], population[i]):
                non_dominated = False
                break
        if non_dominated:
            non_dominated_pop.append(population[i])
        else:
            dominated_pop.append(population[i])
        i += 1
    return non_dominated_pop, dominated_pop


def get_population_iqr(population, n_objectives):
    """
    Compute the interquartile range (IQR) of the population regarding
    each objective.
    
    :param population: The input population
    :param n_objectives: Total number of objectives
    :return: List with the IQR regarding each objective
    """
    
    # Initialise base IQR as 0 for each objective
    iqr = [0 for _ in range(n_objectives)]
    
    for m in range(n_objectives):
        # Iterate over all objectives
        
        # Sort the population with respect to the current objective.
        sorted_pop = sorted(population, key=lambda ind:
                            params['FITNESS_FUNCTION'].value(ind.fitness, m))

        # Get the inter-quartile fitness ranges for the current objective.
        iqr[m] = (params['FITNESS_FUNCTION'].value(percentile(sorted_pop,
                                                              75).fitness, m) -
                  params['FITNESS_FUNCTION'].value(percentile(sorted_pop,
                                                              25).fitness, m))
    return iqr


class ParetoInfo:
    
    def __init__(self):
        self.fronts = [[]]
        self.rank = dict()
        self.domination_count = dict()
        self.crowding_distance = dict()
        self.dominated_solutions = defaultdict(list)
        
        try:
            self.n_objectives = len(params['FITNESS_FUNCTION'].fitness_functions)
        
        except AttributeError:
            s = "utilities.algorithm.NSGA2\n" \
                "Error: Specified fitness function does not have " \
                "'fitness_functions' attribute.\n" \
                "       If using multiple objective optimisation, ensure " \
                "fitness.base_ff_classes.base_moo_ff is implemented.\n" \
                "       See README documentation for more information."
            raise Exception(s)
        
        self.fitness_iqr = [0] * self.n_objectives
    
    def compute_iqr(self, population):
        """
        Compute the Inter-Quartile Range for a population for all fitness
        objectives.
        
        :param population: A population.
        :return: Nothing.
        """
        
        # Get the inter-quartile ranges for all objectives.
        self.fitness_iqr = get_population_iqr(population, self.n_objectives)
        
        # If the IQR value is zero, we replace it for 1---which is equivalent
        # to disregard the normalization process for that objective dimension.
        self.fitness_iqr = [1 if i == 0 else i for i in self.fitness_iqr]
    
    def update_domination_count(self, individual, should_increment=True):
        """
        Update the domination count of the *individual* by incrementing:
        
            (*should_increment*=:obj:`True`)
        
        or decrementing:
            
            (*should_increment*=:obj:`False`)

        :param individual: The referring individual
        :param should_increment: Indicates if the methods increment or
                                 decrement the value.
        :return: Nothing.
        """
        
        if individual in self.domination_count:
            if should_increment:
                self.domination_count[individual] += 1
            else:
                self.domination_count[individual] -= 1
        else:
            if should_increment:
                self.domination_count[individual] = 1
            else:
                self.domination_count[individual] = -1
    
    def get_domination_count(self, individual):
        """
        Avoids references to uninitialised positions in the dictionary.

        :param individual: Individual used as key in the dictionary.
        :return: The value regarding the key, if any, or 0 otherwise.
        """
        
        if individual in self.domination_count:
            return self.domination_count[individual]
        
        return 0
    
    def get_crowding_distance(self, individual):
        """
        Avoids references to uninitialised positions in the dictionary.
        
        :param individual: Individual used as key in the dictionary.
        :return: The value regarding the key, if any, or 0 otherwise.
        """
        
        if individual in self.crowding_distance:
            return self.crowding_distance[individual]
        
        return 0


class ParetoFront:
    """
    This class makes a set of solutions in the Pareto front emulate
    an individual, such that the writing of the statistics in file
    can read the information from the Pareto front as an individual.
    """
    
    def __init__(self, pf_solutions):
        self.phenotype = PhenotypeParser(pf_solutions)
        self.genome = GenomeParser(pf_solutions)
        self.tree = TreeParser(pf_solutions)
        self.fitness = ObjectiveParser(pf_solutions)
        self.pf_solutions = pf_solutions
    
    def __lt__(self, other):
        
        if self.fitness is None:
            # Self.fitness is None, return False as it doesn't
            # matter what the other fitness is.
            return False
        else:
            if other.fitness is None:
                return False
            else:
                return len(other.fitness) > len(self.fitness)


class TestFitness:
    def __init__(self, fitness_list):
        self.fitness_list = fitness_list
    
    def __str__(self):
        return ''.join([str(fitness) + "\n" for fitness in self.fitness_list])


class PhenotypeParser:
    def __init__(self, pf_solutions):
        self.solutions = pf_solutions
    
    def __str__(self):
        return ''.join([str(ind.phenotype) + "\n" for ind in self.solutions])


class GenomeParser(PhenotypeParser):
    def __str__(self):
        return ''.join([str(ind.genome) + "\n" for ind in self.solutions])


class TreeParser(PhenotypeParser):
    def __str__(self):
        return ''.join([str(ind.tree) + "\n" for ind in self.solutions])


class ObjectiveParser(PhenotypeParser):
    def __str__(self):
        return ''.join([str(ind.fitness) + "\n" for ind in self.solutions])
