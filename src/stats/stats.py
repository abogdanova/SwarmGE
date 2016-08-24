from utilities.save_plots import save_best_fitness_plot
from algorithm.parameters import params
from os import path, mkdir, getcwd
from datetime import timedelta
from utilities import trackers
from sys import stdout
from copy import copy
import time


"""Algorithm statistics"""
stats = {
        "gen": 0,
        "best_ever": None,
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
        "total_time": 0
}


def get_stats(individuals, end=False):
    """Generate the statistics for an evolutionary run"""

    if end or params['VERBOSE'] or not params['DEBUG']:

        # Time Stats
        trackers.time_list.append(time.clock())
        available = [i for i in individuals if not i.invalid]
        # TODO: Should we save time stats as raw seconds? Easier for parsing.
        stats['time_taken'] = \
            timedelta(seconds=trackers.time_list[-1] - trackers.time_list[-2])
        stats['total_time'] = timedelta(seconds=(trackers.time_list[-1] -
                                        trackers.time_list[0]))
        # Population Stats
        stats['total_inds'] = params['POPULATION_SIZE'] * (stats['gen'] + 1)
        stats['unique_inds'] = len(trackers.cache)
        stats['unused_search'] = 100 - stats['unique_inds'] / \
                                       stats['total_inds']*100
        stats['best_ever'] = max(individuals)

        # Genome Stats
        genome_lengths = [len(i.genome) for i in available]
        stats['max_genome_length'] = max(genome_lengths)
        stats['ave_genome_length'] = ave(genome_lengths)
        stats['min_genome_length'] = min(genome_lengths)

        # Used Codon Stats
        codons = [i.used_codons for i in available]
        stats['max_used_codons'] = max(codons)
        stats['ave_used_codons'] = ave(codons)
        stats['min_used_codons'] = min(codons)

        # Tree Depth Stats
        depths = [i.depth for i in available]
        stats['max_tree_depth'] = max(depths)
        stats['ave_tree_depth'] = ave(depths)
        stats['min_tree_depth'] = min(depths)

        # Tree Node Stats
        nodes = [i.nodes for i in available]
        stats['max_tree_nodes'] = max(nodes)
        stats['ave_tree_nodes'] = ave(nodes)
        stats['min_tree_nodes'] = min(nodes)

        # Fitness Stats
        fitnesses = [i.fitness for i in available]
        stats['ave_fitness'] = ave(fitnesses)
        stats['best_fitness'] = stats['best_ever'].fitness

    # Save fitness plot information
    if params['SAVE_PLOTS'] and not params['DEBUG']:
        if not end:
            trackers.best_fitness_list.append(stats['best_ever'].fitness)
        if params['VERBOSE'] or end:
            save_best_fitness_plot()

    # Print statistics
    if params['VERBOSE']:
        if not end:
            print_stats()
    elif not params['SILENT']:
        perc = stats['gen'] / (params['GENERATIONS']+1) * 100
        stdout.write("Evolution: %d%% complete\r" % perc)
        stdout.flush()

    # Generate test fitness on regression problems
    if params['PROBLEM'] in ("regression", "classification") and \
            (end or (params['COMPLETE_EVALS']
                     and stats['gen'] == params['GENERATIONS'])):
        stats['best_ever'].training_fitness = copy(stats['best_ever'].fitness)
        stats['best_ever'].evaluate(dist='test')
        stats['best_ever'].test_fitness = copy(stats['best_ever'].fitness)
        stats['best_ever'].fitness = stats['best_ever'].training_fitness

    if params['COMPLETE_EVALS'] and not params['DEBUG']:
        if stats['gen'] == params['GENERATIONS']:
            save_best_midway(stats['best_ever'])

    # Save statistics
    if not params['DEBUG']:
        save_stats(end)
        if params['SAVE_ALL']:
            save_best(end, stats['gen'])
        elif params['VERBOSE'] or end:
            save_best(end, "best")

    if end and not params['SILENT']:
        print_final_stats()


def ave(x):
    """
    :param x: a given list
    :return: the average of param x
    """

    return sum(x)/len(x)


def print_stats():
    """Print the statistics for the generation and individuals"""

    print("______\n")
    for stat in sorted(stats.keys()):
        print(" ", stat, ": \t", stats[stat])
    print("\n")


def print_final_stats():
    """
    Prints a final review of the overall evolutionary process
    """

    if params['PROBLEM'] in ("regression", "classification"):
        print("\n\nBest:\n  Training fitness:\t",
              stats['best_ever'].training_fitness)
        print("  Test fitness:\t\t", stats['best_ever'].test_fitness)
    else:
        print("\n\nBest:\n  Fitness:\t", stats['best_ever'].fitness)
    print("  Phenotype:", stats['best_ever'].phenotype)
    print("  Genome:", stats['best_ever'].genome)
    for stat in sorted(stats.keys()):
        print(" ", stat, ": \t", stats[stat])
    print("\nTime taken:\t", stats['total_time'])


