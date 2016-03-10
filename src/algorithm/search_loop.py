from copy import deepcopy
from algorithm import step, evaluate_fitness
from algorithm.parameters import params
from stats import stats
from utilities.save_plot import search_loop_save_plot


def search_loop(max_generations, individuals, grammar, replacement, selection, crossover, mutation, fitness_function, time_list, TIME_STAMP):
    """Loop over max generations"""

    phenotypes = {}
    fitness_plot = []
    invalids = 0
    #Evaluate initial population
    phenotypes, individuals, invalids, regens = evaluate_fitness.evaluate_fitness(individuals, grammar, fitness_function, phenotypes, invalids, mutation)
    total_inds = params['POPULATION_SIZE']
    best_ever = max(individuals)
    stats.print_stats(0, individuals, best_ever, phenotypes, total_inds, invalids, regens, time_list, TIME_STAMP)
    if params['COMPLETE_EVALS']:
        generation = 1
        while len(phenotypes) < (max_generations * params['POPULATION_SIZE']):
            individuals, best_ever, phenotypes, invalids, step_regens = step.step(
                    individuals, grammar, replacement, selection, crossover,
                    mutation, fitness_function, best_ever, phenotypes,
                    invalids, generation, TIME_STAMP)
            regens += step_regens
            total_inds += params['POPULATION_SIZE']
            stats.print_stats(generation, individuals, best_ever, phenotypes, total_inds, invalids, regens, time_list, TIME_STAMP)
            if generation == max_generations:
                best_test = deepcopy(best_ever)
                best_test.evaluate(fitness_function, dist='test')
                if not params['DEBUG']:
                    #What is this!!!!!!!
                    save_best_midway(generation, best_test, TIME_STAMP, time_list)
            if params['SAVE_PLOTS']:
                search_loop_save_plot(fitness_plot, best_ever.fitness, TIME_STAMP)
            generation += 1
    else:
        for generation in range(1, (max_generations+1)):
            individuals, best_ever, phenotypes, invalids, step_regens = step.step(
                individuals, grammar, replacement, selection, crossover,
                mutation, fitness_function, best_ever, phenotypes,
                invalids, generation, TIME_STAMP)
            regens += step_regens
            total_inds += params['POPULATION_SIZE']
            stats.print_stats(generation, individuals, best_ever, phenotypes, total_inds, invalids, regens, time_list, TIME_STAMP)
            if params['SAVE_PLOTS']:
                search_loop_save_plot(fitness_plot, best_ever.fitness, TIME_STAMP)
    return best_ever, phenotypes, total_inds, invalids, regens, generation