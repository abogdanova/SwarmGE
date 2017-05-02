import matplotlib
import pandas as pd
from os import path, pathsep
import numpy as np

from utilities.stats.trackers import best_fitness_list

matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rc('font', family='Times New Roman')


def save_best_fitness_plot():
    """
    Saves a plot of the current fitness.
    
    :return: Nothing
    """
    from algorithm.parameters import params

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(best_fitness_list)
    ax1.set_ylabel('fitness', fontsize=14)
    ax1.set_xlabel('Generation', fontsize=14)
    plt.title("Best fitness")
    plt.savefig(path.join(params['FILE_PATH'], "fitness.pdf"))
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
    plt.savefig(path.join(params['FILE_PATH'], (name + '.pdf')))
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
        s = "utilities.stats.save_plots.save_plot_from_file\n" \
            "Error: stat %s does not exist" % stat_name
        raise Exception(s)

    # Plot the data
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(stat)
    plt.title(stat_name)

    # Get save path
    save_path = pathsep.join(filename.split(pathsep)[:-1])

    # Save plot
    plt.savefig(path.join(save_path, (stat_name + '.pdf')))
    plt.close()


def save_box_plot(data, names, title):
    """
    Given an array of some data, and a list of names of that data, generate
    and save a box plot of that data.

    :param data: An array of some data to be plotted.
    :param names: A list of names of that data.
    :param title: The title of the plot.
    :return: Nothing
    """

    from algorithm.parameters import params
    
    import matplotlib.pyplot as plt
    plt.rc('font', family='Times New Roman')
    
    # Set up the figure.
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    
    # Plot tight layout.
    plt.tight_layout()
    
    # Plot the data.
    ax1.boxplot(np.transpose(data), 1)
    
    # Plot title.
    plt.title(title)
    
    # Generate list of numbers for plotting names.
    nums = list(range(len(data))[1:]) + [len(data)]
    
    # Plot names for each data point.
    plt.xticks(nums, names, rotation='vertical', fontsize=8)
    
    # Save plot.
    plt.savefig(path.join(params['FILE_PATH'], (title + '.pdf')))
    
    # Close plot.
    plt.close()
