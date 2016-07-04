from stats.stats import generate_folders_and_files
from algorithm.parameters import params
from utilities import trackers
from datetime import datetime
from sys import version_info
import time


def check_python_version():
    """
    Check the python version to ensure it is correct. PonyGE uses Python 3.
    :return: Nothing
    """

    if version_info.major < 3:
        print("Error: Python version not supported. Must use Python 3.x")
        quit()


def initialise_run_params():
    """
    Initialises all lists and trackers. Generates save folders and initial
    parameter files.
    :return: Nothing
    """

    #
    time1 = datetime.now()
    trackers.time_list.append(time.clock())
    hms = "%02d%02d%02d" % (time1.hour, time1.minute, time1.second)
    params['TIME_STAMP'] = (str(time1.year)[2:] + "_" + str(time1.month) +
                            "_" + str(time1.day) + "_" + hms +
                            "_" + str(time1.microsecond))
    print("\nStart:\t", time1, "\n")

    # Generate save folders and files
    if params['DEBUG']:
        print("Seed:\t", params['RANDOM_SEED'], "\n")
    else:
        generate_folders_and_files()
