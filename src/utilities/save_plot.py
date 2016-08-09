from utilities.trackers import best_fitness_list
from os import getcwd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rc('font', family='Times New Roman')


def save_best_fitness_plot():
    """
    Saves a plot of the current fitness
    :return: Nothing
    """
    from algorithm.parameters import params

    fig = plt.figure()  # figsize=[20,15])
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(best_fitness_list)
    ax1.set_ylabel('fitness', fontsize=14)
    ax1.set_xlabel('Generation', fontsize=14)
    plt.savefig(params['FILE_PATH']+str(params['TIME_STAMP'])+'/fitness.pdf')
    plt.close()


def save_average_fitness_plot(filename):
    """
    Saves an average plot of multiple runs. Input file data must be of the
    format:

        run0_gen0       run1_gen0       .   .   .   run(n-1)_gen0
        run0_gen1       run1_gen1       .   .   .   run(n-1)_gen1
        run0_gen2       run1_gen2       .   .   .   run(n-1)_gen2
        .               .               .   .   .   .
        .               .               .   .   .   .
        .               .               .   .   .   .
        run0_gen(n-1)   run1_gen(n-1)   .   .   .   run(n-1)_gen(n-1)
        run0_gen(n)     run1_gen(n)     .   .   .   run(n-1)_gen(n)

    No headers are required in the file. (i.e. this program will not execute
    correctly if there are headers present. THIS WILL BE FIXED EVENTUALLY!

    Generated graphs are:
        .pdf of average fitness with standard deviation
    :param filename: the full file name of a .csv file containing the fitnesses
    of each generation of multiple runs. Must be comma separated.
    :return: Nothing.
    """

    data = np.genfromtxt(filename, delimiter=',')[:,:-1]
    ave = np.nanmean(data, axis=1)
    std = np.nanstd(data, axis=1)
    max_gens = len(ave)

    stdmax = ave + std
    stdmin = ave - std
    r = range(1, max_gens + 1)

    fig = plt.figure() # figsize=[20,15])
    ax1 = fig.add_subplot(1, 1, 1)

    ax1.plot(r, ave, color="blue")
    plt.xlim(0, max_gens + 1)
    ax1.fill_between(r, stdmin, stdmax, color="DodgerBlue", alpha=0.5)

    plt.xlabel('Generation', fontsize=14)
    plt.ylabel('Average Fitness', fontsize=14)
    new_filename = filename.split(".")[0]
    plt.savefig(str(new_filename) + ".pdf")
    plt.close()
