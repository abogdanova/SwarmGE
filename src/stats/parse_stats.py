from os import getcwd, listdir
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib
import getopt
import sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rc('font', family='Times New Roman')


def help_message():
    """
    Prints a help message to explain the usage of this file.
    :return: Nothing
    """

    lines_1 = ["Welcome to PonyGE's post-run stats parser.",
               "-------------------",
               "The following are the available command line args. You must "
               "specify an experiment name and at least one stat to be parsed."
               ""]

    lines_2 = [["\t--help:", "Shows this help message."],
               ["\t--experiment_name:", "The name of the containing folder in "
                                        "which target runs are saved, e.g. "
                                        "in /results/[EXPERIMENT_NAME]."],
               ["\t--stats:", "A comma-separated list of stats to be parsed. "
                              "Specified stats must be valid keys from the "
                              "stats.stats.stats dictionary. "
                              "IMPORTANT: MUST NOT CONTAIN ANY SPACES."],
               ["\t--graph:", "Saves a .pdf figure of each stat specified."]]

    for line in lines_1:
        print(line)
    col_width = max(len(line[0]) for line in lines_2)
    for line in sorted(lines_2):
        print(" ".join(words.ljust(col_width) for words in line))


def parse_opts(command_line_args):
    """
    Parses command line arguments and returns usable variables which are used
    as inputs for other functions in this file.
    :param command_line_args: flags passed in from the command line at
    execution
    :return: experiment_name: the name of the containing folder of results,
             stats: a list of strings. Each string is a valid key from the
                    stats.stats.stats dictionary.
             graph: an optional boolean flag for graphing specified stats.
    """

    try:
        opts, args = getopt.getopt(command_line_args[1:], "",
                                   ["help", "experiment_name=", "stats=",
                                    "graph"])
    except getopt.GetoptError as err:
        print("In order to parse stats you need to specify the location of the"
              " target stats files and a list of desired stats to parse. \n",
              "Run python parse_stats.py --help for more info")
        print(str(err))
        exit(2)

    if not opts:
        print("In order to parse stats you need to specify the location of the"
              " target stats files and a list of desired stats to parse. \n",
              "Run python parse_stats.py --help for more info")
        exit(2)

    experiment_name, stats, graph = None, None, False

    for opt, arg in opts:
        if opt == "--help":
            help_message()
            exit()
        elif opt == "--experiment_name":
            experiment_name = arg
        elif opt == "--stats":
            if arg[0] == "[" and arg[-1] == "]":
                stats = arg[1:-1].split(",")
            else:
                stats = arg.split(",")
        elif opt == "--graph":
            graph = True

    return experiment_name, stats, graph


def parse_stat_from_runs(experiment_name, stats, graph):
    """
    Analyses a list of given stats from a group of runs saved under an
    "experiment_name" folder. Creates a summary .csv file which can be used by
    plotting functions in utilities.save_plot. Saves a file of the format:

        run0_gen0       run1_gen0       .   .   .   run(n-1)_gen0
        run0_gen1       run1_gen1       .   .   .   run(n-1)_gen1
        run0_gen2       run1_gen2       .   .   .   run(n-1)_gen2
        .               .               .   .   .   .
        .               .               .   .   .   .
        .               .               .   .   .   .
        run0_gen(n-1)   run1_gen(n-1)   .   .   .   run(n-1)_gen(n-1)
        run0_gen(n)     run1_gen(n)     .   .   .   run(n-1)_gen(n)

    Generated file is compatible with

        utilities.save_plot.save_average_plot_across_runs()

    :param experiment_name: The name of a collecting folder within the
    ./results folder which holds multiple runs.
    :param stats: A list of the names of the stats to be parsed.
    :return: Nothing.
    """

    # Since results files are not kept in source directory, need to escape
    # one folder.
    path = getcwd() + "/../results/"

    if experiment_name:
        path += experiment_name + "/"
    else:
        print("Error: experiment name not specified")
        quit()

    runs = [run for run in listdir(path) if "." not in run]

    for stat in stats:
        if stat == "best_ever":
            print("Error: Cannot graph instances of individual class. Do not"
                  " specify 'best_ever' as stat to be parsed.")
            quit()
        summary_stats = []

        for run in runs:
            data = pd.read_csv(path + str(run) + "/stats.tsv", sep="\t")
            try:
                summary_stats.append(list(data[stat]))
            except KeyError:
                print("Error: stat", stat, "does not exist")
                quit()

        if stat in ["total_time", "time_taken"]:
            zero = datetime.strptime("1900-01-01 0:00:00.000000",
                                     "%Y-%m-%d %H:%M:%S.%f")
            for i, run in enumerate(summary_stats):
                summary_stats[i] = [(datetime.strptime(time,
                                                       "%H:%M:%S.%f") - zero).total_seconds()
                                    for time in run]

        summary_stats = np.asarray(summary_stats)
        summary_stats = np.transpose(summary_stats)

        np.savetxt(path + stat + ".csv", summary_stats, delimiter=",")
        if graph:
            save_average_plot_across_runs(path + stat + ".csv")


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

    data = np.genfromtxt(filename, delimiter=',')

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
    new_filename = filename[:-3] + "pdf"
    plt.savefig(str(new_filename))
    plt.close()


if __name__ == "__main__":
    experiment_name, stats, graph = parse_opts(sys.argv)
    parse_stat_from_runs(experiment_name, stats, graph)