def save_stats(end=False):
    """Write the results to a results file for later analysis"""
    if params['VERBOSE']:
        filename = params['FILE_PATH'] + str(params['TIME_STAMP']) + \
                   "/stats.tsv"
        savefile = open(filename, 'a')
        for stat in sorted(stats.keys()):
            savefile.write(str(stat) + "\t" + str(stats[stat]) + "\t")
        savefile.write("\n")
        savefile.close()

    elif end:
        filename = params['FILE_PATH'] + str(params['TIME_STAMP']) + \
                   "/stats.tsv"
        savefile = open(filename, 'a')
        for item in trackers.stats_list:
            for stat in sorted(item.keys()):
                savefile.write(str(item[stat]) + "\t")
            savefile.write("\n")
        savefile.close()

    else:
        trackers.stats_list.append(copy(stats))


def save_stats_headers():
    """
    Saves the headers for all stats in the stats dictionary.
    :return: Nothing.
    """

    filename = params['FILE_PATH'] + str(params['TIME_STAMP']) + "/stats.tsv"
    savefile = open(filename, 'w')
    for stat in sorted(stats.keys()):
        savefile.write(str(stat) + "\t")
    savefile.write("\n")
    savefile.close()


def save_final_stats():
    """
    Appends the total time taken for a run to the stats file.
    """

    filename = params['FILE_PATH'] + str(params['TIME_STAMP']) + "/stats.tsv"
    savefile = open(filename, 'a')
    savefile.write("Total time taken: \t" + str(stats['total_time']))
    savefile.close()


def save_params():
    """
    Save evolutionary parameters
    :return: Nothing
    """

    filename = params['FILE_PATH'] + str(params['TIME_STAMP']) + \
               "/parameters.txt"
    savefile = open(filename, 'w')

    col_width = max(len(param) for param in params.keys())
    for param in sorted(params.keys()):
        savefile.write(str(param) + ": ")
        spaces = [" " for _ in range(col_width - len(param))]
        savefile.write("".join(spaces) + str(params[param]) + "\n")
    savefile.close()


def save_best(end=False, name="best"):

    filename = params['FILE_PATH'] + str(params['TIME_STAMP']) + "/" + \
               str(name) + ".txt"
    savefile = open(filename, 'w')
    savefile.write("Generation:\n" + str(stats['gen']) + "\n\n")
    savefile.write("Phenotype:\n" + str(stats['best_ever'].phenotype) + "\n\n")
    savefile.write("Genotype:\n" + str(stats['best_ever'].genome) + "\n")
    savefile.write("Tree:\n" + str(stats['best_ever'].tree) + "\n")
    if params['PROBLEM'] in ("regression", "classification"):
        if end:
            savefile.write("\nTraining fitness:\n" +
                           str(stats['best_ever'].training_fitness))
            savefile.write("\nTest fitness:\n" +
                           str(stats['best_ever'].test_fitness))
        else:
            savefile.write("\nFitness:\n" + str(stats['best_ever'].fitness))
    else:
        savefile.write("\nFitness:\n" + str(stats['best_ever'].fitness))
    savefile.close()


def save_best_midway(best_ever):
    filename = params['FILE_PATH'] + str(params['TIME_STAMP']) + "/best_" + \
               str(stats['gen']) + ".txt"
    savefile = open(filename, 'w')
    t1 = time.clock()
    trackers.time_list.append(t1)
    time_taken = timedelta(seconds=trackers.time_list[-1] -
                           trackers.time_list[0])
    savefile.write("Generation:\n" + str(stats['gen']) + "\n\n")
    savefile.write("Phenotype:\n" + str(best_ever.phenotype) + "\n\n")
    savefile.write("Genotype:\n" + str(best_ever.genome) + "\n")
    savefile.write("Tree:\n" + str(best_ever.tree) + "\n")
    if params['PROBLEM'] in ("regression", "classification"):
        savefile.write("\nTraining fitness:\t" +
                       str(stats['best_ever'].training_fitness))
        savefile.write("\nTest fitness:\t" +
                       str(stats['best_ever'].test_fitness))
    else:
        savefile.write("\nFitness:\t" + str(stats['best_ever'].fitness))
    savefile.write("\nTotal time:\t" + str(time_taken))
    savefile.close()


def generate_folders_and_files():
    """
    Generates necessary folders and files for saving statistics and parameters.
    """

    if params['EXPERIMENT_NAME']:
        params['FILE_PATH'] = getcwd() + "/results/" + params[
            'EXPERIMENT_NAME'] + "/"
    else:
        params['FILE_PATH'] = getcwd() + "/results/"

    # Generate save folders
    if not path.isdir(params['FILE_PATH']):
        mkdir(params['FILE_PATH'])
    if not path.isdir(params['FILE_PATH'] + str(params['TIME_STAMP'])):
        mkdir(params['FILE_PATH'] + str(params['TIME_STAMP']))

    save_params()
    save_stats_headers()
