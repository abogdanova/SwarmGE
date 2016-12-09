from algorithm.parameters import params
from fitness.evaluation import evaluate_fitness
from stats.stats import stats, get_stats
from utilities.algorithm.state import create_state
from utilities.stats import trackers
from utilities.fitness.math_functions import ave


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
    individuals = evaluate_fitness(individuals)
   
    # Generate statistics for run so far
    get_stats(individuals)

    # Traditional GE
    for generation in range(1, (params['GENERATIONS']+1)):
        stats['gen'] = generation

        # New generation
        individuals = params['STEP'](individuals)

        # Generate statistics for run so far
        get_stats(individuals)

        if params['SAVE_STATE'] and not params['DEBUG'] and \
                                generation % params['SAVE_STATE_STEP'] == 0:
            # Save the state of the current evolutionary run.
            create_state(individuals)

    return individuals


def search_loop_break():
    """
    This is a standard search process for an evolutionary algorithm. Loop over
    a given number of generations.

    :return: The final population after the evolutionary process has run for
    the specified number of generations.
    """
    
    RESTART = False
    
    # Initialise population
    individuals = params['INITIALISATION'](params['POPULATION_SIZE'])
    
    # Evaluate initial population
    individuals = evaluate_fitness(individuals)
    
    # Generate statistics for run so far
    get_stats(individuals)
    
    # Traditional GE
    for generation in range(1, (params['GENERATIONS'] + 1)):
        stats['gen'] = generation
        
        # New generation
        individuals = params['STEP'](individuals)
        
        # Generate statistics for run so far
        get_stats(individuals)
        
        if params['SAVE_STATE'] and not params['DEBUG'] and \
                                generation % params['SAVE_STATE_STEP'] == 0:
            # Save the state of the current evolutionary run.
            create_state(individuals)
    
        if stats['best_ever'].fitness == 0:
            break

        if params['RESTARTS']:
            if generation > 100:
                prev = round(ave([stat['ave_fitness'] for stat in
                               trackers.stats_list[-100:]]), 5)
                curr = round(trackers.stats_list[-1]['ave_fitness'], 5)
                
                if prev == curr:
                    # No variation in average population fitness for past 100
                    # generations. Restart evolutionary process
                    
                    RESTART = True
                    break

    if RESTART:
        # Reset trackers
        trackers.stats_list = []
        trackers.cache = {}
        trackers.best_fitness_list = []
        
        stats['restarts'] += 1
        
        # Restart search loop
        individuals = params['SEARCH_LOOP']()

    return individuals


def search_loop_from_state():
    """
    Run the evolutionary search process from a loaded state. Pick up where
    it left off previously.

    :return: The final population after the evolutionary process has run for
    the specified number of generations.
    """
    
    individuals = trackers.state_individuals
        
    # Traditional GE
    for generation in range(stats['gen'] + 1, (params['GENERATIONS'] + 1)):
        stats['gen'] = generation
        
        # New generation
        individuals = params['STEP'](individuals)
        
        # Generate statistics for run so far
        get_stats(individuals)
    
    return individuals
