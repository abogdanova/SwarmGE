from algorithm.parameters import params
from algorithm import evaluate_fitness
from operators import crossover

def step(individuals):
    """Return individuals and best ever individual from a step of
    the EA iteration"""

    # Select parents
    parents = params['SELECTION'](individuals)

    # Crossover parents and add to the new population
    cross_pop = crossover.crossover(parents)

    # Mutate the new population
    new_pop = list(map(params['MUTATION'], cross_pop))

    # Evaluate the fitness of the new population
    new_pop = evaluate_fitness.evaluate_fitness(new_pop)

    # Replace the sorted individuals with the new populations
    individuals = params['REPLACEMENT'](new_pop, individuals)

    return individuals
