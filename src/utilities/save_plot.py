from utilities.trackers import best_fitness_list
import pandas as pd
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

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(best_fitness_list)
    ax1.set_ylabel('fitness', fontsize=14)
    ax1.set_xlabel('Generation', fontsize=14)
    plt.title("Best fitness")
    plt.savefig(
        params['FILE_PATH'] + str(params['TIME_STAMP']) + '/fitness.pdf')
    plt.close()


def save_plot_from_data(data, name):
    """
    Saves a plot of a given set of data.
    :param data: the data to be plotted
    :param name: the name of the data to be plotted.
    :return: Nothing.
    """
    from algorithm.parameters import params

    # Plot the data
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(data)
    plt.title(name)
    plt.savefig(
        params['FILE_PATH'] + str(params['TIME_STAMP']) + '/' + name + '.pdf')
    plt.close()


def save_plot_from_file(filename, stat_name):
    """
    Saves a plot of a given stat from the stats file.
    :param filename: a full specified path to a .csv stats file.
    :param stat_name: the stat of interest for plotting.
    :return: Nothing.
    """

    # Read in the data
    data = pd.read_csv(filename, sep="\t")
    try:
        stat = list(data[stat_name])
    except KeyError:
        print("\nError: stat", stat_name, "does not exist")
        quit()

    # Plot the data
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(stat)
    plt.title(stat_name)

    # Get save path
    save_path = "/".join(filename.split("/")[:-1])

    # Save plot
    plt.savefig(save_path + '/' + stat_name + '.pdf')
    plt.close()


def save_average_plot_across_runs(filename):
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

    The required file can be generated using
        
        stats.parse_stats.parse_stat_from_runs()

    Generates a .pdf graph of average value with standard deviation.
    :param filename: the full file name of a .csv file containing the fitnesses
    of each generation of multiple runs. Must be comma separated.
    :return: Nothing.
    """

    stat_name = filename.split("/")[-1].split(".")[0]

    data = np.genfromtxt(filename, delimiter=',')[:, :-1]
    ave = np.nanmean(data, axis=1)
    std = np.nanstd(data, axis=1)
    max_gens = len(ave)

    stdmax = ave + std
    stdmin = ave - std
    r = range(1, max_gens + 1)

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    ax1.plot(r, ave, color="blue")
    plt.xlim(0, max_gens + 1)
    ax1.fill_between(r, stdmin, stdmax, color="DodgerBlue", alpha=0.5)

    plt.title("Average " + stat_name)
    plt.xlabel('Generation', fontsize=14)
    plt.ylabel('Average ' + stat_name, fontsize=14)
    new_filename = filename.split(".")[0]
    plt.savefig(str(new_filename) + ".pdf")
    plt.close()
