from algorithm.evaluate_fitness import evaluate_fitness
from operators.crossover import crossover
from operators.mutation import mutation
from algorithm.parameters import params


def step(individuals):
    """Return individuals and best ever individual from a step of
    the EA iteration"""

    # Select parents
    parents = params['SELECTION'](individuals)

    # Crossover parents and add to the new population
    cross_pop = crossover(parents)

    # Mutate the new population
    new_pop = mutation(cross_pop)

    # Evaluate the fitness of the new population
    new_pop = evaluate_fitness(new_pop)

    # Replace the sorted individuals with the new populations
    individuals = params['REPLACEMENT'](new_pop, individuals)

    return individuals
