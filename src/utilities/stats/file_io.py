import types
from os import path, getcwd, makedirs

from algorithm.parameters import params
from stats.stats import stats
from utilities.stats import trackers


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
