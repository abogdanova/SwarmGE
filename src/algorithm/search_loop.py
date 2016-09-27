from algorithm import step, evaluate_fitness
from stats.stats import stats, get_stats
from algorithm.parameters import params
from utilities.trackers import cache


def search_loop_wheel():
    """
    Allows the user to select different main search functions.
    
    :return: The returns of the main search loop function.
    """
    
    if params['COMPLETE_EVALS']:
        return search_loop_complete_evals()
    else:
        return search_loop()


def search_loop():
    """
    This is a standard search process for an evolutionary algorithm. Loop over
    a given number of generations.
    
    :return: The final population after the evolutionary process has run for
    the specified number of generations.
    """

    # Initialise population
    individuals = params['INITIALISATION'](params['POPULATION_SIZE'])

    # Evaluate initial population
    individuals = evaluate_fitness.evaluate_fitness(individuals)

    # Generate statistics for run so far
    get_stats(individuals)

    # Traditional GE
    for generation in range(1, (params['GENERATIONS']+1)):
        stats['gen'] = generation

        # New generation
        individuals = step.step(individuals)

        # Generate statistics for run so far
        get_stats(individuals)

    return individuals


def search_loop_complete_evals():
    """
    This is a non-standard search process for an evolutionary algorithm. Loop
    over a given number of total fitness evaluations rather than a set
    number of generations. May run for more generations than are set in
    params['GENERATIONS'].
    
    :return: The final population after the evolutionary process has run for
    the specified number of fitness evaluations.
    """

    # Initialise population
    individuals = params['INITIALISATION'](params['POPULATION_SIZE'])

    # Evaluate initial population
    individuals = evaluate_fitness.evaluate_fitness(individuals)

    # Generate statistics for run so far
    get_stats(individuals)

    # Runs for a specified number of fitness evaluations
    while len(cache) < (params['GENERATIONS'] * params['POPULATION_SIZE']):

        stats['gen'] += 1

        # New generation
        individuals = step.step(individuals)

        # Generate statistics for run so far
        get_stats(individuals)

    return individuals
