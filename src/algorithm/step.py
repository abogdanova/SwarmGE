from operators.replacement import replacement
from algorithm.evaluation import evaluation
from operators.selection import selection
from operators.crossover import crossover
from operators.mutation import mutation


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
    new_pop = evaluation(new_pop)

    # Replace the old population with the new population.
    individuals = replacement(new_pop, individuals)

    return individuals
