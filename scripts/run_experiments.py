""" This program cues up and executes multiple runs of PYGE. Results of runs
    are parsed and placed in a spreadsheet for easy visual analysis.

    Copyright (c) 2014 Michael Fenton
    Hereby licensed under the GNU GPL v3."""

from utilities.algorithm.initialise_run import check_python_version

check_python_version()

from multiprocessing import Pool
from subprocess import call
import sys

from algorithm.parameters import params, set_params
from scripts.parse_stats import parse_stats_from_runs


def execute_run(seed):
    """
    Initialise all aspects of a run.
    
    :return: Nothing.
    """

    exec_str = "source activate py35;python ponyge.py " \
               "--random_seed " + str(seed) + " " + " ".join(sys.argv[1:])
    
    call(exec_str, shell=True)


def execute_runs():
    """
    Execute multiple runs in series using multiple cores.
    
    :return: Nothing.
    """

    # Initialise empty list of results.
    results = []

    # Initialise pool of workers.
    pool = Pool(processes=params['CORES'])

    for run in range(params['RUNS']):
        # Execute a single evolutionary run.
        results.append(pool.apply_async(execute_run, (run,)))

    for result in results:
        result.get()

    # Close pool once runs are finished.
    pool.close()
    
    # Save spreadsheets and all plots for runs so far.
    parse_stats_from_runs(params['EXPERIMENT_NAME'], True)


if __name__ == "__main__":
    # Setup run parameters.
    set_params(sys.argv[1:], create_files=False)
    
    # Execute multiple runs.
    execute_runs()
