import types
from copy import copy
from time import time
from os import getcwd, path, makedirs
from sys import stdout
import numpy as np

from algorithm.parameters import params
from utilities.stats import trackers
from utilities.stats.save_plots import save_best_fitness_plot
from utilities.algorithm.state import create_state

"""Algorithm statistics"""
stats = {
        "gen": 0,
        "total_inds": 0,
        "regens": 0,
        "invalids": 0,
        "unique_inds": len(trackers.cache),
        "unused_search": 0,
        "ave_genome_length": 0,
        "max_genome_length": 0,
        "min_genome_length": 0,
        "ave_used_codons": 0,
        "max_used_codons": 0,
        "min_used_codons": 0,
        "ave_tree_depth": 0,
        "max_tree_depth": 0,
        "min_tree_depth": 0,
        "ave_tree_nodes": 0,
        "max_tree_nodes": 0,
        "min_tree_nodes": 0,
        "ave_fitness": 0,
        "best_fitness": 0,
        "time_taken": 0,
        "total_time": 0,
        "time_adjust": 0
}


def get_stats(individuals, end=False):
    """
    Generate the statistics for an evolutionary run. Save statistics to
    utilities.trackers.stats_list. Print statistics. Save fitness plot
    information.

    :param individuals: A population of individuals for which to generate
    statistics.
    :param end: Boolean flag for indicating the end of an evolutionary run.
    :return: Nothing.
    """

    # Get best individual.
    best = max(individuals)

    if not trackers.best_ever or best > trackers.best_ever:
        # Save best individual in trackers.best_ever.
        trackers.best_ever = best

    if end or params['VERBOSE'] or not params['DEBUG']:
        # Update all stats.
        update_stats(individuals, end)

    # Save fitness plot information
    if params['SAVE_PLOTS'] and not params['DEBUG']:
        if not end:
            trackers.best_fitness_list.append(trackers.best_ever.fitness)

        if params['VERBOSE'] or end:
            save_best_fitness_plot()

    # Print statistics
    if params['VERBOSE'] and not end:
        print_generation_stats()

    elif not params['SILENT']:
        # Print simple display output.
        perc = stats['gen'] / (params['GENERATIONS']+1) * 100
        stdout.write("Evolution: %d%% complete\r" % perc)
        stdout.flush()

    # Generate test fitness on regression problems
    if hasattr(params['FITNESS_FUNCTION'], "training_test") and end:
        trackers.best_ever.training_fitness = copy(trackers.best_ever.fitness)
        trackers.best_ever.test_fitness = params['FITNESS_FUNCTION'](
            trackers.best_ever, dist='test')
        trackers.best_ever.fitness = trackers.best_ever.training_fitness

    # Save stats to list.
    if params['VERBOSE'] or (not params['DEBUG'] and not end):
        trackers.stats_list.append(copy(stats))
    
    # Save stats to file.
    if not params['DEBUG']:
        if stats['gen'] == 0:
            save_stats_headers()
        save_stats_to_file(end)
        if params['SAVE_ALL']:
            save_best_ind_to_file(end, stats['gen'])
        elif params['VERBOSE'] or end:
            save_best_ind_to_file(end, "best")

    if end and not params['SILENT']:
        print_final_stats()

    if params['SAVE_STATE'] and not params['DEBUG'] and \
                            stats['gen'] % params['SAVE_STATE_STEP'] == 0:
        # Save the state of the current evolutionary run.
        create_state(individuals)


def update_stats(individuals, end):
    """
    Update all stats in the stats dictionary.
    
    :param individuals: A population of individuals.
    :param end: Boolean flag for indicating the end of an evolutionary run.
    :return: Nothing.
    """

    if not end:
        # Time Stats
        trackers.time_list.append(time() - stats['time_adjust'])
        stats['time_taken'] = trackers.time_list[-1] - \
                              trackers.time_list[-2]
        stats['total_time'] = trackers.time_list[-1] - \
                              trackers.time_list[0]

    # Population Stats
    stats['total_inds'] = params['POPULATION_SIZE'] * (stats['gen'] + 1)
    stats['invalids'] = len(trackers.invalid_cache)
    if params['CACHE']:
        stats['unique_inds'] = len(trackers.cache)
        stats['unused_search'] = 100 - stats['unique_inds'] / \
                                       stats['total_inds'] * 100

    # Genome Stats
    genome_lengths = [len(i.genome) for i in individuals]
    stats['max_genome_length'] = np.nanmax(genome_lengths)
    stats['ave_genome_length'] = np.nanmean(genome_lengths)
    stats['min_genome_length'] = np.nanmin(genome_lengths)

    # Used Codon Stats
    codons = [i.used_codons for i in individuals]
    stats['max_used_codons'] = np.nanmax(codons)
    stats['ave_used_codons'] = np.nanmean(codons)
    stats['min_used_codons'] = np.nanmin(codons)

    # Tree Depth Stats
    depths = [i.depth for i in individuals]
    stats['max_tree_depth'] = np.nanmax(depths)
    stats['ave_tree_depth'] = np.nanmean(depths)
    stats['min_tree_depth'] = np.nanmin(depths)

    # Tree Node Stats
    nodes = [i.nodes for i in individuals]
    stats['max_tree_nodes'] = np.nanmax(nodes)
    stats['ave_tree_nodes'] = np.nanmean(nodes)
    stats['min_tree_nodes'] = np.nanmin(nodes)

    # Fitness Stats
    fitnesses = [i.fitness for i in individuals]
    stats['ave_fitness'] = np.nanmean(fitnesses)
    stats['best_fitness'] = trackers.best_ever.fitness


