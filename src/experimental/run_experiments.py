""" This program cues up and executes multiple runs of PYGE. Results of runs
    are parsed and placed in a spreadsheet for easy visual analysis.

    Copyright (c) 2014 Michael Fenton
    Hereby licensed under the GNU GPL v3."""

from multiprocessing import cpu_count, Pool
from shutil import copytree, rmtree
from os import path, getcwd, mkdir
from operator import itemgetter
from socket import gethostname
from datetime import datetime
import create_graphs, ponyge
from time import sleep

def execute_single_core(FOLDER, RUN_FOLDER):
    """execute multiple runs"""
    first_progs = []
    first_fits = []
    answers = []
    time1 = datetime.now()

    print("\nMulti-Run Start:", time1, "\n")

    for run in range(RUNS):
        answer = ponyge.mane()
        first_progs.append(answer)

        if path.isdir(str(curr_path) + "/Results/" + str(RUN_FOLDER) + "/" + str(FOLDER)):
            pass
        else:
            mkdir(str(curr_path) + "/Results/" + str(RUN_FOLDER) + "/" + str(FOLDER))

        # Write this info to a spreadsheet
        results = open("Results/" + str(answer[0]) + "/" + str(answer[0]) + ".txt", 'r')
        lines = iter(results)
        if run == 0:
            all_results = open("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv", "w")
            n = 0
            for line in lines:
                result = line.split()
                if result == []:
                    break
                elif result[0] == '#':
                    line = next(lines)
                while result[0] == "Gen:":
                    all_results.write(str(float(result[3])) + ",\n")
                    n+=1
                    break
            all_results.close()
        else:
            all_results = open("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv", "r")
            prev_data = all_results.readlines()
            all_results.close()
            n = 0
            for line in lines:
                result = line.split()
                if result == []:
                    break
                elif result[0] == '#':
                    line = next(lines)
                while result[0] == "Gen:":
                    prev_data[n] = str(float(result[3])) + "," + prev_data[n]
                    n+=1
                    break
            with open("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv", "w") as file:
                file.writelines(prev_data)
        copytree("Results/" + str(answer[0]), "Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + "/" + str(answer[0]))
        rmtree(str(curr_path) + "/Results/" + str(answer[0]), ignore_errors=True)

        if run>= 1:
            create_graphs.mane("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv")

    time2 = datetime.now()
    total_time = time2 - time1

    # Write info about best indiv from each run to a file.
    filename = "Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) +".txt"
    savefile = open(filename, 'w')
    for ans, answer in enumerate(first_progs):
        savefile.write("Run " + str(ans) + "\tName: " + str(answer[0]) + "\tBest: " + str(answer[1]) + "\n")
    first_progs.sort(key=itemgetter(1))

    savefile.write("\nBEST: " + str(first_progs[-1]))
    savefile.write("\n\nTotal time taken for " + str(RUNS) + " runs: " + str(total_time))
    savefile.close()

    print("\nTotal time taken for",RUNS,"runs:", total_time)
    print("\nBEST:",first_progs[-1])

def execute_multi_core(FOLDER, RUN_FOLDER, CORES):
    """ Execute multiple runs in series using multiple cores to evaluate each
        population. """
    first_progs = []
    first_fits = []
    time1 = datetime.now()

    print("\nMulti-Run Start:", time1, "\n")
    ponyge.MULTICORE = True
    ponyge.CORES = CORES

    for run in range(RUNS):
        answer = ponyge.mane()
        first_progs.append(answer)

        if path.isdir(str(curr_path) + "/Results/" + str(RUN_FOLDER) + "/" + str(FOLDER)):
            pass
        else:
            mkdir(str(curr_path) + "/Results/" + str(RUN_FOLDER) + "/" + str(FOLDER))

        # Write this info to a spreadsheet
        results = open("Results/" + str(answer[0]) + "/" + str(answer[0]) + ".txt", 'r')
        lines = iter(results)
        if run == 0:
            all_results = open("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv", "w")
            n = 0
            for line in lines:
                result = line.split()
                if result == []:
                    break
                elif result[0] == '#':
                    line = next(lines)
                while result[0] == "Gen:":
                    if result[3] == "None":
                        all_results.write("None,\n")
                    else:
                        all_results.write(str(float(result[3])) + ",\n")
                    n+=1
                    break
            all_results.close()
        else:
            all_results = open("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv", "r")
            prev_data = all_results.readlines()
            all_results.close()
            n = 0
            for line in lines:
                result = line.split()
                if result == []:
                    break
                elif result[0] == '#':
                    line = next(lines)
                while result[0] == "Gen:":
                    if result[3] == "None":
                        prev_data[n] = "None," + prev_data[n]
                    else:
                        prev_data[n] = str(float(result[3])) + "," + prev_data[n]
                    n += 1
                    break
            with open("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv", "w") as file:
                file.writelines(prev_data)
        copytree("Results/" + str(answer[0]), "Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + "/" + str(answer[0]))
        rmtree(str(curr_path) + "/Results/" + str(answer[0]), ignore_errors=True)

        if run>= 1:
            create_graphs.mane("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv")

    time2 = datetime.now()
    total_time = time2 - time1

    # Write info about best indiv from each run to a file.
    filename = "Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) +".txt"
    savefile = open(filename, 'w')
    for ans, answer in enumerate(first_progs):
        savefile.write("Run " + str(ans) + "\tName: " + str(answer[0]) + "\tBest: " + str(answer[1]) + "\n")
    first_progs.sort(key=itemgetter(1))

    savefile.write("\nBEST: " + str(first_progs[-1]))
    savefile.write("\n\nTotal time taken for " + str(RUNS) + " runs: " + str(total_time))
    savefile.close()

    print("\nTotal time taken for",RUNS,"runs:", total_time)
    print("\nBEST:",first_progs[-1])

def execute_multi_single_core(FOLDER, RUN_FOLDER, CORES):
    """execute multiple runs"""
    first_progs = []
    first_fits = []
    answers = []
    time1 = datetime.now()

    print("\nMulti-Run Start:", time1, "\n")
    ponyge.MULTICORE = False
    pool = Pool(processes=CORES)

    for run in range(RUNS):
        answer = pool.apply_async(ponyge.mane)
        answers.append(answer)
        sleep(1)

    for result in answers:
        answer = result.get()
        first_progs.append(answer)

    for run, answer in enumerate(first_progs):
        if path.isdir(str(curr_path) + "/Results/" + str(RUN_FOLDER) + "/" + str(FOLDER)):
            pass
        else:
            mkdir(str(curr_path) + "/Results/" + str(RUN_FOLDER) + "/" + str(FOLDER))

        # Write this info to a spreadsheet
        results = open("Results/" + str(answer[0]) + "/" + str(answer[0]) + ".txt", 'r')
        lines = iter(results)
        if run == 0:
            all_results = open("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv", "w")
            n = 0
            for line in lines:
                result = line.split()
                if result == []:
                    break
                elif result[0] == '#':
                    line = next(lines)
                while result[0] == "Gen:":
                    all_results.write(str(float(result[3])) + ",\n")
                    n+=1
                    break
            all_results.close()
        else:
            all_results = open("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv", "r")
            prev_data = all_results.readlines()
            all_results.close()
            n = 0
            for line in lines:
                result = line.split()
                if result == []:
                    break
                elif result[0] == '#':
                    line = next(lines)
                while result[0] == "Gen:":
                    prev_data[n] = str(float(result[3])) + "," + prev_data[n]
                    n+=1
                    break
            with open("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv", "w") as file:
                file.writelines(prev_data)
        copytree("Results/" + str(answer[0]), "Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + "/" + str(answer[0]))
        rmtree(str(curr_path) + "/Results/" + str(answer[0]), ignore_errors=True)

        if run>= 1:
            create_graphs.mane("Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) + ".csv")

    pool.close()
    time2 = datetime.now()
    total_time = time2 - time1

    # Write info about best indiv from each run to a file.
    filename = "Results/" + str(RUN_FOLDER) + "/" + str(FOLDER) +".txt"
    savefile = open(filename, 'w')
    for ans, answer in enumerate(first_progs):
        savefile.write("Run " + str(ans) + "\tName: " + str(answer[0]) + "\tBest: " + str(answer[1]) + "\n")
    first_progs.sort(key=itemgetter(1))

    savefile.write("\nBEST: " + str(first_progs[-1]))
    savefile.write("\n\nTotal time taken for " + str(RUNS) + " runs: " + str(total_time))
    savefile.close()

    print("\nTotal time taken for",RUNS,"runs:", total_time)
    print("\nBEST:",first_progs[-1])

if __name__ == '__main__':

    ponyge.EXPERIMENT_MANAGER = True
    ponyge.HOLD_NETWORK = False
    ponyge.GRAMMAR_FILE = "grammars/scheduling_complete.bnf"
    ponyge.FITNESS_FUNCTION = ponyge.Scheduling_Optimisation()
    ponyge.POPULATION_SIZE = 1000
    ponyge.GENERATION_SIZE = ponyge.POPULATION_SIZE
    ponyge.GENERATIONS = 200
    RUNS = 20

    """This is only to be used on local machines to run experiments in sequence
    (all individuals in a single experiment are evaluated in parallel). When
    running batches of experiments on the servers, it is better not to use
    multi-core mode and to run all experiments in paralell (with individuals
    evaluated in sequence)."""
    MULTICORE = True
    CORES = cpu_count() - 2

    """Use this to turn on debugging mode. This mode doesn't write any
    files and should be used when you want to test new methods or grammars,
    etc."""
    ponyge.DEBUG = False

    """Use this to save the phenotype of the best individual from each generation.
    This is useful for making gifs of the evolution of the best indivs, but can
    generate a lot of files."""
    ponyge.SAVE_ALL = not ponyge.DEBUG

    """Saves a CDF graph of the first individual and the final evolved individual.
    Also saves a graph of the evolution of the best fitness result for each
    generation."""
    ponyge.SAVE_PLOTS = not ponyge.DEBUG

    """Tracks duplicate individuals across evolution by saving a string of each
    phenotype in a big list of all phenotypes. Gives you an idea of how much
    repetition is in standard GE/GP. EATS memory, so only use if you have small
    phenotypes. Must be True if you're using REMOVE_DUPLICATES."""
    ponyge.CACHE = True

    """ Uses the cache to look up the fitness of duplicate individuals. CACHE
        must be True if you want to use this (obviously)"""
    ponyge.LOOKUP_FITNESS = False

    """ Uses the cache to give a bad fitness to duplicate individuals. CACHE
        must be True if you want to use this (obviously)"""
    ponyge.LOOKUP_BAD_FITNESS = True

    """ This is the call to tell the program whether or not to run the
        simulation environment in MATLAB. If the simulation has already been
        run with the same settings then there is no need to run it again as
        the relevant files have already been created"""
    SIMULATION = False

    """ This is the number of UEs to place in the network environment. Full
        spec is 1260 users, debug/testing spec can be set lower to save
        computational time"""
    N_USERS = 5000 # 1260

    """ The number of individual scenarios that the individual is to be tested
        on. A single scenario is a unique distribution of UEs on the map. The
        more scenarios an individual is tested on, the more generalisable the
        evolved control function will be. However, more scenarios means a
        longer run time."""
    SCENARIOS = 10

    """ Use this to cycle between training and test data. The training data
        set is [0, SCENARIOS]. Test data set increases the STARTS to
        [SCENARIOS, SCENARIOS*2]
    """
    scenario = 0

    """ Now including different SC distributions for training and test data.
        This means you can train on a much smaller network, thereby saving a
        bunch of time and computational effort. Testing then takes place on a
        larger network for longer. Test network only works if TEST_DATA is
        turned on. """
    N_SMALL_TRAINING = 30
    N_SMALL_TEST = 30

    """ Evolve solutions on a realistic version of the network. SINR is capped
        at 30 db and has a resolution of 1 db. Only the top 10 interfering
        cells are used to calculate SINR. Channel gain matrix is quantized to
        1 db."""
    REALISTIC = True
    ponyge.REALISTIC = REALISTIC

    """ Stress test the network by placing UEs in the worst possible locations.
    """
    stress_test = False

    """ How much information do we pull out of the estimated SINR matrix?
        Level 1: use quantized channel gain matrix
        Level 2: SINR values quantized to [0:2:30]
        Level 3: SINR values averaged over ABS and non-ABS, quantized to
                 [0:2:30]
    """
    difficulty = 3  # 1 / 2 / 3
    ponyge.difficulty = difficulty

    """ Use this to evaluate the final evolved individaul on an unseen set of
        test data. Test data is the same for all runs. Final best solution
        will display the fitness of the test data rather than the training
        data. If False then everything is evolved and tested on the training
        dataset. """
    TEST_DATA = True
    ponyge.TEST_DATA = TEST_DATA

    hostname = gethostname().split('.')
    name = hostname[0]
    FOLDER_NAME = "Test 23 - Real World Scheduling high density " + name
    global curr_path
    curr_path = getcwd()

    NAME = " ".join(FOLDER_NAME.split("-")[1].split()[:-1])
    run_matlab = False

    if not SIMULATION and not path.isfile(curr_path + "/bell_simulation/gain_" + str(N_SMALL_TRAINING) + ".mat"):
        if TEST_DATA and not path.isfile(curr_path + "/bell_simulation/gain_" + str(N_SMALL_TEST) + ".mat"):
            print("\nError: gain matrices do not exist for networks with", N_SMALL_TRAINING, "and", N_SMALL_TEST, "small cells.\n")
            sleep(1)
            print("Matlab must be run to generate new gain matrices.\n")
        else:
            print("\nError: gain matrix does not exist for network with", N_SMALL_TRAINING, "small cells.\n")
            sleep(1)
            print("Matlab must be run to generate a new gain matrix.\n")
        sleep(1)
        user_input = input("Do you wish to run Matlab? ['yes' | 'no']\n\n")
        if user_input in ["yes", "y", "Yes", "YES", "Y"]:
            run_matlab = True
        elif user_input in ["no", "n", "NO", "No", "N"]:
            print("\nSuit yourself so.\n")
            quit()

    elif TEST_DATA and not SIMULATION and not path.isfile(curr_path + "/bell_simulation/gain_" + str(N_SMALL_TEST) + ".mat"):
        print("\nError: gain matrix does not exist for network with", N_SMALL_TEST, "small cells.\n")
        sleep(1)
        print("Matlab must be run to generate a new gain matrix.\n")
        sleep(1)
        user_input = input("Do you wish to run Matlab? ['yes' | 'no']\n\n")
        if user_input in ["yes", "y", "Yes", "YES", "Y"]:
            run_matlab = True
        elif user_input in ["no", "n", "NO", "No", "N"]:
            print("\nSuit yourself so.\n")
            quit()

    if not TEST_DATA:
        DIST = "training"

    import hold_network_info
    hold_network_info.init(run_matlab, N_USERS,
        training=N_SMALL_TRAINING,
        test=N_SMALL_TEST,
        both=TEST_DATA,
        set="training",
        b_lim=15,
        STRESS=stress_test,
        ITERATIONS=SCENARIOS,
        SCENARIO=scenario)

    if ponyge.FITNESS_FUNCTION.__class__.__name__ == "Scheduling_Optimisation":
        # We can pre-compute the network stats to schedule really fast.

        print("Pre-computing network...")
        import standalone_scheduler

        stdal_sched = standalone_scheduler.Standalone_Fitness(
            realistic=REALISTIC, difficulty=difficulty)
        pre_computed_network = stdal_sched.pre_compute_network()
    else:
        pre_computed_network = None
        stdal_sched = None

    ponyge.pre_computed_network = pre_computed_network
    ponyge.stdal_sched = stdal_sched

    # Create sorted folders for individual runs
    if path.isdir(str(curr_path) + "/Results/" + str(FOLDER_NAME)):
        pass
    else:
        mkdir(str(curr_path) + "/Results/" + str(FOLDER_NAME))

    if MULTICORE:
        execute_multi_core(NAME, FOLDER_NAME, CORES)
    else:
        execute_multi_single_core(NAME, FOLDER_NAME, CORES)
        # execute_single_core(NAME, FOLDER_NAME)
