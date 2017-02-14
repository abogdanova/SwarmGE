from fitness.evaluation import evaluate_fitness
from operators.crossover import crossover
from operators.mutation import mutation
from operators.replacement import replacement
from operators.selection import selection
from algorithm.parameters import params


def step(individuals):
    """
    Runs a single generation of the evolutionary algorithm process:
        Selection
        Variation
        Evaluation
        Replacement
    
    :param individuals: The current generation, upon which a single
    evolutionary generation will be imposed.
    :return: The next generation of the population.
    """

    # Select parents from the original population.
    parents = selection(individuals)

    # Crossover parents and add to the new population.
    cross_pop = crossover(parents)

    # Mutate the new population.
    new_pop = mutation(cross_pop)

    # Evaluate the fitness of the new population.
    new_pop = evaluate_fitness(new_pop)

    # Replace the old population with the new population.
    individuals = replacement(new_pop, individuals)
    
    return individuals


def steady_state_step(individuals):
    """
    Runs a single generation of the evolutionary algorithm process,
    using steady state replacement:
        Selection
        Variation
        Evaluation
        Replacement

    :param individuals: The current generation, upon which a single
    evolutionary generation will be imposed.
    :return: The next generation of the population.
    """
    
    # Initialise counter for new individuals.
    ind_counter = 0
    
    while ind_counter < params['POPULATION_SIZE']:
    
        # Select parents from the original population.
        parents = selection(individuals)
        
        # Crossover parents and add to the new population.
        cross_pop = crossover(parents)
        
        # Mutate the new population.
        new_pop = mutation(cross_pop)
        
        # Evaluate the fitness of the new population.
        new_pop = evaluate_fitness(new_pop)
        
        # Replace the old population with the new population.
        individuals = replacement(new_pop, individuals)
        
        # Increment the ind counter
        ind_counter += params['GENERATION_SIZE']
    
    return individuals
