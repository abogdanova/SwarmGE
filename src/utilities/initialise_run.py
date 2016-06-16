from stats.stats import generate_folders_and_files
from algorithm.parameters import params
from utilities import trackers
from datetime import datetime
import time


def initialise_run_params():
    # Initialise time lists and trackers
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