def print_generation_stats():
    """
    Print the statistics for the generation and individuals

    :return: Nothing.
    """

    print("______\n")
    for stat in sorted(stats.keys()):
        print(" ", stat, ": \t", stats[stat])
    print("\n")


def print_final_stats():
    """
    Prints a final review of the overall evolutionary process.

    :return: Nothing.
    """

    if hasattr(params['FITNESS_FUNCTION'], "training_test"):
        print("\n\nBest:\n  Training fitness:\t",
              trackers.best_ever.training_fitness)
        print("  Test fitness:\t\t", trackers.best_ever.test_fitness)
    else:
        print("\n\nBest:\n  Fitness:\t", trackers.best_ever.fitness)
    print("  Phenotype:", trackers.best_ever.phenotype)
    print("  Genome:", trackers.best_ever.genome)
    print_generation_stats()


def save_stats_to_file(end=False):
    """
    Write the results to a results file for later analysis

    :param end: A boolean flag indicating whether or not the evolutionary
    process has finished.
    :return: Nothing.
    """

    if params['VERBOSE']:
        filename = path.join(params['FILE_PATH'], "stats.tsv")
        savefile = open(filename, 'a')
        for stat in sorted(stats.keys()):
            savefile.write(str(stats[stat]) + "\t")
        savefile.write("\n")
        savefile.close()

    elif end:
        filename = path.join(params['FILE_PATH'], "stats.tsv")
        savefile = open(filename, 'a')
        for item in trackers.stats_list:
            for stat in sorted(item.keys()):
                savefile.write(str(item[stat]) + "\t")
            savefile.write("\n")
        savefile.close()


def save_stats_headers():
    """
    Saves the headers for all stats in the stats dictionary.

    :return: Nothing.
    """

    filename = path.join(params['FILE_PATH'], "stats.tsv")
    savefile = open(filename, 'w')
    for stat in sorted(stats.keys()):
        savefile.write(str(stat) + "\t")
    savefile.write("\n")
    savefile.close()


def save_params_to_file():
    """
    Save evolutionary parameters in a parameters.txt file. Automatically
    parse function and class names.

    :return: Nothing.
    """

    # Generate file path and name.
    filename = path.join(params['FILE_PATH'], "parameters.txt")
    savefile = open(filename, 'w')

    # Justify whitespaces for pretty printing/saving.
    col_width = max(len(param) for param in params.keys())

    for param in sorted(params.keys()):
        savefile.write(str(param) + ": ")
        spaces = [" " for _ in range(col_width - len(param))]

        if isinstance(params[param], types.FunctionType):
            # Object is a function, save function name.
            savefile.write("".join(spaces) + str(params[
                                                     param].__name__) + "\n")
        elif hasattr(params[param], '__call__'):
            # Object is a class instance, save name of class instance.
            savefile.write("".join(spaces) + str(params[
                                                     param].__class__.__name__) + "\n")
        else:
            # Write object as normal.
            savefile.write("".join(spaces) + str(params[param]) + "\n")

    savefile.close()


def save_best_ind_to_file(end=False, name="best"):
    """
    Saves the best individual to a file.

    :param end: A boolean flag indicating whether or not the evolutionary
    process has finished.
    :param name: The name of the individual. Default set to "best".
    :return: Nothing.
    """

    filename = path.join(params['FILE_PATH'], (str(name) + ".txt"))
    savefile = open(filename, 'w')
    savefile.write("Generation:\n" + str(stats['gen']) + "\n\n")
    savefile.write("Phenotype:\n" + str(trackers.best_ever.phenotype) + "\n\n")
    savefile.write("Genotype:\n" + str(trackers.best_ever.genome) + "\n")
    savefile.write("Tree:\n" + str(trackers.best_ever.tree) + "\n")
    if hasattr(params['FITNESS_FUNCTION'], "training_test"):
        if end:
            savefile.write("\nTraining fitness:\n" +
                           str(trackers.best_ever.training_fitness))
            savefile.write("\nTest fitness:\n" +
                           str(trackers.best_ever.test_fitness))
        else:
            savefile.write("\nFitness:\n" + str(trackers.best_ever.fitness))
    else:
        savefile.write("\nFitness:\n" + str(trackers.best_ever.fitness))
    savefile.close()


def generate_folders_and_files():
    """
    Generates necessary folders and files for saving statistics and parameters.

    :return: Nothing.
    """

    if params['EXPERIMENT_NAME']:
        # Experiment manager is being used.
        path_1 = path.join(getcwd(), "..", "results")

        if not path.isdir(path_1):
            # Create results folder.
            makedirs(path_1)

        # Set file path to include experiment name.
        params['FILE_PATH'] = path.join(path_1, params['EXPERIMENT_NAME'])

    else:
        # Set file path to results folder.
        params['FILE_PATH'] = path.join(getcwd(), "..", "results")

    # Generate save folders
    if not path.isdir(params['FILE_PATH']):
        makedirs(params['FILE_PATH'])

    if not path.isdir(path.join(params['FILE_PATH'],
                                str(params['TIME_STAMP']))):
        makedirs(path.join(params['FILE_PATH'],
                        str(params['TIME_STAMP'])))

    params['FILE_PATH'] = path.join(params['FILE_PATH'],
                                    str(params['TIME_STAMP']))

    save_params_to_file()
