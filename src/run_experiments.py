""" This program cues up and executes multiple runs of PYGE. Results of runs
    are parsed and placed in a spreadsheet for easy visual analysis.

    Copyright (c) 2014 Michael Fenton
    Hereby licensed under the GNU GPL v3."""

from utilities.algorithm.initialise_run import check_python_version

check_python_version()

from multiprocessing import cpu_count
from operator import itemgetter
from datetime import datetime
import sys

from experimental import setup_run
import ponyge
from algorithm.parameters import params, set_params
from stats.parse_stats import parse_stat_from_runs


def execute_multi_core():
    """ Execute multiple runs in series using multiple cores to evaluate each
        population. """

    run_results = []
    time1 = datetime.now()

    print("\nMulti-Run Start:", time1, "\n")

    for run in range(params['RUNS']):

        if run > 0:
            # Setup each subsequent run like a brand new run.
            from utilities.algorithm import initialise_run
            from stats.stats import stats
            from utilities.stats import trackers

            stats.__init__()
            trackers_lists = [i for i in dir(trackers)
                              if not i.startswith("__")]
            for t_list in trackers_lists:
                init_string = "trackers." + t_list + ".__init__()"
                eval(init_string)

            params['RANDOM_SEED'] = None
            initialise_run.initialise_run_params()

        # Execute a single evolutionary run.
        run_results.append(ponyge.mane())

        if run > 0:
            # Save spreadsheet and average fitness plot for runs so far.
            parse_stat_from_runs(params['EXPERIMENT_NAME'],
                                 ["best_fitness"], True)

    time2 = datetime.now()
    total_time = time2 - time1

    # Write info about best indiv from each run to a file.
    filename = "../results/" + str(params['EXPERIMENT_NAME']) + "/" + \
               str(params['EXPERIMENT_NAME']) + ".txt"
    savefile = open(filename, 'w')
    for ans, answer in enumerate(run_results):
        savefile.write("Run " + str(ans) + "\tName: " + str(answer[0]) +
                       "\tBest: " + str(answer[1]) + "\n")
    run_results.sort(key=itemgetter(1))

    # Write info about best overall result.
    savefile.write("\nBEST: " + str(run_results[-1]))
    savefile.write("\n\nTotal time taken for " + str(params['RUNS']) +
                   " runs: " + str(total_time))
    savefile.close()

    print("\nTotal time taken for", params['RUNS'], "runs:", total_time)
    print("\nBEST:", run_results[-1])


if __name__ == "__main__":
    # Setup run parameters.
    params['EXPERIMENT_NAME'] = "Test 1 - Real World Scheduling high " \
                                "density " + params['MACHINE']
    set_params(sys.argv)
    params['CORES'] = cpu_count()

    # Setup network parameters.
    setup_run.main()

    # Execute multiple runs.
    execute_multi_core()
