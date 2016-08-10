from os import getcwd, listdir
import pandas as pd
import numpy as np


def parse_stat_from_runs(experiment_name, stat_name):
    """
    Analyses a given stat from a group of runs saved under an "experiment_name"
    folder. Creates a summary .csv file which can be used by plotting functions
    in utilities.save_plot. Saves a file of the format:

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
    :param stat_name: The name of the stat to be parsed.
    :return: Nothing.
    """

    summary_stats = []
    path = getcwd() + "/results/" + experiment_name + "/"
    runs = [run for run in listdir(path) if not "." in run]

    for run in runs:
        data = pd.read_csv(path + str(run) + "/stats.tsv", sep="\t")
        try:
            summary_stats.append(list(data[stat_name]))
        except KeyError:
            print("Error: stat", stat_name, "does not exist")
            quit()
            
    summary_stats = np.asarray(summary_stats)
    summary_stats = np.transpose(summary_stats)
    np.savetxt(path + stat_name + ".csv", summary_stats, delimiter=",")
