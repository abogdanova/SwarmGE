# Network optimisation program/function which will take a number of inputs
# for a heteregenous cellular network consisting of combinations of Macro
# Cells (MCs) and Small Cells (SCs) and output network configuration
# settings such that the User Equipment (UE) throughput is maximised.

# Copyright (c) 2014
# Michael Fenton


from random import randint, random, seed, getstate, setstate, uniform
from matplotlib.ticker import FormatStrFormatter, LogLocator
from os import getcwd, path, mkdir, getpid
from numpy import mean, sin, cos, tan, log, sqrt
from sys import platform
from math import floor, ceil
import matplotlib.pyplot as plt
plt.rc('font', family='Times New Roman')
from operator import itemgetter
from copy import deepcopy, copy
from datetime import datetime
import numpy.ma as ma
import scipy.io as io
import experimental.deap_1 as opt
# import cma_binary as opt
import numpy as np
import psutil

from utilities.fitness.math_functions import pdiv

np.seterr(divide='ignore', invalid='ignore')


class Optimise_Network():
    """A class for optimising a network given some network conditions"""

    def __init__(self,
                SC_power=None,
                SC_CSB=None,
                bias_limit=15,
                SCHEDULING_ALGORITHM=None,
                SCHEDULING_TYPE="original_sched",
                PB_ALGORITHM="pdiv(ms_log_R, N_s)",
                ABS_ALGORITHM="pdiv(ABS_MUEs, non_ABS_MUEs + ABS_MSUEs)",
                TOPOLOGY=2,
                ALL_TOGETHER=False,
                PRINT=False,
                MAP=False,
                SAVE=False,
                SHOW=False,
                REAL=True,
                DISTRIBUTION="training",
                NAME="test",
                BENCHMARK=False,
                SCENARIO_INPUTS=None,
                DIFFERENCE=False,
                FAIR=False,
                scenario=0,
                iterations=0,
                DIFFICULTY=3):
        """This is the master func which runs all the individual functions
           within the network optimisation class."""

        import experimental.hold_network_info as HNI
        network = HNI.get_network(DISTRIBUTION)

        # Network Values
        self.power_limits = network.power_limits
        self.CSB_limits = [0, bias_limit]
        self.n_macro_cells = network.n_macro_cells
        self.n_small_cells = network.n_small_cells
        self.n_all_cells = network.n_all_cells
        self.macro_cells = network.macro_cells
        self.small_cells = network.small_cells
        self.BS_locations = network.BS_locations
        self.user_locations = []
        self.environmental_encoding = network.environmental_encoding
        self.gains = network.gains
        for i, small in enumerate(self.small_cells):
            if SC_power:
                small['power'] = float(SC_power[i])
            else:
                small['power'] = 23
            if SC_CSB:
                small['bias'] = float(SC_CSB[i])
            else:
                small['bias'] = 0
            small['potential_users'] = []
            small['attached_users'] = []
            small['macro_interactions'] = []
            small['sum_log_R'] = 0
            small['OPT_log_R'] = 0
            small['first_log_R'] = 0
            small['bench_log_R'] = 0
            small['simple_log_R'] = 0
            small['new_log_R'] = 0
            small['average_downlink'] = 0
            small['extended_users'] = []
            small['SINR_frame'] = [[] for _ in range(40)]
            small['sum_SINR'] = [0 for _ in range(40)]
        for i, macro in enumerate(self.macro_cells):
            macro['potential_users'] = []
            macro['attached_users']=[]
            macro['small_interactions'] = []
            macro['sum_log_R'] = 0
            macro['SINR_frame'] = [[] for _ in range(40)]
            macro['sum_SINR'] = [0 for _ in range(40)]
        self.users = network.users
        self.hotspots = network.hotspots
        self.n_users = network.n_users
        self.size = network.size
        # self.perc_signal = network.perc_signal
        self.iterations = network.iterations
        self.scenario = network.scenario
        self.user_scenarios = network.user_scenarios
        self.STRESS_TEST = network.STRESS_TEST
        self.stress_percentage = network.stress_percentage
        self.bandwidth = 20000000.0
        del(network)

        # Options
        if type(SCENARIO_INPUTS) is str:
            self.scenario_inputs = eval(SCENARIO_INPUTS)
        else:
            self.scenario_inputs = SCENARIO_INPUTS
        if self.scenario_inputs:
            self.hotspots = []
        self.PRE_COMPUTE = False
        self.difference = DIFFERENCE
        self.topology = TOPOLOGY
        self.SINR_limit = 10**(-5/10.0)  # -5 dB
        self.SINR_limits = [-5, 23]
        self.NAME = NAME
        self.ALL_TOGETHER = ALL_TOGETHER
        self.PRINT = PRINT
        self.step = 0.01
        self.SCHEDULING = False
        self.MAP = MAP
        self.scheduling_algorithm = SCHEDULING_ALGORITHM
        if self.scheduling_algorithm:
            self.SCHEDULING = True
        self.pb_algorithm = PB_ALGORITHM
        self.ABS_algorithm = ABS_ALGORITHM
        self.ABS_activity = np.asarray([1 for _ in range(self.n_all_cells)])
        self.min_ABS_ratio = 0.875
        # 0 0.125 0.25 0.375 0.5 0.625 0.75 0.875 1
        # A higher number means less frames will be blanked. min ratio of 1
        # means no frames will be blanked as a minimum. A min ratio of 0.125
        # means only one frame remains unblanked.
        self.SINR_interference_limit = 11  # self.n_all_cells
        # number of interfering cells is this -1
        self.DIFFICULTY = DIFFICULTY
        self.show_all_UEs = False

        # Fitness Values
        self.improvement = None
        self.improvement_R = None
        self.improvement_SINR = None
        self.improvement_SINR5 = None
        self.improvement_R_list = []
        self.improvement_SINR_list = []
        self.improvement_SINR5_list = []
        self.improvement_SINR50_list = []
        self.improvement_DL5_list = []
        self.improvement_DL50_list = []
        self.sum_log_R_list = []
        self.SINR_list = []
        self.first_xar = []
        self.first_yar = []
        self.max_downs_list = []
        self.max_perks_list = []
        self.downlink_5_list = []
        self.downlink_50_list = []
        self.SLR_difference_list = []
        self.SLR_difference_list_2 = []
        self.SLR_difference_list_3 = []
        self.SC_dict = {}
        self.ave_improvement_R = None
        self.ave_improvement_SINR = None
        self.ave_improvement_SINR5 = None
        self.ave_improvement_SINR50 = None
        self.ave_improvement_DL5 = None
        self.ave_improvement_DL50 = None
        self.helpless_UEs = []
        self.CDF_log = False
        self.OPT_SCHEDULING = False
        self.SYNCHRONOUS_ABS = True
        self.BENCHMARK = BENCHMARK
        self.BENCHMARK_SCHEDULING = False
        self.BENCHMARK_ABS = False
        self.NEW_SCHEDULING = False
        if self.BENCHMARK:
            self.BENCHMARK_SCHEDULING = True
            self.BENCHMARK_ABS = True
        self.REALISTIC = REAL
        self.FAIR = FAIR
        self.SCHEDULING_TYPE = SCHEDULING_TYPE
        if not self.REALISTIC:
            self.SINR_interference_limit = self.n_all_cells
        if scenario:
            self.SCENARIO = scenario
        if iterations:
            self.iterations = iterations

        # Variables
        self.small_powers = []
        self.small_biases = []
        self.power_bias = []
        self.all_powers = []
        self.seed = 13
        self.cgm = []
        self.MC_UES = []
        self.SC_UES = []
        self.total_unassigned_slots = 1000000
        self.frame = 0
        # Set minimum number of scheduled sub-frames for all UEs at 5 sub-
        # frames out of a full frame of 40 sub-frames. This is because the
        # maximum permissible ABS ratio is 35/40, meaning there will always
        # be a minimum of 5 frames out of 40 with full MC transmission.
        self.SHOW = SHOW
        now = datetime.now()
        hms = "%02d%02d%02d" % (now.hour, now.minute, now.second)
        self.TIME_STAMP = (str(now.year)[2:] + "_" + str(now.month) + "_" + str(now.day) + "_" + hms)
        self.schedule_info = np.zeros(shape=(self.n_all_cells, 40, self.n_users))
        self.schedule_info1 = np.zeros(shape=(40, self.n_users))
        self.noise_W = 10**((-124-30)/10)
        self.SAVE = SAVE
        if self.SAVE:
            self.generate_save_folder()
        if not self.iterations:
            self.iterations = 1
        if platform == 'win32':
            self.slash = "\\"
        else:
            self.slash = "/"

    def run_all(self):
        """run all functions in the class"""

        state = getstate()

        # original seed is 13
        seed(self.seed)
        np.random.seed(self.seed)
        self.time_list = []
        time1 = datetime.now()
        self.time_list.append(time1)

        self.balance_bias()

        if self.difference:
            self.get_normalised_benchmark_difference()
            quit()

        else:

            def go_frame_go(i):
                """ Run the network with a live plot of the CDF of Downlink rates
                """
                self.frame += 1
                one = datetime.now()
                answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)
                two = datetime.now()
                print("Frame",self.frame, "\tTime:", two-one)
               # if self.frame == 25:
               #     self.first_xar = self.CDF_downlink
                self.ax1.clear()

                xar = self.CDF_downlink
                yar = self.actual_frequency
                zar = self.CDF_SINR

                self.ax1.plot(xar, yar, 'b', self.first_xar, yar, 'r')
                self.ax1.set_ylabel('Cumulative distribution')
                self.ax1.set_ylim([0,1])
                self.ax1.set_xlabel('Log of downlink rates (bits/sec)', color='b')

                self.ax2.plot(zar, yar, 'g', self.first_zar, yar, '#ffa500')
                self.ax2.set_xlabel('Log of SINR', color='g')

            """ Run the network continuously here (with live CDF plot). Simply
                un-comment the following five lines.
            """
           # self.fig = plt.figure(figsize=[20,15])
           # self.ax1 = self.fig.add_subplot(1,1,1)
           # self.ax2 = self.ax1.twiny()
           # ani = animation.FuncAnimation(self.fig, go_frame_go)
           # plt.show()

            """ Run the network for a specified number of frames here. Simply
                delete "if None:#".
            """
            for frame in range(self.iterations):
                self.iteration = self.scenario + frame
                self.users = self.user_scenarios[frame]

                # self.reset_to_zero()
                # self.update_network(FIST=True)
                # answers = self.run_full_frame(first=True, two=self.PRINT)

                if self.BENCHMARK:
                    if self.FAIR:
                        self.balance_network()
                    else:
                        self.set_benchmark_pb()
                        self.update_network()
                    answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)

                elif self.ALL_TOGETHER:
                    # If we're evolving everything together then we don't need to
                    # run things separately to get individual fitnesses. We only
                    # need to run the network multiple times in order to get
                    # individual fitnesses for ABS and Scheduling (i.e. the
                    # fitness for scheduling will be the increase in fitness over
                    # ABS, etc.). If we're doing everything together, then we can
                    # just do it all in one step and save a ton of time since we
                    # get the same answer anyway. Good stuff!
                    self.balance_network()
                    answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)

                elif not self.ABS_algorithm and not self.SCHEDULING:
                    # Just the fitness from the pb algorithm
                    self.balance_network()
                    answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)

                elif self.ABS_algorithm and not self.SCHEDULING:
                    # Just the fitness from the ABS algorithm
                    self.balance_network()
                    answers = self.run_full_frame(first=True, two=self.PRINT, three=self.SAVE)
                    self.update_network()
                    answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)

                else:
                    # Just the fitness from the scheduling algorithm
                    self.ALL_TOGETHER = True
                    self.SCHEDULING = False

                    # self.balance_network()

                    self.BENCHMARK_ABS = True
                    self.set_benchmark_pb()
                    self.update_network(FIST=True)

                    answers = self.run_full_frame(first=True, two=self.PRINT, three=self.SAVE)
                    self.SCHEDULING = True
                    self.update_network()
                    answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)
                    self.ALL_TOGETHER = False

                if self.SHOW or self.SAVE:
                    self.save_CDF_plot("Scheduling_"+str(frame), SHOW=self.SHOW, SAVE=self.SAVE)

                if self.MAP:
                    self.save_heatmap("Optimised", SHOW=self.SHOW, SAVE=self.SAVE)

                if answers == 0:
                    # no point checking other scenarios this guy does nothing
                    break

                if self.ALL_TOGETHER and answers < 2:
                    # no point checking other scenarios this guy sucks
                    break

                elif answers < -5:
                    # no point checking other scenarios this guy sucks
                    break

                # self.get_average_performance()

            total_time = self.time_list[-1] - self.time_list[0]
            if self.PRINT:
                print("\nTotal time taken:", total_time)
                process = psutil.Process(getpid())
                print(self.NAME, "Mem:\t", process.memory_info().rss/1024/1024, "Mb\n")
            setstate(state)

            # self.deep_cleanse()
            return answers

    def run_all_2(self):
        """run all functions in the class"""

        state = getstate()

        # original seed is 13
        seed(self.seed)
        np.random.seed(self.seed)
        self.time_list = []
        time1 = datetime.now()
        self.time_list.append(time1)

        # self.balance_bias()

        self.ave_CDF_baseline = []
        self.ave_CDF_optimum = []
        self.ave_CDF_evolved = []
        # self.ave_CDF_simplified = []
        self.ave_CDF_benchmark = []
        self.PRE_COMPUTE = True
        # self.SIMPLIFIED_SCHEDULING = False
        self.weights_dict = {'0.0': [],
                            '0.4': [],
                            '0.8': [],
                            '1.2': [],
                            '1.6': [],
                            '2.0': [],
                            '2.4': [],
                            '2.8': [],
                            '3.2': []}

        self.weights_dict_SLR = {'0.0': [],
                                 '0.4': [],
                                 '0.8': [],
                                 '1.2': [],
                                 '1.6': [],
                                 '2.0': [],
                                 '2.4': [],
                                 '2.8': [],
                                '3.2': []}

        # self.ave_bench_times = []
        # self.ave_evolved_times = []

        if self.difference:
            self.get_normalised_benchmark_difference()
            quit()

        else:

            for frame in range(self.iterations):

                self.BASELINE_SCHEDULING = False
                self.EVOLVED_SCHEDULING = False

                print("-----")
                self.iteration = self.scenario + frame
                print("Iteration", self.iteration)
                self.users = self.user_scenarios[frame]

                self.reset_to_zero()
                # self.set_benchmark_pb()
                # self.update_network()
                # answers = self.run_full_frame(first=True, two=self.PRINT)

                # Get baseline fitness values
                print("Baseline scheduling")
                self.ALL_TOGETHER = True
                self.SCHEDULING = False
                # self.balance_network()
                self.BASELINE_SCHEDULING = True
                self.BENCHMARK_ABS = True
                self.set_benchmark_pb()
                self.update_network()

                answers = self.run_full_frame(first=True, two=self.PRINT, three=self.SAVE)
                OLR = self.sum_log_R
                baseline_CDF = self.CDF_downlink
                self.ave_CDF_baseline += self.CDF_downlink

                # for weight in self.weights_dict:
                #     self.weight = float(weight)
                #
                #     # Calculate hand-coded scheduling
                #     print "Hand-coded scheduling", weight
                self.BASELINE_SCHEDULING = False
                #     self.NEW_SCHEDULING = True
                #     # self.OPT_SCHEDULING = True
                self.SCHEDULING = True
                #     # self.update_network()
                #     answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)
                #     self.NEW_SCHEDULING = False
                #     # self.OPT_SCHEDULING = False
                #     self.weights_dict_SLR[weight] = self.sum_log_R
                #     self.weights_dict[weight] += self.CDF_downlink
                #     # self.ave_CDF_optimum += self.CDF_downlink

                # Run benchmark scheduling
                print("Benchmark scheduling")
                self.BENCHMARK_SCHEDULING = True
                # self.update_network()
                answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)
                self.BENCHMARK_SCHEDULING = False

                b_mark_5 = round(self.DL5/1024/1024, 2)
                b_mark_50 = round(self.DL50/1024/1024, 2)
                BLR = self.sum_log_R
                benchmark_CDF = self.CDF_downlink
                self.ave_CDF_benchmark += self.CDF_downlink

                # Run evolved scheduling
                print("Evolved scheduling")
                self.EVOLVED_SCHEDULING = True
                # self.update_network()
                answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)
                self.ALL_TOGETHER = False
                self.EVOLVED_SCHEDULING = False

                evolved_5 = round(self.DL5/1024/1024, 2)
                evolved_50 = round(self.DL50/1024/1024, 2)
                ELR = self.sum_log_R
                evolved_CDF = self.CDF_downlink
                self.ave_CDF_evolved += self.CDF_downlink

                small_ues = [UE['id'] for UE in self.users if
                             UE['attachment'] == 'small']
                average_downlinks = \
                np.average(self.received_downlinks, axis=0)[small_ues]
                log_average_downlinks = np.log(
                    average_downlinks[average_downlinks > 0])
                log_average_downlinks[log_average_downlinks == -np.inf] = 0
                small_log_R = np.sum(log_average_downlinks)

                print("\nSmall Log R:", small_log_R, "\n")


                # # Run evolved scheduling
                # print "Simplified scheduling"
                # self.SIMPLIFIED_SCHEDULING = True
                # # self.update_network()
                # answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)
                # self.ALL_TOGETHER = False
                # self.SIMPLIFIED_SCHEDULING = False

                # simplified_5 = round(self.DL5/1024/1024, 2)
                # simplified_50 = round(self.DL50/1024/1024, 2)
                # SLR = self.sum_log_R
                # simplified_CDF = self.CDF_downlink
                # self.ave_CDF_simplified.append(np.array(self.CDF_downlink))

                self.diff_5 = self.return_percent(b_mark_5, evolved_5)
                self.diff_50 = self.return_percent(b_mark_50, evolved_50)
                self.diff_SLR = self.return_percent(BLR, ELR)
                self.orig_SLR = self.return_percent(OLR, ELR)
                # self.opt_SLR = self.return_percent(ELR, CLR)
                # self.sim_SLR = self.return_percent(SLR, ELR)

                if self.MAP:
                    self.save_heatmap("Optimised", SHOW=self.SHOW, SAVE=self.SAVE)

                if answers == 0:
                    # no point checking other scenarios this guy does nothing
                    break

                if self.ALL_TOGETHER and answers < 2:
                    # no point checking other scenarios this guy sucks
                    break

                elif answers < -5:
                    # no point checking other scenarios this guy sucks
                    break

                self.get_average_performance()

            # l1, l2 = [], []
            # for i in self.ave_bench_times:
            #     l1.append(i.microseconds/1000000)
            # for i in self.ave_evolved_times:
            #     l2.append(i.microseconds/1000000)

            # print "\nBenchmark application time:", self.average(l1)
            # print "\nEvolved application time:  ", self.average(l2)

            self.ave_CDF_baseline = np.sort(np.array(self.ave_CDF_baseline))
            self.ave_CDF_benchmark = np.sort(np.array(self.ave_CDF_benchmark))
            self.ave_CDF_evolved = np.sort(np.array(self.ave_CDF_evolved))
            self.ave_CDF_optimum = np.sort(np.array(self.ave_CDF_optimum))
            # for weight in self.weights_dict:
            #     self.weights_dict[weight] = np.sort(np.array(self.weights_dict[weight]))

            if self.STRESS_TEST:
                plot_name = str(self.n_small_cells) + " SCs stress CDF"
            else:
                plot_name = str(self.n_small_cells) + " SCs standard CDF"

            if self.SHOW or self.SAVE:

                plots = {"Baseline": self.ave_CDF_baseline,
                         "Evolved": self.ave_CDF_evolved,
                         # "Hand-coded": self.ave_CDF_optimum,
                         "Benchmark": self.ave_CDF_benchmark}
                # for weight in self.weights_dict:
                #     plots['Weight = ' + weight] = self.weights_dict[weight]

                self.save_CDF_whole("CDF comparison", plots,
                                     SHOW=self.SHOW, SAVE=self.SAVE)

                self.save_CDF_bottom(plot_name, plots, SHOW=False,
                                     SAVE=self.SAVE)
                self.save_CDF_top(plot_name, plots, SHOW=False, SAVE=self.SAVE)

            total_time = self.time_list[-1] - self.time_list[0]
            if self.PRINT:
                print(("\nTotal time taken:", total_time))
                process = psutil.Process(getpid())
                print((self.NAME, "Mem:\t", process.memory_info().rss/1024/1024,
                      "Mb\n"))
            setstate(state)

            # self.deep_cleanse()
            return answers

    def pre_compute_scenarios(self):
        """ Pre-compute all SINR data for all training scenarios so that
        evolutionary runs can be done much faster. """

        self.PRE_COMPUTE = False
        self.SCHEDULING = False
        self.seed = 13
        # original seed is 13
        seed(self.seed)
        np.random.seed(self.seed)
        self.time_list = []
        time1 = datetime.now()
        self.time_list.append(time1)

        self.balance_bias()

        PRE_COMPUTED_SCENARIOS = []

        for frame in range(self.iterations):
            self.iteration = self.scenario + frame
            self.users = self.user_scenarios[frame]

            # Use benchmark power/bias and ABS
            self.BENCHMARK_ABS = True
            self.set_benchmark_pb()
            self.update_network(FIST=True)
            answers = self.run_full_frame(first=True, two=self.PRINT, three=self.SAVE)

            # Use evolved power/bias and ABS
            # self.reset_to_zero()
            # self.update_network(FIST=True)
            # answers = self.run_full_frame(first=True, two=self.PRINT)
            # self.ALL_TOGETHER = True
            # self.balance_network()
            # answers = self.run_full_frame(first=True, two=self.PRINT, three=self.SAVE)

            self.PRE_COMPUTE = True
            self.update_network()

            vals = {"first_log_R":self.first_log_R,
                    "first_log_SINR":self.first_log_SINR,
                    "first_SINR5":self.first_SINR5,
                    "first_SINR50":self.first_SINR50,
                    "first_DL5":self.first_DL5,
                    "first_DL50":self.first_DL50,
                    # "first_xar":self.first_xar,
                    # "first_zar":self.first_zar,
                    "users":self.users,
                    "small_cells":[{"attached_users":cell['attached_users'],
                                "average_downlink":cell['average_downlink'],
                                "sum_log_R":cell['sum_log_R']} for cell in
                                self.small_cells],
                    "macro_cells":[{"attached_users":cell['attached_users'],
                                "average_downlink":cell['average_downlink'],
                                "sum_log_R":cell['sum_log_R']} for cell in
                                self.macro_cells],
                    "SINR_SF_UE_est":self.SINR_SF_UE_est,
                    "SINR_SF_UE_act":self.SINR_SF_UE_act,
                    "max_SINR_over_frame":self.max_SINR_over_frame,
                    "min_SINR_over_frame":self.min_SINR_over_frame,
                    "potential_slots":self.potential_slots}

            PRE_COMPUTED_SCENARIOS.append(deepcopy(vals))
            self.ALL_TOGETHER = False
        return PRE_COMPUTED_SCENARIOS

    def return_pre_compute_fitness(self, scheduler, scheduler_type,
        PRE_COMPUTED_SCENARIOS, NAME=None):
        """ Run a full frame of the network using the pre-computed stats """

        self.improvement_R_list = []
        self.improvement_SINR_list = []
        self.improvement_SINR5_list = []
        self.improvement_SINR50_list = []
        self.improvement_DL5_list = []
        self.improvement_DL50_list = []
        self.ave_improvement_R = None
        self.ave_improvement_SINR = None
        self.ave_improvement_SINR5 = None

        for scenario in PRE_COMPUTED_SCENARIOS:
            self.scheduling_algorithm = scheduler
            self.SCHEDULING_TYPE = scheduler_type
            self.PRE_COMPUTE = True
            self.NAME = NAME
            self.SCHEDULING = True

            self.first_log_R = scenario["first_log_R"]
            self.first_log_SINR = scenario["first_log_SINR"]
            self.first_SINR5 = scenario["first_SINR5"]
            self.first_SINR50 = scenario["first_SINR50"]
            self.first_DL5 = scenario["first_DL5"]
            self.first_DL50 = scenario["first_DL50"]

            self.users = scenario["users"]
            self.small_cells = scenario["small_cells"]
            self.macro_cells = scenario["macro_cells"]
            self.SINR_SF_UE_est = scenario["SINR_SF_UE_est"]
            self.SINR_SF_UE_act = scenario["SINR_SF_UE_act"]
            self.max_SINR_over_frame = scenario['max_SINR_over_frame']
            self.min_SINR_over_frame = scenario['min_SINR_over_frame']
            self.potential_slots = deepcopy(scenario["potential_slots"])

            answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)
        return answers

    def save_pre_compute_scenarios(self):
        """ Pre-compute all SINR data for all training scenarios so that
        evolutionary runs can be done much faster. """

        self.PRE_COMPUTE = False
        self.SCHEDULING = False
        self.seed = 13
        # original seed is 13
        seed(self.seed)
        np.random.seed(self.seed)
        self.time_list = []
        time1 = datetime.now()
        self.time_list.append(time1)

        PRE_COMPUTED_SCENARIOS = []

        for frame in range(self.iterations):
            self.iteration = self.scenario + frame
            self.users = self.user_scenarios[frame]

            # Use benchmark power/bias and ABS
            self.BENCHMARK_ABS = True
            self.set_benchmark_pb()
            self.update_network(FIST=True)
            answers = self.run_full_frame(first=True, two=self.PRINT, three=self.SAVE)

            # Use evolved power/bias and ABS
            # self.reset_to_zero()
            # self.update_network(FIST=True)
            # answers = self.run_full_frame(first=True, two=self.PRINT)
            # self.ALL_TOGETHER = True
            # self.balance_network()
            # answers = self.run_full_frame(first=True, two=self.PRINT, three=self.SAVE)

            self.PRE_COMPUTE = True
            self.update_network()

            all_cell_dict = self.compute_cell_requirements()
            small_ues = [UE['id'] for UE in self.users if UE['attachment'] == 'small']
            average_downlinks = np.average(self.received_downlinks, axis=0)[small_ues]
            log_average_downlinks = np.log(average_downlinks[average_downlinks > 0])
            log_average_downlinks[log_average_downlinks == -np.inf] = 0
            small_log_R = np.sum(log_average_downlinks)

            vals = {"first_log_R": small_log_R,
                    "small_cells": [{"attached_users": cell['attached_users'],
                                    "id":cell['id']} for cell in
                                    self.small_cells],
                    "small_users": small_ues,
                    "all_cell_dict": all_cell_dict,
                    "SINR_SF_UE_est": self.SINR_SF_UE_est,
                    "SINR_SF_UE_act": self.SINR_SF_UE_act,
                    "avg_SINR_over_frame": self.avg_SINR_over_frame,
                    "potential_slots": self.potential_slots}

            PRE_COMPUTED_SCENARIOS.append(deepcopy(vals))
            self.ALL_TOGETHER = False
        return PRE_COMPUTED_SCENARIOS

    def run_full_frame(self, first=False, two=False, three=False, lists=True,time=True, check=False):
        """ Run the network for a full frame of 40ms and calculate the
            performance of the network for that frame.
        """

        # Need to figure out a schedule for SC attached UEs. We need to say
        # which UEs will recieve data in which subframes. MC UEs are all
        # scheduled constantly, but this is not the case for SC UEs as ABS
        # subframes will be in effect and some UEs will get better performance
        # only during an ABS subframe. UEs cannot be scheduled if their SINR
        # is less than 1, as this will result in a transmission outage. The
        # only way to save these UEs is to reconfigure the network.
        if self.PRE_COMPUTE:
            self.set_scheduling(FIRST=first)

        self.frame += 1

        # self.schedule_info1 is num_SFs*num_users and stores in cell (x,y)
        # the number of other UEs sharing SF x with UE y
        self.schedule_info1 = np.zeros(shape=(40, self.n_users))

        for macro in self.macro_cells:
            macro['schedule'] = []
            if macro['attached_users']:
                MC_attached_users = macro['attached_users']
                sf_congestion = self.potential_slots[:, MC_attached_users].sum(axis=1)
                self.schedule_info1[:,MC_attached_users] = self.potential_slots[:,MC_attached_users]
                potential = self.potential_slots[:,MC_attached_users]
                potential[potential == 0] = np.nan
                macro['schedule'] = potential * np.array(MC_attached_users)
                self.schedule_info1[:, MC_attached_users] *= pdiv(1,sf_congestion[:, np.newaxis])

        for small in self.small_cells:
            small['schedule'] = []
            if small['attached_users']:
                SC_attached_users = small['attached_users']
                if (not self.SCHEDULING) or first:
                    sf_congestion = self.potential_slots[:, SC_attached_users].sum(axis=1)
                    self.schedule_info1[:,SC_attached_users] = self.potential_slots[:,SC_attached_users]
                    potential = self.potential_slots[:,SC_attached_users]
                else:
                    sf_congestion = self.scheduling_decisions[:, SC_attached_users].sum(axis=1)
                    self.schedule_info1[:,SC_attached_users] = self.scheduling_decisions[:,SC_attached_users]
                    potential = self.scheduling_decisions[:,SC_attached_users]
                # print potential[:8]#potential == np.nan]
                # potential[potential == 0] = np.nan
                small['schedule'] = potential * np.array(SC_attached_users)
                self.schedule_info1[:, SC_attached_users] *= pdiv(1,sf_congestion[:, np.newaxis])

       # self.get_proportional_fairness_downlink()
        self.get_basic_downlink()
        self.get_user_statistics(FIRST=first)
        if check:
            answers = self.calculate_performance(FIRST=False, PRINT=two, SAVE=three, LISTS=lists, TIME=time)
        else:
            answers = self.calculate_performance(FIRST=first, PRINT=two, SAVE=three, LISTS=lists, TIME=time)
        return answers

    def update_network(self, FIST=False):
        """ Sets the user attachment and ABS configurations for a network of
            given powers and biases.
        """

        self.clear_memory()
        self.small_powers = [self.small_cells[j]['power'] for j in range(self.n_small_cells)]
        self.small_biases = [self.small_cells[j]['bias'] for j in range(self.n_small_cells)]
        self.power_bias = [self.small_powers, self.small_biases]
        self.all_powers = [self.macro_cells[0]['power'] for x in range(self.n_macro_cells)] + self.small_powers

        # get the locations of each user and extract only the columns of the
        # gain matrix for the UEs on the map, add the powers to get received
        # signal with pathloss. Also get the strongest MC interferers per SC.
        self.UE_locations_x = [self.users[i]['location'][0] for i in range(self.n_users)]
        self.UE_locations_y = [self.users[i]['location'][1] for i in range(self.n_users)]
        self.SC_locations_x = [self.small_cells[i]['location'][0] for i in range(self.n_small_cells)]
        self.SC_locations_y = [self.small_cells[i]['location'][1] for i in range(self.n_small_cells)]
        self.all_cell_powers = self.gains[:, self.UE_locations_y, self.UE_locations_x] + np.array(self.all_powers)[:, np.newaxis]
        self.all_cell_bias = np.asarray([0 for i in range(self.n_macro_cells)] + self.small_biases)
        self.cell_attachment = self.all_cell_powers + self.all_cell_bias[:, np.newaxis]

        if self.REALISTIC and self.DIFFICULTY == 1:
            # We need to quantize the received channel gains to the nearest 3
            # dBm
            quantized_cgm = self.gains[:, self.UE_locations_y, self.UE_locations_x]
            # Round off gains to nearest 3 dBm
            quantized_cgm = np.around(quantized_cgm/3)*3
            self.cgm = quantized_cgm + np.array(self.all_powers)[:, np.newaxis]

            # Set the lower limit for received powers to -123.4 dBm
            self.cgm[self.cgm <= -123.4] = np.nan

        # Need to find the strongest serving MC for each SC. Dictates ABS
        # ratios for SC attached UEs
        SC_interferers = self.gains[:, self.SC_locations_y,
                 self.SC_locations_x] + np.array(self.all_powers)[:, np.newaxis]
        self.SC_interferers = np.argmax(SC_interferers[:self.n_macro_cells,
                                        :], axis=0)
        del(self.SC_locations_x)
        del(self.SC_locations_y)
        del(self.UE_locations_x)
        del(self.UE_locations_y)
        del(self.all_powers)

        self.set_users()
        self.get_ABS()
        self.set_SINR()
        if not self.PRE_COMPUTE:
            self.set_scheduling(FIRST=FIST)

    def calculate_performance(self, TIME=True, PRINT=True, FIRST=False, LISTS=True, SAVE=False):
        """ Runs all programs to set the users for a given network state. Also
            Gets downlinks for all users."""

        self.DL5 = self.get_downlink_percentile(0.05)
        self.SINR5 = self.get_SINR_percentile(0.05)
        self.DL50 = self.get_downlink_percentile(0.5)
        self.SINR50 = self.get_SINR_percentile(0.5)
        if FIRST:
            #if not self.difference:
            self.first_log_R = self.sum_log_R
            self.first_log_SINR = self.sum_log_SINR
            self.first_SINR5 = self.SINR5
            self.first_SINR50 = self.SINR50
            self.first_DL5 = self.DL5
            self.first_DL50 = self.DL50
            if not self.PRE_COMPUTE:
                self.first_xar = self.CDF_downlink
                self.first_zar = self.CDF_SINR
        else:
            self.improvement_R = self.return_percent(self.first_log_R, self.sum_log_R)
            self.improvement_SINR = self.return_percent(self.first_log_SINR, self.sum_log_SINR)
            self.improvement_SINR5 = self.return_percent(self.first_SINR5, self.SINR5)
            self.improvement_SINR50 = self.return_percent(self.first_SINR50, self.SINR50)
            self.improvement_DL5 = self.return_percent(self.first_DL5, self.DL5)
            self.improvement_DL50 = self.return_percent(self.first_DL50, self.DL50)
            if not LISTS:
                self.ave_improvement_R = None
                self.ave_improvement_SINR = None
                self.ave_improvement_SINR5 = None
                self.ave_improvement_SINR50 = None
                self.ave_improvement_DL5 = None
                self.ave_improvement_DL50 = None
            else:
                self.improvement_R_list.append(self.improvement_R)
                self.improvement_SINR_list.append(self.improvement_SINR)
                self.improvement_SINR5_list.append(self.improvement_SINR5)
                self.improvement_SINR50_list.append(self.improvement_SINR50)
                self.improvement_DL5_list.append(self.improvement_DL5)
                self.improvement_DL50_list.append(self.improvement_DL50)
                self.ave_improvement_R = self.average(self.improvement_R_list)
                self.ave_improvement_SINR = self.average(self.improvement_SINR_list)
                self.ave_improvement_SINR5 = self.average(self.improvement_SINR5_list)
                self.ave_improvement_SINR50 = self.average(self.improvement_SINR50_list)
                self.ave_improvement_DL5 = self.average(self.improvement_DL5_list)
                self.ave_improvement_DL50 = self.average(self.improvement_DL50_list)

        if TIME:
            time = datetime.now()
            self.time_list.append(time)
        opt_time = self.time_list[-1] - self.time_list[-2]
        total_time = self.time_list[-1] - self.time_list[0]

        answers = {"SINR5": self.SINR5, "DL5": self.DL5,
                   "sum_log_R": self.sum_log_R,
                   # "CDF_downlink":self.CDF_downlink,
                   # "first_CDF_downlink":self.first_xar,
                   # "first_CDF_SINR":self.first_zar,
                   "improvement": self.improvement_R,
                   "ave_improvement_R": self.ave_improvement_R,
                   "sum_log_SINR": self.sum_log_SINR,
                   "ave_improvement_SINR": self.ave_improvement_SINR,
                   "ave_improvement_SINR5": self.ave_improvement_SINR5,
                   "ave_improvement_SINR50": self.ave_improvement_SINR50,
                   "ave_improvement_DL5": self.ave_improvement_DL5,
                   "ave_improvement_DL50": self.ave_improvement_DL50,
                   # "frequency":self.actual_frequency,
                   "max_downlink": self.max_downlink,
                   "min_downlink": self.min_downlink,
                   # "power_bias":self.power_bias,
                   # "CDF_SINR":self.CDF_SINR,
                   "difficulty": self.DIFFICULTY,
                   "scheduling type": self.SCHEDULING_TYPE,
                   "no. small cells": self.n_small_cells,
                   "stress percentage": self.stress_percentage,
                   "realistic": self.REALISTIC,
                   "step time": opt_time,
                   "total time": total_time,
                   "unscheduled_UEs": len([UE for UE in self.users if UE['downlink'] == 0]),
                   "helpless_UEs": len([UE for UE in self.users if max(UE['SINR_frame']) <= self.SINR_limit])}

        if PRINT:
            if self.frame:
                print(self.frame, end=' ')
            print("\tMin:", round(self.min_downlink[0], 2), end=' ')
            print(" \tMax:", round(self.max_downlink[0], 2), end=' ')
            print("\t5th %:", round(self.DL5/1024/1024, 2), end=' ')
            print(" \t50th %:", round(self.DL50/1024/1024, 2), end=' ')
            if FIRST:
                print("\tSLR:", round(self.sum_log_R, 2))
            else:
                print("\tSLR:", round(self.sum_log_R, 2), end=' ')
                if self.difference:
                    print("\tImpr:", round(self.improvement_R, 4))
                else:
                    print("\tImpr:", round(self.improvement_R, 4), end=' ')
                    print("   \tAve Impr:", round(self.ave_improvement_R, 4))
            print("\tHelpless:", answers['helpless_UEs'], end=' ')
            print("\tUnscheduled:", answers['unscheduled_UEs'])

        if SAVE:
            filename = "./Network_Stats/" + str(self.TIME_STAMP) + "/Network_Stats.txt"
            savefile = open(filename, 'a')
            savefile.write(str(self.frame))
            savefile.write("\tMin: " + str(round(self.min_downlink[0], 2)))
            savefile.write(" \tMax: " + str(round(self.max_downlink[0], 2)))
            savefile.write("\t5th %:" + str(round(self.DL5/1024/1024, 2)))
            savefile.write(" \t50th %:" + str(round(self.DL50/1024/1024, 2)))
            savefile.write("\tSLR: " + str(round(self.sum_log_R, 2)))
            if not FIRST:
                savefile.write("  \tImpr: " + str(round(self.improvement_R, 2)))
                if not self.difference:
                    savefile.write("  \tAve Impr: " + str(round(self.ave_improvement_R, 4)))
            savefile.write("\tHelpless UEs: " + str(answers['helpless_UEs']))
            savefile.write("\tUnscheduled UEs: " + str(answers['unscheduled_UEs']))
            savefile.write("\n")
            savefile.close()

        return answers["ave_improvement_R"]

    def clear_memory(self):
        """Clears the memory of all cells to allow for changes in cell
           parameters"""
        for macro in self.macro_cells:
            macro['attached_users'] = []
            macro['small_interactions'] = []
            macro['potential_users'] = []
            macro['sum_log_R'] = 0
            macro['SINR_frame'] = [[] for _ in range(40)]
            macro['sum_SINR'] = [0 for _ in range(40)]
            macro['rank_sum'] = 0
            macro['min_rank'] = 9999999999999
            macro['max_rank'] = -9999999999999
            macro['max_SINR'] = [-9999999999999 for _ in range(40)]
            macro['min_SINR'] = [9999999999999 for _ in range(40)]
            macro['percentage_rank_sum'] = 0
            macro['ABS_MSUEs'] = 0
        for i, small in enumerate(self.small_cells):
            small['attached_users'] = []
            small['potential_users'] = []
            small['macro_interactions'] = []
            small['sum_log_R'] = 0
            small['SINR_frame'] = [[] for _ in range(40)]
            small['sum_SINR'] = [0 for _ in range(40)]
            small['rank_sum'] = 0
            small['min_rank'] = 9999999999999
            small['max_rank'] = -9999999999999
            small['max_SINR'] = [-9999999999999 for _ in range(40)]
            small['min_SINR'] = [9999999999999 for _ in range(40)]
            small['percentage_rank_sum'] = 0
        self.helpless_UEs = []
        self.MC_UES = []
        self.SC_UES = []

    def deep_cleanse(self):
        """ Re-sets the powers and biases of SCs so that the optimisation
            algorithm can test its mettle on a fresh network.
        """

        self.users = None
        self.small_cells = None
        self.macro_cells = None
        self.gains = None
        self.BS_locations = None
        self.user_locations = None
        self.environmental_encoding = None
        self.hotspots = None
        self.ABS_activity = None
        self.pb_algorithm = None
        self.ABS_algorithm = None
        self.scheduling_algorithm = None
        self.first_xar = None
        self.first_yar = None
        self.improvement = None
        self.improvement_R = None
        self.improvement_SINR = None
        self.improvement_SINR5 = None
        self.improvement_R_list = []
        self.improvement_SINR_list = []
        self.improvement_SINR5_list = []
        self.improvement_SINR50_list = []
        self.improvement_DL5_list = []
        self.improvement_DL50_list = []
        self.ave_improvement_R = None
        self.ave_improvement_SINR = None
        self.ave_improvement_SINR5 = None
        self.sum_log_R_list = []
        self.SINR_list = []
        self.schedule_info = np.zeros(shape=(self.n_all_cells, 40, self.n_users))
        self.schedule_info1 = np.zeros(shape=(40, self.n_users))

    def random_power_bias(self):
        """ Random powers and biases for all SCs.
        """

        for i, small in enumerate(self.small_cells):
            small['power'] = uniform(self.power_limits[0], self.power_limits[1])
            small['bias'] = uniform(self.CSB_limits[0], self.CSB_limits[1])

    def max_power_bias(self):
        """ Random powers and biases for all SCs.
        """

        for i, small in enumerate(self.small_cells):
            small['power'] = self.power_limits[1]
            small['bias'] = self.CSB_limits[1]

    def max_power_no_bias(self):
        """ Random powers and biases for all SCs.
        """

        for i, small in enumerate(self.small_cells):
            small['power'] = self.power_limits[1]
            small['bias'] = self.CSB_limits[0]

    def set_benchmark_pb(self):
        """ Sets the power and bias of all SCs to static levels for the benchmark.
        """

        # print "Benchmark PB"

        for i, small in enumerate(self.small_cells):
            small['power'] = self.power_limits[1]
            small['bias'] = 7

    def reset_to_zero(self):
        """ Re-sets the powers and biases of SCs to minimum levels so that the
            optimisation algorithm can test its mettle on a fresh network.
        """

        for i, small in enumerate(self.small_cells):
            small['power'] = self.power_limits[0]
            small['bias'] = self.CSB_limits[0]

    def balance_bias(self):
        """Ensures the powers of SCs are maximised before the CSBs are used."""

        for small in self.small_cells:
            if small['power'] < self.power_limits[1]:
                if small['bias'] > 0:
                    remainder = self.power_limits[1] - small['power']
                    balance = remainder - small['bias']
                    if balance >= 0:
                        small['power'] += small['bias']
                        small['bias'] = 0
                    else:
                        small['power'] += remainder
                        small['bias'] -= remainder

    def pdiv(self, a, b):
        """ Protected division operator to prevent division by zero"""

        if type(b) is np.ndarray:
            # Then we have matrix division
            c = deepcopy(b)
            zeros = c == 0
            c[zeros] = 1
            return a/c
        else:
            if b == 0:
                return a
            else:
                return a/b

    def average(self, a):
        """returns the average value of a list"""

        return sum(a)/len(a)

    def std(self, values, ave):
        return sqrt(float(sum((value - ave) ** 2
                                   for value in values)) / len(values))

    def round(self, a, base=4):
        """ Rounds a given number to the nearest specified base.
        """
        return int(base * round(a/base))

    def return_percent(self, original, new):
        """ Returns a number as a percentage change from an original number."""
        if original < 0:
            new -= original
            original = 0
        return -(100 - new/float(original)*100)

    def balance_network(self):
        """Optimise the network for the current distribution of UEs"""

        # print "Evolved PB"

        p_lim_0 = self.power_limits[0]
        b_lim_0 = self.CSB_limits[0]
        total_min = p_lim_0 + b_lim_0
        p_lim_1 = self.power_limits[1]
        b_lim_1 = self.CSB_limits[1]
        total_max = p_lim_1 + b_lim_1

        for small in self.small_cells:
            all_UEs = small['attached_users']
            macro_list = {}
            if all_UEs:
                N_s = len(small['attached_users'])
                R_s_avg = small['average_downlink']
                s_log_R = small['sum_log_R']
              # For each MC sector that the SC overlaps with find the number
              # of UEs that would attach to these MCs if no SC were present.
                for ind in all_UEs:
                    user = self.users[ind]
                    macro = user['macro']
                    if macro in macro_list:
                        macro_list[macro][0] += 1
                        macro_list[macro][1].append(user['downlink'])
                        if user['downlink']:
                            macro_list[macro][2] += log(user['downlink'])
                    else:
                        if user['downlink']:
                            macro_list[macro] = [1,[user['downlink']], log(user['downlink'])]
                        else:
                            macro_list[macro] = [1,[user['downlink']], 0]

                correction = 0

              # Look at each MC that the SC overlaps with and let the most-
              # overlapped-with-MC influence the correction most strongly
                for i in macro_list:
                    N_ms = macro_list[i][0]
                    """
                    number is the number of UEs who have the same macro cell
                    as their governing macro.
                    """
                    macro = self.macro_cells[i]
                    N_m = len(macro['attached_users'])
                    R_ms_avg = self.average(macro_list[i][1])
                    R_m_avg = self.macro_cells[i]['average_downlink']
                    m_log_R = macro['sum_log_R']
                    ms_log_R = macro_list[i][2]

                    correction += eval(self.pb_algorithm)
                total = small['power'] + small['bias']
                if correction > 0:
                    if total < total_max:
                        # Can increase something
                        new_total = total + correction
                        if new_total > total_max:
                            small['power'] = p_lim_1
                            small['bias'] = b_lim_1
                        else:
                            if new_total > p_lim_1:
                                small['power'] = p_lim_1
                                small['bias'] = new_total - p_lim_1
                            else:
                                small['power'] = new_total
                                small['bias'] = b_lim_0
                    else:
                        # Everything is at its limits, can't increase anything
                        pass
                elif correction < 0:
                    if total > total_min:
                        # Can decrease something
                        new_total = total + correction
                        if new_total < total_min:
                            small['power'] = p_lim_0
                            small['bias'] = b_lim_0
                        else:
                            if new_total > p_lim_1:
                                small['power'] = p_lim_1
                                small['bias'] = new_total - p_lim_1
                            else:
                                small['power'] = new_total
                                small['bias'] = b_lim_0
                    else:
                        # Everything is at its limits, can't decrease anything
                        pass
        if not self.ALL_TOGETHER and (self.ABS_algorithm or self.BENCHMARK_ABS):
            self.update_network(FIST=True)
        else:
            self.update_network()

    def set_users(self):
        """Sets parameters for all users"""

        self.SC_attached_UEs = []
        # store the cell IDs and powers from best serving cells (MC and SCs)
        # for each UE

        if self.REALISTIC and self.DIFFICULTY == 1:
            from bottleneck import partsort
            cell_powers_tp = self.cgm.transpose()
            del(self.cgm)
        macro_attachment_id = np.argmax(self.all_cell_powers[:self.n_macro_cells, :], axis=0)
        macro_received_power = self.all_cell_powers[macro_attachment_id, list(range(self.n_users))]
        small_attachment_id = np.argmax(self.cell_attachment[self.n_macro_cells:, :], axis=0)
        small_received_power = self.all_cell_powers[small_attachment_id+self.n_macro_cells, list(range(self.n_users))]

        for i, user in enumerate(self.users):
            # Need to find the top N strongest cells per UE
            if self.REALISTIC and self.DIFFICULTY == 1:
                cell_powers_tp[i][cell_powers_tp[i] < -partsort(-cell_powers_tp[i], self.SINR_interference_limit)[:self.SINR_interference_limit][-1]] = np.nan
            user['attachment'] = 'None'
            user['extended'] = False
            user['SINR_frame'] = [0 for i in range(40)]
            # user['downlink_frame'] = [0 for i in range(40)]
            user['previous_downlink_frame'] = []
            # user['scheduled'] = 0
            # user['proportion'] = [0 for x in range(40)]
            # user['channel_gain_matrix'] = cell_powers_tp[i]
            user_id = user['id']

            # Small cell operations, add best serving SC
            user['small'] = small_attachment_id[user_id]
            user['small_received_power'] = small_received_power[user_id]
            small = self.small_cells[user['small']]
            small['potential_users'].append(user['id'])

            # Macro cell operations, add best serving MC
            user['macro'] = macro_attachment_id[user_id]
            user['macro_received_power'] = macro_received_power[user_id]
            macro = self.macro_cells[user['macro']]
            macro['potential_users'].append(user['id'])

            self.set_user_attachment(user, macro, small)

        if self.REALISTIC and self.DIFFICULTY == 1:
            self.channel_gain_matrix = cell_powers_tp.transpose()
        self.SC_attached_UEs = np.array(self.SC_attached_UEs)

    def set_user_attachment(self, user, macro, small):
        """Set the attachment for a user to the cell which provides the best
           signal strength, but also which includes a sufficient Cell Selection
           Bias."""

        m_down = user['macro_received_power']
        s_down = user['small_received_power']

        if m_down > (s_down + small['bias']):
            user['attachment'] = 'macro'
            self.MC_UES.append(user['id'])
            user['attachment_id'] = macro['id']
            self.SC_attached_UEs.append(False)
            if user['id'] not in macro['attached_users']:
                macro['attached_users'].append(user['id'])
            else:
                print("attempting duplicate MC user")
        else:
            user['attachment'] = 'small'
            self.SC_UES.append(user['id'])
            self.SC_attached_UEs.append(True)
            user['attachment_id'] = self.n_macro_cells + small['id']
            if user['id'] not in small['attached_users']:
                small['attached_users'].append(user['id'])
            else:
                print("attempting duplicate SC user")
            if m_down > s_down:
                small['extended_users'].append(user['id'])
                user['extended'] = True
                macro['ABS_MSUEs'] += 1

    def get_ABS(self):
        """gets the ABS ratio for a MC. Adjusts the downlink rates for MCs and
        SCs to suit."""

        self.cumulatvie_ABS_frames = np.asarray([0 for i in range(40)])

        ABS_MSUEs = np.array([self.macro_cells[j]['ABS_MSUEs'] for j in range(self.n_macro_cells)])
        ABS_MUEs = np.array([len(self.macro_cells[j]['attached_users']) for j in range(self.n_macro_cells)])
        non_ABS_MUEs = ABS_MUEs + ABS_MSUEs
        alpha = 1 # 1/(1-(ABS_MSUEs/non_ABS_MUEs))

        numbers = np.asarray([self.min_ABS_ratio for i in range(self.n_macro_cells)])#ABS_MUEs/(ABS_MUEs + ABS_MSUEs)

        if self.BENCHMARK_ABS:
            # print "Benchmark ABS"
            numbers = (1-alpha)+(alpha*ABS_MSUEs/non_ABS_MUEs)
            numbers = np.round(numbers/0.125)/8
            numbers[numbers >= 1] = self.min_ABS_ratio
            numbers[numbers <= 0] = 0.125
            numbers[np.where(ABS_MUEs == 0)[0]] = 0.125
            numbers = 1 - numbers
        elif self.ABS_algorithm:
            # print "Evolved ABS"
            numbers = eval(self.ABS_algorithm)
            if type(numbers) == float:
                numbers = np.array([numbers for i in range(self.n_macro_cells)])
            numbers = np.round(numbers/0.125)/8
            numbers[numbers >= 1] = self.min_ABS_ratio
            numbers[numbers <= 0] = 0.125
            numbers[np.where(ABS_MUEs == 0)[0]] = 0.125
        else:
            numbers = np.round(numbers/0.125)/8
            numbers[numbers >= 1] = self.min_ABS_ratio
            numbers[numbers <= 0] = 0.125
            numbers[np.where(ABS_MUEs == 0)[0]] = 0.125

        if self.SYNCHRONOUS_ABS:
            new_ratios = int(round(np.average(numbers)*8))/8
            numbers = [new_ratios for _ in range(self.n_macro_cells)]

        for id, macro in enumerate(self.macro_cells):
            macro['ABS_ratio'] = numbers[id]
            macro['ABS_pattern'] = np.array([1 for i in range(40)])
            for i in range(int(round(round((1-macro['ABS_ratio']),3)/0.025))):
                macro['ABS_pattern'][(i*8)%39] = 0
            # print macro['id'], "\t", macro['ABS_ratio'], "\t", macro['ABS_pattern']
            macro['ABS_pattern'] = np.asarray(macro['ABS_pattern'])
            self.cumulatvie_ABS_frames += (-macro['ABS_pattern']+1)

    def get_proportional_fairness_downlink(self):
        """Gets the downlink rates for UEs using Shannon's formula and
           congestion information. Uses proportional fairness to divide
           available bandwidth up amongst scheduled UEs.
           """

        for small in self.small_cells:
            SC_attached_users = small['attached_users']
            schedule = small['schedule'][self.subframe]
            avg_downlink = []
            if schedule:
                sched = []
                for ind in schedule:
                    user = self.users[ind]
                    SINR = user['SINR_frame'][self.subframe]
                    if (self.subframe == 0) and not user['previous_downlink_frame']:
                        # No proportional fairness because we don't know how
                        # everyone will perform yet. Just split the bandwidth
                        # evenly across the spectrum.
                        user['proportion'][self.subframe] = 1
                    else:
                        # We can implement proportional fairness. We want to
                        # find out who needs the most bandwidth, and approtion
                        # it out appropriately.
                        r_1 = float(self.bandwidth)*log((1+SINR), 2)
                        # Instantaneous downlink (no bandwidth split)
                        if user['previous_downlink_frame']:
                            length = 40 + len(user['downlink_frame'][:self.subframe-1])
                            r_2 = (sum(user['previous_downlink_frame']) + sum(user['downlink_frame'][:self.subframe-1])) / length
                            if r_2 == 0:
                                r_2 = 1
                        else:
                            if self.subframe != 0:
                                r_2 = sum(user['downlink_frame'][:self.subframe]) / len(user['downlink_frame'][:self.subframe])
                                if r_2 == 0:
                                    r_2 = 1
                        user['proportion'][self.subframe] = r_1/r_2
                    sched.append(user['proportion'][self.subframe])
                for ind in schedule:
                    user = self.users[ind]
                    SINR = user['SINR_frame'][self.subframe]
                    proportion = user['proportion'][self.subframe]
                    downlink = proportion*(float(self.bandwidth)/sum(sched))*log((1+SINR), 2)
                    user['downlink_frame'][self.subframe] = downlink

        for i, macro in enumerate(self.macro_cells):
            MC_attached_users = macro['attached_users']
            schedule = macro['schedule'][self.subframe]
            avg_downlink = []
            if schedule:
                sched = []
                for ind in schedule:
                    user = self.users[ind]
                    SINR = user['SINR_frame'][self.subframe]
                    if (self.subframe == 0) and not user['previous_downlink_frame']:
                        # No proportional fairness because we don't know how
                        # everyone will perform yet. Just split the bandwidth
                        # evenly across the spectrum.
                        user['proportion'][self.subframe] = 1
                    else:
                        # We can implement proportional fairness. We want to
                        # find out who needs the most bandwidth, and approtion
                        # it out appropriately.
                        r_1 = float(self.bandwidth)*log((1+SINR), 2)
                        # Instantaneous downlink (no bandwidth split)
                        if user['previous_downlink_frame']:
                            length = 40 + len(user['downlink_frame'][:self.subframe-1])
                            r_2 = (sum(user['previous_downlink_frame']) + sum(user['downlink_frame'][:self.subframe-1])) / length
                        else:
                            if self.subframe != 0:
                                r_2 = sum(user['downlink_frame'][:self.subframe]) / len(user['downlink_frame'][:self.subframe])
                                if r_2 == 0:
                                    r_2 = 1
                        user['proportion'][self.subframe] = r_1/r_2
                    sched.append(user['proportion'][self.subframe])
                for ind in schedule:
                    user = self.users[ind]
                    SINR = user['SINR_frame'][self.subframe]
                    if SINR:
                        proportion = user['proportion'][self.subframe]
                        downlink = proportion*(self.bandwidth/sum(sched))*log((1+SINR), 2)
                    user['downlink_frame'][self.subframe] = downlink

        self.received_downlinks = np.zeros(shape=(40, self.n_users))
        for user_id, user in enumerate(self.users):
            self.received_downlinks[:, user_id] = np.array(self.users[user_id]['downlink_frame'])

    def get_basic_downlink(self):
        """ Gets the downlink rates for UEs using Shannon's formula and
            congestion information. Divides the bandwidth equally between UEs.
           """

        # Instantaneous_downlinks is a num_SFs*num_users matrix storing
        # downlinks received by each UE if no congestion and if each UE was
        # always scheduled.
        instantaneous_downlinks = self.bandwidth * np.log2(1+self.SINR_SF_UE_act)

        # Next we take account of the scheduling by dividing the bandwidth by
        # the number sharing each SF.
        self.received_downlinks = instantaneous_downlinks * self.schedule_info1

        # our method yields infinities and nans which are summarily mapped to 0
        self.received_downlinks[np.isnan(self.received_downlinks)] = 0
        self.received_downlinks[self.received_downlinks >= 1E308] = 0

        # for user in range(self.n_users):
        #     self.users[user]['downlink_frame'] = self.received_downlinks[:, user]

    def get_new_downlink(self):
        """ Gets the downlink rates for UEs using Shannon's formula and
            congestion information. Uses a new thing to divide
            available bandwidth up amongst scheduled UEs. The SINR of every UE
            attached to a cell for a particular subframe is analysed. Each UE
            is then given an amount of the available bandwidth which is
            inversly proportional to the SINR of that UE compared to other UEs
            in that subframe. I.e., if there are three UEs with SINR of 5 and
            one with an SINR of 85, then the UE with the better SINR is given
            proportionally less bandwidth than the others. In this case, the
            UE with an SINR of 85 would get 5%  of the available bandwidth,
            whereas the UEs with an SINR of 5 would each get 31.666%  of the
            available bandwidth. The idea is to try to give everyone equal
            downlink rates for a particular subframe.

            This might not necessarily work; initial tests seem to show it
            performing worse than proportional fairness. Maybe we should try to
            assign people bandwidth based on their potential downlink
            throughputs, rather than the proportions based on SINR.

           """

        for small in self.small_cells:
            SC_attached_users = small['attached_users']
            schedule = small['schedule'][self.subframe]
            avg_downlink = []
            if schedule:

                total_SINR = 0
                total_proportion = 0
                for ind in schedule:
                    user = self.users[ind]
                    SINR = user['SINR_frame'][self.subframe]
                    total_SINR += SINR
                for ind in schedule:
                    user = self.users[ind]
                    SINR = user['SINR_frame'][self.subframe]
                    if SINR == total_SINR:
                        proportion = 1
                    else:
                        proportion = 1 - (SINR/total_SINR)
                    total_proportion += proportion
                    user['proportion'][self.subframe] = proportion
                for ind in schedule:
                    user = self.users[ind]
                    SINR = user['SINR_frame'][self.subframe]
                    proportion = user['proportion'][self.subframe]
                    downlink = (proportion/total_proportion)*self.bandwidth*log((1+SINR), 2)
                    user['downlink_frame'][self.subframe] = downlink

        for macro in self.macro_cells:
            MC_attached_users = macro['attached_users']
            schedule = macro['schedule'][self.subframe]
            avg_downlink = []
            if schedule:
                total_SINR = 0
                total_proportion = 0
                for ind in schedule:
                    user = self.users[ind]
                    SINR = user['SINR_frame'][self.subframe]
                    total_SINR += SINR
                for ind in schedule:
                    user = self.users[ind]
                    SINR = user['SINR_frame'][self.subframe]
                    if SINR == total_SINR:
                        proportion = 1
                    else:
                        proportion = 1 - (SINR/total_SINR)
                    total_proportion += proportion
                    user['proportion'][self.subframe] = proportion
                for ind in schedule:
                    user = self.users[ind]
                    SINR = user['SINR_frame'][self.subframe]
                    proportion = user['proportion'][self.subframe]
                    downlink = (proportion/total_proportion)*self.bandwidth*log((1+SINR), 2)
                    user['downlink_frame'][self.subframe] = downlink

    def set_SINR(self):
        """ Set all the SINR values for all UEs in the network for a full frame
        """

        # convert to linear
        # Actual
        signal_W = (10**((self.all_cell_powers-30)/10))
        signal_W[np.isnan(signal_W)] = 0
        del(self.all_cell_powers)

        if self.REALISTIC and self.DIFFICULTY == 1:
            # Estimtated
            cgm_W = 10**((self.channel_gain_matrix-30)/10)
            cgm_W[np.isnan(cgm_W)] = 0
            del(self.channel_gain_matrix)

        # encode the ABS patterns in a num_SFs*num_cells matrix, i.e. each row
        # i indicates which cells mute in SF i
        small_ABS = [1 for n in range(self.n_small_cells)]
        self.ABS_activity = np.array([[[macro['ABS_pattern'][i] for macro in self.macro_cells] + small_ABS] for i in range(40)])[:,0,:]

        # Actual
        # signal_W is a num_cells*num_users matrix until this point, we
        # broadcast it with the ABS information to give a
        # num_SFs*num_cells*num_users matrix. From this we can get the SINRs
        # across all SFs for each UE as follows...
        tiled_signal_W = np.tile(signal_W, (40, 1, 1))

        if self.REALISTIC and self.DIFFICULTY == 1:
            # Estimtated
            # Also have to take the channel gain matrix and apply the same
            # operations in order to map it to the ABS pattern. Channel gain matrix
            # is limited to the top N interfering cells
            full_c_g_m = np.tile(cgm_W, (40, 1, 1))

        indices_zeros = np.where(self.ABS_activity == 0)

        # turn off the muted cells in each SF. Achieved by setting the power
        # received by each UE to 0 from the muted cell
        # Actual
        tiled_signal_W[indices_zeros[0], indices_zeros[1], :] = 0
        if self.REALISTIC and self.DIFFICULTY == 1:
            # Estimtated
            full_c_g_m[indices_zeros[0], indices_zeros[1], :] = 0

        # store the id of the cell each UE attaches to in a num_users vector
        attached_cells = [self.users[i]['attachment_id'] for i in range(self.n_users)]
        # divide the received_powers by (interference + noise) where these are
        # num_SFs*num_users matrices
        received_powers = tiled_signal_W[:, attached_cells, list(range(len(attached_cells)))]
        actual_interference = np.sum(tiled_signal_W, axis=1)
        self.SINR_SF_UE_act = received_powers / ((actual_interference - received_powers) + self.noise_W)

        l1, l2 = self.SINR_limits[0], self.SINR_limits[1]

        if self.REALISTIC:
            # Need to limit ACTUAL SINR values to max 23 db (199.5262315 in
            # linear).
            self.SINR_SF_UE_act = np.clip(self.SINR_SF_UE_act, 0, 10**(l2/10))

        # Calculate CQI data.
        self.CQI = np.zeros(shape=(40, self.n_users))

        for idx, small in enumerate(self.small_cells):
            small['macro'] = self.SC_interferers[idx]
            # Need to find the strongest interfering/serving MC for
            # this SC. The ABS pattern of this MC will determine the
            # reported SINR values of the SC attached UEs.
            small['ABS_pattern'] = self.macro_cells[small['macro']]['ABS_pattern']

        for user in self.users:
            ind = user['id']


            if user['attachment'] == "small":
                small = self.small_cells[user['small']]
                governing_ABS = small['ABS_pattern']
                ABSclass = np.invert(governing_ABS.astype(bool)).astype(int)
                nonABSclass = governing_ABS
                a = self.SINR_SF_UE_act[:, ind] * ABSclass
                b = self.SINR_SF_UE_act[:, ind] * nonABSclass

                ABS_SINR = 10**(np.clip(np.around(10 * np.log10(np.mean(a[np.nonzero(a)]))), l1, l2)/10)
                user['ABS_SINR'] = ABS_SINR
                non_ABS_SINR = 10**(np.clip(np.around(10 * np.log10(np.mean(b[np.nonzero(b)]))), l1, l2)/10)
                user['non_ABS_SINR'] = non_ABS_SINR
                if self.DIFFICULTY == 2:
                    averaged = self.SINR_SF_UE_act[:, ind]
                elif self.DIFFICULTY == 3:
                    averaged = (ABSclass * ABS_SINR) + (nonABSclass * non_ABS_SINR)
            else:
                a = self.SINR_SF_UE_act[:, ind]
                if self.DIFFICULTY == 2:
                    averaged = a
                elif self.DIFFICULTY == 3:
                    macro = self.macro_cells[user['macro']]
                    averaged = np.mean(a[np.nonzero(a)]) * macro['ABS_pattern']

            # Need to convert from linear to logarithmic (db)
            averaged_db = 10 * np.log10(averaged)

            # Need to quantize and clip our logarithmic SINR values
            quantized_db = np.around(averaged_db)
            self.CQI[:, ind] = np.clip(quantized_db, l1, l2)

        if self.REALISTIC:

            # Need to convert back to linear from logarithmic (db)
            self.SINR_SF_UE_est = (10**((self.CQI)/10))
            del(self.CQI)

            if self.DIFFICULTY == 1:
                received_powers_cgm = full_c_g_m[:, attached_cells, list(range(len(attached_cells)))]
                reported_interference = np.sum(full_c_g_m, axis=1)

                # finally we get the SINR for each UE in each SF in a
                # num_SFs*num_users matrix
                self.SINR_SF_UE_est = received_powers_cgm / ((reported_interference - received_powers_cgm) + self.noise_W)

            # Need to limit reported SINR values to max 23 db / (199.5262315 in
            # linear).
            self.SINR_SF_UE_est = np.clip(self.SINR_SF_UE_est, 0, l2)

        else:
            self.SINR_SF_UE_est = self.SINR_SF_UE_act

        # extract statistics for each UE like max SINR etc, we'll need this
        # info when scheduling UEs
        self.max_SINR_over_frame = np.max(self.SINR_SF_UE_est, axis=0)
        self.min_SINR_over_frame = np.min(ma.masked_where(self.SINR_SF_UE_est == 0, self.SINR_SF_UE_est), axis=0).data
        self.avg_SINR_over_frame = np.average(self.SINR_SF_UE_est, axis=0)
        self.potential_slots = self.SINR_SF_UE_est >= self.SINR_limit
        self.good_subframes_over_frame = np.sum(self.potential_slots, axis=0)
        self.helpless_UEs = self.max_SINR_over_frame <= self.SINR_limit

    def set_scheduling(self, FIRST=False):
        """ Compute per-subframe scheduling for each UE in the network """

        scheduling_decisions = np.ones((40, self.n_users), dtype=bool)
        if self.SCHEDULING and not FIRST:
            # this all gives scheduling decisions for MCs too but we just don't
            # use these decisions
            if (self.SCHEDULING_TYPE == "original_sched") and not self.BENCHMARK_SCHEDULING:
                a_max_cell_SINR = np.zeros(shape=(40, self.n_users))
                a_min_cell_SINR = np.zeros(shape=(40, self.n_users))
                num_SC_shared = np.zeros(self.n_users)
                for i, small in enumerate(self.small_cells):
                    if small['attached_users']:
                        SC_attached_users = small['attached_users']
                        num_SC_attached = len(SC_attached_users)

                        for ind in SC_attached_users:
                            num_SC_shared[ind] = num_SC_attached

                        for sf in range(40):
                            temp_sinrs = self.SINR_SF_UE_est[sf, SC_attached_users]

                            if all(temp_sinrs <= self.SINR_limit):
                                a_max_cell_SINR[sf, SC_attached_users] = 0
                                a_min_cell_SINR[sf, SC_attached_users] = 0
                            else:
                                a_max_cell_SINR[sf, SC_attached_users] = np.max(temp_sinrs[temp_sinrs >= self.SINR_limit])
                                a_min_cell_SINR[sf, SC_attached_users] = np.min(temp_sinrs[temp_sinrs >= self.SINR_limit])

            if self.OPT_SCHEDULING:

                if self.REALISTIC:
                    real_network = "/Real"
                else:
                    real_network = "/Genie"
                if self.STRESS_TEST:
                    stress = "/stress"
                else:
                    stress = "/standard"

                path1 = getcwd()+'/scheduling_data'
                path2 = path1+real_network
                path3 = path2+stress
                path4 = path3 +'/'+str(self.n_small_cells)+'SCs'
                paths = [path1, path2, path3, path4]
                for full_path in paths:
                    if not path.exists(full_path):
                        mkdir(full_path)

                if path.exists(path4 + '/all_data'+str(self.iteration)+".mat"):
                    CHECK = False
                else:
                    CHECK = True

                if CHECK:
                    for cell in [i for i in self.small_cells if len(i['attached_users']) > 1]:
                        cell_id = cell['id']
                        print("Calculating optimum for SC", cell_id, "with", end=' ')
                        ids = cell['attached_users']
                        print(len(ids), "attached UEs")
                        num_attached = len(ids)
                        instan_downlinks = np.log2(1+self.SINR_SF_UE_act[:8, ids])
                        SINR = self.SINR_SF_UE_act[:8, ids]
                        schedule = opt.get_schedule(num_attached, instan_downlinks, SINR)
                        scheduling_decisions[:,ids] = schedule
                    data = {'schedules':scheduling_decisions}
                    io.savemat(path4 + '/all_data' + str(self.iteration), data)
                else:
                    print("Loading CMA schedule for iteration", self.iteration)
                    data = io.loadmat(path4 + '/all_data'+str(self.iteration))
                    scheduling_decisions = data['schedules']

            elif self.BENCHMARK_SCHEDULING:
                # benchmark scheduling, Lopez and Claussen (2013)

                # t1 = datetime.now()

                for small in [cell for cell in self.small_cells if
                              len(cell['attached_users']) > 1]:
                    # print "\n\nCell", small['id'], "with", len(small['attached_users']), "attached"

                    attached = small['attached_users']
                    num_attached = len(attached)
                    non_ABS = np.array(small['ABS_pattern'])
                    ABS = np.array([not i for i in non_ABS], dtype=int)
                    num_ABS = np.count_nonzero(ABS[:8])
                    num_non_ABS = 8 - num_ABS

                    ABS_queue = []
                    non_ABS_queue = []

                    def compute_balance(ABS_queue, non_ABS_queue):
                        # Step 4: Calculate estimated throughputs for worst UEs
                        # in each queue

                        ABS_sched = [a for a in ABS_queue if
                                     a[1] > self.SINR_limit]
                        non_ABS_sched = [b for b in non_ABS_queue if
                                     b[2] > self.SINR_limit]

                        if len(ABS_queue) == 0 or len(ABS_sched) == 0:
                            return True

                        elif len(non_ABS_queue) == 0 or len(non_ABS_sched) == 0:
                            return False

                        else:

                            worst_ABS = ABS_sched[0][1]
                            worst_non_ABS = non_ABS_sched[0][2]
                            TP_ABS = (self.bandwidth / len(
                                ABS_sched)) * np.log2(
                                1 + worst_ABS) * num_ABS / 8
                            TP_no_ABS = (self.bandwidth / len(
                                non_ABS_sched)) * np.log2(
                                1 + worst_non_ABS) * num_non_ABS / 8

                            if (TP_no_ABS / TP_ABS) > 1:
                                # non ABS UE is better off, need to offload
                                # from ABS queue
                                return False

                            elif (TP_no_ABS / TP_ABS) < 1:
                                # ABS UE is better off, need to offload from
                                # non ABS queue
                                return True

                            else:
                                return "finished"

                    # Steps 1 & 2:
                    for ue in attached:
                        user = self.users[ue]
                        ABS_SINR = user['ABS_SINR']
                        non_ABS_SINR = user['non_ABS_SINR']
                        if user['extended']:
                            ABS_queue.append([ue, ABS_SINR, non_ABS_SINR])
                        else:
                            non_ABS_queue.append([ue, ABS_SINR, non_ABS_SINR])

                    # print "\tABS:    ", len(ABS_queue)
                    # print "\tnon ABS:", len(non_ABS_queue)

                    # Step 3: Sort each queue with respect to increasing SINR
                    # (i.e.) worst performers earliest in the queue
                    ABS_queue.sort(key=itemgetter(1))
                    non_ABS_queue.sort(key=itemgetter(2))

                    check_1 = False
                    check_2 = True

                    # If either queue is empty, place one UE from the other
                    # queue there
                    if (len(ABS_queue) == 0):
                        mover = non_ABS_queue.pop(0)
                        ABS_queue.append(mover)
                        move_to_ABS = True
                        check_1 = True
                    elif (len(non_ABS_queue) == 0):
                        available = [e for e in ABS_queue if
                                     e[2] > self.SINR_limit]
                        if not available:
                            # Then we can't put anyone into the non ABS queue
                            # Revert to baseline scheduling
                            ABS_queue = [[ue] for ue in attached]
                            non_ABS_queue = [[ue] for ue in attached]
                            check_2 = False
                        else:
                            mover = available[-1]
                            non_ABS_queue.append(mover)
                            ABS_queue.remove(mover)
                            move_to_ABS = False
                            check_1 = True

                    if check_2:
                        ABS_queue.sort(key=itemgetter(1))
                        non_ABS_queue.sort(key=itemgetter(2))

                        # Place any UEs who can only be scheduled in ABS
                        # frames in the ABS queue.
                        need_help = [f for f in non_ABS_queue if
                                     (f[2] <= self.SINR_limit) and (
                                     f[1] > self.SINR_limit)]
                        if need_help:
                            for ue in need_help:
                                ABS_queue.append(ue)
                                non_ABS_queue.remove(ue)
                                move_to_ABS = True
                                check_1 = True

                        ABS_queue.sort(key=itemgetter(1))
                        non_ABS_queue.sort(key=itemgetter(2))

                        # If nobody in the ABS queue can be scheduled, revert
                        # to baseline scheduling
                        if all([g[1] <= self.SINR_limit for g in ABS_queue]):
                            ABS_queue = [[ue] for ue in attached]
                            non_ABS_queue = [[ue] for ue in attached]
                            check_2 = False

                    if check_2:
                        # We need to implement the baseline algorithm

                        # Initial check for direction move...
                        move = compute_balance(ABS_queue, non_ABS_queue)
                        if not check_1:
                            if move:
                                move_to_ABS = True
                            else:
                                move_to_ABS = False

                        # Iterate until one of the stopping conditions is
                        # satisfied then break out of loop
                        while True:

                            if move == "finished":
                                break

                            # Check to make sure neither queue is empty
                            if (len(ABS_queue) == 0):
                                mover = non_ABS_queue.pop(0)
                                ABS_queue.append(mover)
                                if not move_to_ABS:
                                    # We previously removed someone from the
                                    # ABS queue
                                    break
                                move_to_ABS = True

                            elif (len(non_ABS_queue) == 0):
                                available = [h for h in ABS_queue if
                                             h[2] > self.SINR_limit]
                                if not available:
                                    # Then we can't put anyone into the non
                                    # ABS queue; Revert to baseline scheduling
                                    ABS_queue = [[ue] for ue in attached]
                                    non_ABS_queue = [[ue] for ue in attached]
                                    break
                                else:
                                    mover = available[-1]
                                    non_ABS_queue.append(mover)
                                    ABS_queue.remove(mover)
                                    if move_to_ABS:
                                        # We previously placed someone in
                                        # the ABS queue
                                        break
                                    move_to_ABS = False

                            if move:
                                # Need to move from non-ABS to ABS

                                if not move_to_ABS:
                                    # We previously removed someone from the
                                    # ABS queue
                                    break

                                # If there are too many in the non ABS queue,
                                # take the worst (first in the list) and put
                                # them in the ABS queue
                                mover = non_ABS_queue.pop(0)
                                ABS_queue.append(mover)
                                move_to_ABS = True
                            else:
                                # Need to move from ABS to non-ABS

                                if move_to_ABS:
                                    # We previously placed someone in the ABS
                                    # queue
                                    break

                                # If there are too many in the ABS queue, take
                                # the best (last in the list) and put them in
                                # the non-ABS queue, but only if they have an
                                # SINR greater than the lower limit.
                                available = [j for j in ABS_queue if
                                             j[2] > self.SINR_limit]
                                if not available:
                                    # Then we can't put more into the non ABS
                                    # queue
                                    break
                                else:
                                    mover = available[-1]
                                    non_ABS_queue.append(mover)
                                    ABS_queue.remove(mover)
                                move_to_ABS = False

                            ABS_queue.sort(key=itemgetter(1))
                            non_ABS_queue.sort(key=itemgetter(2))

                            move = compute_balance(ABS_queue, non_ABS_queue)

                    schedule = np.zeros(shape=(40, self.n_users))
                    for ue in attached:
                        if ue in [i[0] for i in ABS_queue]:
                            schedule[:, ue] = ABS
                        elif ue in [i[0] for i in non_ABS_queue]:
                            schedule[:, ue] = non_ABS
                        elif ue in [i[0] for i in ABS_queue] and ue in [i[0]
                                                                        for i
                                                                        in
                                                                        non_ABS_queue]:
                            schedule[:, ue] = [1 for i in range(40)]

                    inds_schedule = schedule[:, attached]
                    inds_schedule[self.SINR_SF_UE_est[:,
                                  attached] <= self.SINR_limit] = 0

                    # Check to make sure every UE is scheduled for at least one
                    # SF
                    lookup = np.sum(inds_schedule, axis=0) == 0
                    inds_schedule[:, lookup] = 1

                    inds_schedule[self.SINR_SF_UE_est[:,
                                  attached] <= self.SINR_limit] = 0

                    # Check to make sure someone is scheduled in at least every
                    # SF
                    lookup = np.sum(inds_schedule, axis=1) == 0
                    inds_schedule[lookup, :] = 1

                    scheduling_decisions[:, attached] = inds_schedule

                scheduling_decisions[
                    self.SINR_SF_UE_est <= self.SINR_limit] = False

                # t2 = datetime.now()
                # self.ave_bench_times.append(t2-t1)

            elif None:#self.BENCHMARK_SCHEDULING:
                # benchmark scheduling, Lopez and Claussen (2013)

                # t1 = datetime.now()

                for small in [cell for cell in self.small_cells if len(cell['attached_users']) > 1]:
                    # print "\n\nCell", small['id'], "with", len(small['attached_users']), "attached"

                    attached = small['attached_users']
                    num_attached = len(attached)
                    non_ABS = np.array(small['ABS_pattern'])
                    ABS = np.array([not i for i in non_ABS], dtype=int)
                    num_ABS = np.count_nonzero(ABS[:8])
                    num_non_ABS = 8 - num_ABS

                    ABS_queue = []
                    non_ABS_queue = []

                    def compute_balance_3(ABS_queue, non_ABS_queue):
                        # Step 4: Calculate estimated throughputs for worst UEs
                        # in each queue

                        ABS_sched = [i for _ in ABS_queue if
                                     i[1] > self.SINR_limit]

                        non_ABS_sched = [i for _ in non_ABS_queue if
                                     i[2] > self.SINR_limit]

                        if len(ABS_queue) == 0 or len(ABS_sched) == 0:
                            return True

                        elif len(non_ABS_queue) == 0 or len(non_ABS_sched) == 0:
                            return False

                        else:
                            worst_ABS = ABS_sched[0][1]
                            worst_non_ABS = non_ABS_sched[0][2]
                            TP_ABS = (self.bandwidth / len(
                                ABS_sched)) * np.log2(
                                1 + worst_ABS) * num_ABS / 8
                            TP_no_ABS = (self.bandwidth / len(
                                non_ABS_sched)) * np.log2(
                                1 + worst_non_ABS) * num_non_ABS / 8

                            if (TP_no_ABS / TP_ABS) > 1:
                                # non ABS UE is better off, need to offload
                                # from ABS queue
                                return False

                            elif (TP_no_ABS / TP_ABS) < 1:
                                # ABS UE is better off, need to offload from
                                # non ABS queue
                                return True

                            else:
                                return "finished"

                    # Steps 1 & 2:
                    for ue in attached:
                        user = self.users[ue]
                        ABS_SINR = user['ABS_SINR']
                        non_ABS_SINR = user['non_ABS_SINR']
                        if user['extended'] or non_ABS_SINR <= self.SINR_limit:
                            ABS_queue.append([ue, ABS_SINR, non_ABS_SINR])
                        else:
                            non_ABS_queue.append([ue, ABS_SINR, non_ABS_SINR])

                    # print "\tABS:    ", len(ABS_queue)
                    # print "\tnon ABS:", len(non_ABS_queue)

                    # Step 3: Sort each queue with respect to increasing SINR
                    # (i.e.) worst performers earliest in the queue
                    ABS_queue.sort(key=itemgetter(1))
                    non_ABS_queue.sort(key=itemgetter(2))

                    check_1 = False
                    check_2 = True

                    # If either queue is empty, place one UE from the other
                    # queue there if possible

                    if all([i[1] <= self.SINR_limit for i in ABS_queue]) and all([i[2] <= self.SINR_limit for i in non_ABS_queue]):
                        ABS_queue = [[ue] for ue in attached]
                        non_ABS_queue = [[ue] for ue in attached]
                        check_2 = False

                    elif (len(ABS_queue) == 0) or all(
                            [i[1] <= self.SINR_limit for i in ABS_queue]):
                        mover = non_ABS_queue.pop(0)
                        ABS_queue.append(mover)
                        move_to_ABS = True
                        check_1 = True

                    elif (len(non_ABS_queue) == 0) or all(
                            [i[2] <= self.SINR_limit for i in non_ABS_queue]):
                        available = [i for i in ABS_queue if
                                     i[2] > self.SINR_limit]
                        if not available:
                            ABS_queue = [[ue] for ue in attached]
                            non_ABS_queue = [[ue] for ue in attached]
                            check_2 = False
                        else:
                            mover = available[-1]
                            non_ABS_queue.append(mover)
                            ABS_queue.remove(mover)
                            move_to_ABS = False
                            check_1 = True

                    if check_2:
                        # We need to implement the benchmark algorithm
                        ABS_queue.sort(key=itemgetter(1))
                        non_ABS_queue.sort(key=itemgetter(2))

                        # Initial check for direction move...
                        move = compute_balance_3(ABS_queue, non_ABS_queue)
                        if not check_1:
                            if move:
                                move_to_ABS = True
                            else:
                                move_to_ABS = False

                        # Iterate until one of the stopping conditions is
                        # satisfied then break out of loop
                        while True:

                            if move == "finished":
                                break

                            # Check to make sure neither queue is empty
                            if (len(ABS_queue) == 0):
                                mover = non_ABS_queue.pop(0)
                                ABS_queue.append(mover)
                                if not move_to_ABS:
                                    # We previously removed someone from the
                                    # ABS queue
                                    break
                                move_to_ABS = True

                            elif (len(non_ABS_queue) == 0):
                                available = [i for i in ABS_queue if i[2] > self.SINR_limit]
                                if not available:
                                    # Then we can't put anyone into the non
                                    # ABS queue; Revert to baseline scheduling
                                    ABS_queue = [[ue] for ue in attached]
                                    non_ABS_queue = [[ue] for ue in attached]
                                    break
                                else:
                                    mover = available[-1]
                                    non_ABS_queue.append(mover)
                                    ABS_queue.remove(mover)
                                    if move_to_ABS:
                                        # We previously placed someone in
                                        # the ABS queue
                                        break
                                    move_to_ABS = False

                            if move:
                                # Need to move from non-ABS to ABS

                                if not move_to_ABS:
                                    # We previously removed someone from the
                                    # ABS queue
                                    break

                                # If there are too many in the non ABS queue,
                                # take the worst (first in the list) and put
                                # them in the ABS queue
                                mover = non_ABS_queue.pop(0)
                                ABS_queue.append(mover)
                                move_to_ABS = True

                            else:
                                # Need to move from ABS to non-ABS

                                if move_to_ABS:
                                    # We previously placed someone in the ABS
                                    # queue
                                    break

                                # If there are too many in the ABS queue, take
                                # the best (last in the list) and put them in
                                # the non-ABS queue, but only if they have an
                                # SINR greater than the lower limit.
                                available = [i for i in ABS_queue if i[2] > self.SINR_limit]
                                if not available:
                                    # Then we can't put more into the non ABS
                                    # queue
                                    break
                                else:
                                    mover = available[-1]
                                    non_ABS_queue.append(mover)
                                    ABS_queue.remove(mover)
                                move_to_ABS = False

                            ABS_queue.sort(key=itemgetter(1))
                            non_ABS_queue.sort(key=itemgetter(2))

                            move = compute_balance_3(ABS_queue, non_ABS_queue)

                    schedule = np.zeros(shape=(40, self.n_users))

                    for ue in attached:
                        if ue in [i[0] for i in ABS_queue]:
                            schedule[:, ue] = ABS
                        elif ue in [i[0] for i in non_ABS_queue]:
                            schedule[:, ue] = non_ABS
                        elif ue in [i[0] for i in ABS_queue] and ue in [i[0] for i in non_ABS_queue]:
                            schedule[:, ue] = [1 for i in range(40)]

                    inds_schedule = schedule[:, attached]
                    inds_schedule[self.SINR_SF_UE_est[:, attached] <= self.SINR_limit] = 0

                    # Check to make sure every UE is scheduled for at least one
                    # SF
                    lookup = np.sum(inds_schedule, axis=0) == 0
                    inds_schedule[:, lookup] = 1

                    inds_schedule[self.SINR_SF_UE_est[:, attached] <= self.SINR_limit] = 0

                    # Check to make sure someone is scheduled in at least every
                    # SF
                    lookup = np.sum(inds_schedule, axis=1) == 0
                    inds_schedule[lookup, :] = 1

                    scheduling_decisions[:, attached] = inds_schedule

                scheduling_decisions[self.SINR_SF_UE_est <= self.SINR_limit] = False

                # t2 = datetime.now()
                # self.ave_bench_times.append(t2-t1)

            elif None:#self.NEW_SCHEDULING:
                # New attempt at scheduling which places UEs in either ABS or
                # non-ABS queues so as to maximise a given fitness

                # t1 = datetime.now()

                for small in [cell for cell in self.small_cells if len(cell['attached_users']) > 1]:
                    # print "\n\nCell", small['id'], "with", len(small['attached_users']), "attached"

                    attached = small['attached_users']
                    num_attached = len(attached)
                    non_ABS = np.array(small['ABS_pattern'])
                    ABS = np.array([not i for i in non_ABS], dtype=int)
                    num_ABS = np.count_nonzero(ABS[:8])
                    num_non_ABS = 8 - num_ABS
                    weight = self.weight

                    ABS_queue = []
                    non_ABS_queue = []
                    both_queues = []

                    def calculate_w_SLR(ABS, non_ABS):
                        if not ABS:
                            ABS = [[0, 0, 0]]
                        elif not non_ABS:
                            non_ABS = [[0, 0, 0]]

                        npABS = np.array(ABS)
                        np_noABS = np.array(non_ABS)
                        ABS_1 = npABS[:,1]
                        no_ABS = np_noABS[:,2]

                        ABS_down = (self.bandwidth/len(ABS_1)) * np.log2(1+ABS_1) * num_ABS/8
                        non_ABS_down = (self.bandwidth/len(no_ABS)) * np.log2(1+no_ABS) * num_non_ABS/8

                        ABS_down[npABS[:,1] <= self.SINR_limit] = 0
                        non_ABS_down[np_noABS[:,2] <= self.SINR_limit] = 0

                        log_ABS = np.log(ABS_down[ABS_down > 0])
                        log_non_ABS = np.log(non_ABS_down[non_ABS_down > 0])

                        log_average_downlinks = np.concatenate((log_ABS, log_non_ABS))
                        num_att = len(log_average_downlinks)

                        # weight = 0 will give normal sum_log_R
                        # higher weights increase lower percentile
                        # performance
                        # negative weights increases the performance
                        # of the best performing UEs in the network.

                        return np.sum(np.sort(log_average_downlinks)*np.array(list(reversed(list(range(1,num_att+1)))))**weight)

                    def compute_direction(ABS_q, non_ABS_q):
                        # Step 4: Calculate estimated throughputs for worst UEs
                        # in each queue

                        if len(ABS_q) == 0:
                            return True
                        elif len(non_ABS_q) == 0:
                            return False
                        else:
                            non_ABS_sched = [i for i in non_ABS_q if i[2] > self.SINR_limit]
                            SLR_1 = calculate_w_SLR(ABS_q, non_ABS_sched)

                            # Move one UE and check has it made things better
                            # or worse

                            ABS_new = deepcopy(ABS_q)
                            non_ABS_new = deepcopy(non_ABS_q)

                            mover = non_ABS_new.pop(0)
                            ABS_new.append(mover)

                            SLR_2 = calculate_w_SLR(ABS_new, non_ABS_new)

                            if (SLR_2 / SLR_1) > 1:
                                return True
                            elif (SLR_2 / SLR_1) < 1:
                                return False
                            else:
                                return "finished"

                    # Steps 1 & 2:
                    for ue in attached:
                        user = self.users[ue]
                        ABS_SINR = user['ABS_SINR']
                        non_ABS_SINR = user['non_ABS_SINR']
                        if user['extended']:
                            ABS_queue.append([ue, ABS_SINR, non_ABS_SINR])
                        else:
                            non_ABS_queue.append([ue, ABS_SINR, non_ABS_SINR])

                    # print "\tABS:    ", len(ABS_queue)
                    # print "\tnon ABS:", len(non_ABS_queue)

                    # Step 3: Sort each queue with respect to increasing SINR
                    # (i.e.) worst performers earliest in the queue
                    ABS_queue.sort(key=itemgetter(1))
                    non_ABS_queue.sort(key=itemgetter(2))

                    check_1 = False
                    check_2 = True

                    # If either queue is empty, place one UE from the other
                    # queue there
                    if (len(ABS_queue) == 0):
                        mover = non_ABS_queue.pop(0)
                        ABS_queue.append(mover)
                        move_to_ABS = True
                        check_1 = True

                    elif (len(non_ABS_queue) == 0):
                        available = [i for i in ABS_queue if i[2] > self.SINR_limit]
                        if not available:
                            # Then we can't put anyone into the non ABS queue
                            # Revert to baseline scheduling
                            ABS_queue = [[ue] for ue in attached]
                            non_ABS_queue = [[ue] for ue in attached]
                            check_2 = False
                        else:
                            mover = available[-1]
                            non_ABS_queue.append(mover)
                            ABS_queue.remove(mover)
                            move_to_ABS = False
                            check_1 = True

                    if check_2:
                        ABS_queue.sort(key=itemgetter(1))
                        non_ABS_queue.sort(key=itemgetter(2))

                        # Place any UEs who can only be scheduled in ABS
                        # frames in the ABS queue.
                        need_help = [i for i in non_ABS_queue if (i[2] <= self.SINR_limit) and (i[1] > self.SINR_limit)]
                        if need_help:
                            for ue in need_help:
                                ABS_queue.append(ue)
                                non_ABS_queue.remove(ue)
                                move_to_ABS = True
                                check_1 = True

                        ABS_queue.sort(key=itemgetter(1))
                        non_ABS_queue.sort(key=itemgetter(2))

                        # If nobody in the ABS queue can be scheduled, revert
                        # to baseline scheduling
                        if all([i[1] <= self.SINR_limit for i in ABS_queue]):
                            ABS_queue = [[ue] for ue in attached]
                            non_ABS_queue = [[ue] for ue in attached]
                            check_2 = False

                    if check_2:
                        # We need to implement the baseline algorithm

                        # Initial check for direction move...
                        move = compute_direction(ABS_queue, non_ABS_queue)
                        if not check_1:
                            if move:
                                move_to_ABS = True
                            else:
                                move_to_ABS = False

                        # Iterate until one of the stopping conditions is
                        # satisfied then break out of loop
                        while True:

                            if move == "finished":
                                break

                            # Check to make sure neither queue is empty
                            if (len(ABS_queue) == 0):
                                mover = non_ABS_queue.pop(0)
                                ABS_queue.append(mover)
                                if not move_to_ABS:
                                    # We previously removed someone from the
                                    # ABS queue
                                    break
                                move_to_ABS = True

                            elif (len(non_ABS_queue) == 0):
                                available = [i for i in ABS_queue if i[2] > self.SINR_limit]
                                if not available:
                                    # Then we can't put anyone into the non
                                    # ABS queue; Revert to baseline scheduling
                                    ABS_queue = [[ue] for ue in attached]
                                    non_ABS_queue = [[ue] for ue in attached]
                                    break
                                else:
                                    mover = available[-1]
                                    non_ABS_queue.append(mover)
                                    ABS_queue.remove(mover)
                                    if move_to_ABS:
                                        # We previously placed someone in
                                        # the ABS queue
                                        break
                                    move_to_ABS = False

                            if move:
                                # Need to move from non-ABS to ABS

                                if not move_to_ABS:
                                    # We previously removed someone from the
                                    # ABS queue
                                    break

                                # If there are too many in the non ABS queue,
                                # take the worst (first in the list) and put
                                # them in the ABS queue
                                mover = non_ABS_queue.pop(0)
                                ABS_queue.append(mover)
                                move_to_ABS = True
                            else:
                                # Need to move from ABS to non-ABS

                                if move_to_ABS:
                                    # We previously placed someone in the ABS
                                    # queue
                                    break

                                # If there are too many in the ABS queue, take
                                # the best (last in the list) and put them in
                                # the non-ABS queue, but only if they have an
                                # SINR greater than the lower limit.
                                available = [i for i in ABS_queue if i[2] > self.SINR_limit]
                                if not available:
                                    # Then we can't put more into the non ABS
                                    # queue
                                    break
                                else:
                                    mover = available[-1]
                                    non_ABS_queue.append(mover)
                                    ABS_queue.remove(mover)
                                move_to_ABS = False

                            ABS_queue.sort(key=itemgetter(1))
                            non_ABS_queue.sort(key=itemgetter(2))

                            move = compute_direction(ABS_queue, non_ABS_queue)

                    # print "    ABS UEs:    ", [ue[0] for ue in ABS_queue]
                    # print "    Non ABS UEs:", [ue[0] for ue in non_ABS_queue]


                    schedule = np.zeros(shape=(40, self.n_users))
                    for ue in attached:
                        if ue in [i[0] for i in ABS_queue]:
                            schedule[:,ue] = ABS
                        elif ue in [i[0] for i in non_ABS_queue]:
                            schedule[:,ue] = non_ABS
                        elif ue in [i[0] for i in ABS_queue] and ue in [i[0] for i in non_ABS_queue]:
                            schedule[:,ue] = [1 for i in range(40)]

                    inds_schedule = schedule[:, attached]
                    inds_schedule[self.SINR_SF_UE_est[:,attached] <= self.SINR_limit] = 0

                    # Check to make sure every UE is scheduled for at least one
                    # SF
                    lookup = np.sum(inds_schedule, axis=0) == 0
                    inds_schedule[:, lookup] = 1

                    inds_schedule[self.SINR_SF_UE_est[:,attached] <= self.SINR_limit] = 0

                    # Check to make sure someone is scheduled in at least every
                    # SF
                    lookup = np.sum(inds_schedule, axis=1) == 0
                    inds_schedule[lookup, :] = 1

                    scheduling_decisions[:, attached] = inds_schedule

                scheduling_decisions[self.SINR_SF_UE_est <= self.SINR_limit] = False

                # t2 = datetime.now()
                # self.ave_bench_times.append(t2-t1)

            elif self.NEW_SCHEDULING:
                # New attempt at visuals-based timeframe scheduling by setting
                # the top right hand diagonal corner of the cell's sorted
                # scheduing array to zeros.

                # t1 = datetime.now()

                for small in [cell for cell in self.small_cells if
                              len(cell['attached_users']) > 1]:
                    # print "\n\nCell", small['id'], "with", len(small['attached_users']), "attached"

                    attached = small['attached_users']
                    num_attached = len(attached)
                    non_ABS = np.array(small['ABS_pattern'])
                    ABS = np.array([not i for i in non_ABS], dtype=int)
                    num_ABS = np.count_nonzero(ABS[:8])
                    num_non_ABS = 8 - num_ABS
                    UE_rep_mat = np.zeros(shape=(8, self.n_users))
                    schedules = np.ones(shape=(8, self.n_users))

                    weight = self.weight

                    def calculate_SLR(sched):

                        sched[UE_rep_mat[:, sorted_UEs] <= self.SINR_limit] = 0
                        congestion = np.sum(sched, axis=1)
                        congestion = np.repeat(congestion, num_attached)
                        congestion = np.reshape(congestion, (8, num_attached))
                        rates = self.bandwidth / congestion * UE_inst_mat[:,
                                                              sorted_UEs] * sched
                        rates = np.nan_to_num(rates)
                        avg_rates = np.average(rates, axis=0)
                        SLR = np.sum(np.log(avg_rates))
                        return SLR

                    def calculate_w_SLR(sched):

                        sched[UE_rep_mat[:, sorted_UEs] <= self.SINR_limit] = 0
                        congestion = np.sum(sched, axis=1)
                        congestion = np.repeat(congestion, num_attached)
                        congestion = np.reshape(congestion, (8, num_attached))
                        rates = self.bandwidth / congestion * UE_inst_mat[:,
                                                              sorted_UEs] * sched
                        rates = np.nan_to_num(rates)
                        avg_rates = np.average(rates, axis=0)
                        log_average_downlinks = np.log(avg_rates)

                        num_att = len(avg_rates)
                        return np.sum(
                            np.sort(log_average_downlinks) * np.array(list(
                                reversed(list(range(1, num_att + 1))))) ** weight)

                    # Step 1: Sort SC attached UEs with respect to increasing
                    # SINR (i.e.) worst performers earliest in the queue
                    sorted_UEs_arr = []
                    for ue in attached:
                        user = self.users[ue]
                        ABS_SINR = user['ABS_SINR']
                        non_ABS_SINR = user['non_ABS_SINR']
                        UE_rep_mat[:num_ABS, ue] = ABS_SINR
                        UE_rep_mat[num_ABS:, ue] = non_ABS_SINR
                        sorted_UEs_arr.append([ue, ABS_SINR, non_ABS_SINR,
                                               np.average(
                                                   [ABS_SINR, non_ABS_SINR])])
                    sorted_UEs_arr.sort(key=itemgetter(3))
                    sorted_UEs = list(
                        np.ravel(np.array(sorted_UEs_arr)[:, [0]]))
                    UE_inst_mat = np.log2(1 + UE_rep_mat)
                    schedules[UE_rep_mat <= self.SINR_limit] = 0

                    # Step 2: Calculate fitness of starting point
                    prev_SLR = calculate_w_SLR(schedules[:, sorted_UEs])

                    # Step 3: Iterative loop
                    row = 0
                    UE = 0

                    test_schedules = copy(schedules[:, sorted_UEs])

                    while True:

                        if UE == -num_attached:
                            print("Crap", -UE, num_attached)
                            new_SLR = calculate_w_SLR(test_schedules)
                            for sched in test_schedules:
                                print(list(sched))
                            quit()
                            break
                        else:
                            UE -= 1
                        test_schedules[row][UE:] = 0
                        new_SLR = calculate_w_SLR(test_schedules)
                        if new_SLR < prev_SLR:
                            UE += 1
                            test_schedules[row][:UE] = 1
                            if row == 6:
                                break
                            else:
                                row += 1
                            UE = -1
                            test_schedules[row][UE] = 0
                            new_SLR = calculate_w_SLR(test_schedules)
                            if new_SLR < prev_SLR:
                                test_schedules[row][UE] = 1
                                break
                            else:
                                prev_SLR = new_SLR
                        else:
                            prev_SLR = new_SLR

                    # quit()

                    inds_schedule = np.vstack((test_schedules, test_schedules,
                                               test_schedules, test_schedules,
                                               test_schedules))
                    inds_schedule[self.SINR_SF_UE_est[:,
                                  sorted_UEs] <= self.SINR_limit] = 0

                    # Check to make sure every UE is scheduled for at least one
                    # SF
                    lookup = np.sum(inds_schedule, axis=0) == 0
                    inds_schedule[:, lookup] = 1

                    inds_schedule[self.SINR_SF_UE_est[:,
                                  sorted_UEs] <= self.SINR_limit] = 0

                    # Check to make sure someone is scheduled in at least every
                    # SF
                    lookup = np.sum(inds_schedule, axis=1) == 0
                    inds_schedule[lookup, :] = 1

                    scheduling_decisions[:, sorted_UEs] = inds_schedule

                scheduling_decisions[
                    self.SINR_SF_UE_est <= self.SINR_limit] = False

                # t2 = datetime.now()
                # self.ave_bench_times.append(t2-t1)

            elif None:#self.NEW_SCHEDULING:
                # New attempt at visuals-based timeframe scheduling by moving crosshairs

                # t1 = datetime.now()

                for small in [cell for cell in self.small_cells if
                              len(cell['attached_users']) > 1]:
                    # print "\n\nCell", small['id'], "with", len(
                    #     small['attached_users']), "attached"

                    attached = small['attached_users']
                    num_attached = len(attached)
                    non_ABS = np.array(small['ABS_pattern'])
                    ABS = np.array([not i for i in non_ABS], dtype=int)
                    num_ABS = np.count_nonzero(ABS[:8])
                    num_non_ABS = 8 - num_ABS
                    UE_rep_mat = np.zeros(shape=(8, self.n_users))
                    schedules = np.ones(shape=(8, self.n_users))

                    weight = self.weight

                    def calculate_SLR(sched):

                        congestion = np.sum(sched, axis=1)
                        congestion = np.repeat(congestion, num_attached)
                        congestion = np.reshape(congestion, (8, num_attached))
                        rates = self.bandwidth / congestion * UE_inst_mat[:,
                                                              sorted_UEs] * sched
                        rates = np.nan_to_num(rates)
                        avg_rates = np.average(rates, axis=0)
                        SLR = np.sum(np.log(avg_rates))
                        return SLR

                    def calculate_w_SLR(sched):

                        congestion = np.sum(sched, axis=1)
                        congestion = np.repeat(congestion, num_attached)
                        congestion = np.reshape(congestion, (8, num_attached))
                        rates = self.bandwidth / congestion * UE_inst_mat[:,
                                                              sorted_UEs] * sched
                        rates = np.nan_to_num(rates)
                        avg_rates = np.average(rates, axis=0)
                        log_average_downlinks = np.log(avg_rates)
                        num_att = len(avg_rates)
                        return np.sum(
                            np.sort(log_average_downlinks) * np.array(list(
                                reversed(list(range(1, num_att + 1))))) ** weight)

                    def compute_direction(ROWS, COLS):

                        orig = calculate_w_SLR(get_sched(ROWS, COLS))
                        COLS -= 1
                        new = calculate_w_SLR(get_sched(ROWS, COLS))
                        if new > orig:
                            return True
                        else:
                            return False

                    def get_sched(ROW, COL):
                        """Returns a scheduling matrix for a SC given ROWS and COLS."""

                        sched = np.ones(shape=(8, num_attached))
                        sched[:ROW][:, COL:] = 0
                        sched[:ROW][:, :COL] = 1
                        sched[ROW:][:, :COL] = 0
                        sched[ROW:][:, COL:] = 1
                        sched[UE_rep_mat[:, sorted_UEs] <= self.SINR_limit] = 0
                        return sched

                    # Step 1: Sort SC attached UEs with respect to increasing
                    # SINR (i.e.) worst performers earliest in the queue
                    sorted_UEs_arr = []
                    for ue in attached:
                        user = self.users[ue]
                        ABS_SINR = user['ABS_SINR']
                        non_ABS_SINR = user['non_ABS_SINR']
                        UE_rep_mat[:num_ABS, ue] = ABS_SINR
                        UE_rep_mat[num_ABS:, ue] = non_ABS_SINR
                        sorted_UEs_arr.append([ue, ABS_SINR, non_ABS_SINR,
                                               np.average(
                                                   [ABS_SINR, non_ABS_SINR])])
                    sorted_UEs_arr.sort(key=itemgetter(3))
                    sorted_UEs = list(
                        np.ravel(np.array(sorted_UEs_arr)[:, [0]]))
                    UE_inst_mat = np.log2(1 + UE_rep_mat)
                    schedules[UE_rep_mat <= self.SINR_limit] = 0

                    # Step 2: Calculate the minimum number of protected UEs
                    min_protected = num_attached - np.count_nonzero(
                        schedules[:, sorted_UEs][-1])
                    max_attack_x = num_attached - min_protected

                    # Step 3: Calculate Initial Guess
                    test_schedules = copy(schedules[:, sorted_UEs])
                    max_UEs = UE_rep_mat[:, sorted_UEs][0]

                    def optimise_COLS(ROW):
                        """Optimise number of UEs (COLS) for a given subframe
                        (ROWS)."""

                        # Start with the best UEs in the best subframes
                        COL = -max(len([i for i in max_UEs if i == max(list(max_UEs))]), 1)
                        cut = compute_direction(ROW, COL)
                        previous_cut = cut

                        # print "Cols:        ", COL
                        # print "Proposed cut:", previous_cut

                        while True:

                            # print "Cols:        ", COL
                            # print "Proposed cut:", cut
                            # print "Previous cut:", previous_cut
                            # print "\n"

                            if cut:
                                if not previous_cut:
                                    break
                                previous_cut = True
                            else:
                                if previous_cut:
                                    break
                                previous_cut = False

                            if previous_cut:
                                if COL == -num_attached:
                                    break
                                COL -= 1
                            else:
                                if COL == -1:
                                    break
                                COL += 1

                            cut = compute_direction(ROW, COL)
                        return ROW, COL

                    ROW, COL = optimise_COLS(num_ABS)

                    def optimise_ROWS(ROW, COL):
                        prev = calculate_w_SLR(get_sched(ROW, COL))
                        while True:
                            if ROW == 7:
                                break
                            ROW += 1
                            ROW, COL = optimise_COLS(ROW)
                            new = calculate_w_SLR(get_sched(ROW, COL))
                            if new < prev:
                                ROW -= 1
                                break
                            else:
                                prev = new
                        return ROW, COL

                    ROW, COL = optimise_ROWS(ROW, COL)

                    test_schedules = get_sched(ROW, COL)

                    # print "    COLS:       ", COL
                    # print "    ABS UEs:    ", list(np.array(sorted_UEs[:COL]).astype(int))
                    # print "    non ABS UEs:", list(np.array(sorted_UEs[COL:]).astype(int))

                    # quit()

                    inds_schedule = np.vstack((test_schedules, test_schedules,
                                               test_schedules, test_schedules,
                                               test_schedules))
                    inds_schedule[self.SINR_SF_UE_est[:,
                                  sorted_UEs] <= self.SINR_limit] = 0

                    # Check to make sure every UE is scheduled for at least one
                    # SF
                    lookup = np.sum(inds_schedule, axis=0) == 0
                    inds_schedule[:, lookup] = 1

                    inds_schedule[self.SINR_SF_UE_est[:,
                                  sorted_UEs] <= self.SINR_limit] = 0

                    # Check to make sure someone is scheduled in at least every
                    # SF
                    lookup = np.sum(inds_schedule, axis=1) == 0
                    inds_schedule[lookup, :] = 1

                    scheduling_decisions[:, sorted_UEs] = inds_schedule

                scheduling_decisions[
                    self.SINR_SF_UE_est <= self.SINR_limit] = False

                # t2 = datetime.now()
                # self.ave_bench_times.append(t2-t1)

            else:
                if self.SCHEDULING_TYPE == "original_sched":
                    min_SINR = np.array([self.min_SINR_over_frame, ]*40)
                    max_SINR = np.array([self.max_SINR_over_frame, ]*40)
                    num_shared = np.array([num_SC_shared, ]*40)
                    good_slots = np.array([self.good_subframes_over_frame, ]*40)
                    SINR = self.SINR_SF_UE_est
                    max_cell_SINR = a_max_cell_SINR
                    min_cell_SINR = a_min_cell_SINR
                    scheduling_decisions = eval(self.scheduling_algorithm)

                elif self.SCHEDULING_TYPE == "genetic_alg":
                    scheduling_decisions = self.genetic_alg()

                else:
                    # t1 = datetime.now()
                    scheduling_decisions = self.compute_scheduling()

                    # t2 = datetime.now()
                    # self.ave_evolved_times.append(t2-t1)

                if type(scheduling_decisions) is bool or type(scheduling_decisions) is np.bool_:
                    if scheduling_decisions:
                        scheduling_decisions = np.ones(shape=(40,self.n_users), dtype=bool)
                    else:
                        scheduling_decisions = np.zeros(shape=(40, self.n_users), dtype=bool)

        scheduling_decisions[self.SINR_SF_UE_est <= self.SINR_limit] = False

        if self.REALISTIC:
            # Need to model dropped data transmissions due to actual
            # SINR <= self.SINR_limit

            check = np.logical_and((self.SINR_SF_UE_act <= self.SINR_limit), scheduling_decisions)
            available = np.logical_and(self.potential_slots, np.logical_not(scheduling_decisions))
            unavailable = self.SINR_SF_UE_act <= self.SINR_limit

            copied_dropped = deepcopy(check)
            for sf, lookup in enumerate(copied_dropped):
                if any(lookup):
                    available_copy = deepcopy(available)
                    boolean = np.zeros((40, self.n_users))
                    # Only operate on those UEs who have dropped calls
                    boolean[min((sf+4), 39):] = lookup
                    # Find free permissible slots in which these UEs can be
                    # rescheduled (that we know of)
                    slots = np.logical_and(available_copy, boolean)
                    if np.any(slots):
                        # Find array indices of available slots
                        indices = np.array(np.where(slots)).transpose().tolist()
                        # Sort the indices by UE
                        indices.sort(key=itemgetter(1))
                        # Get UE ids
                        troubled_UEs = np.where(lookup)[0]
                        # Find which UEs CAN be rescheduled
                        lucky_UEs = list(set([i[1] for i in indices if i[1] in troubled_UEs]))
                        for user in lucky_UEs:
                            new_slot = [list(i) for i in indices if i[1]==user][0]
                            available[new_slot[0]][new_slot[1]] = False
                            if self.SINR_SF_UE_act[new_slot[0]][new_slot[1]] >= self.SINR_limit:
                                # print "Subframe", sf, "rescheduled for UE", user, "in subframe", new_slot[0]
                                # Reschedule the UE in their new slot
                                scheduling_decisions[new_slot[0]][new_slot[1]] = True
                            else:
                                # The slot we had thought was ok is actually
                                # not. The call will be dropped again.
                                copied_dropped[new_slot[0]][new_slot[1]] = True
                                # print "Subframe", sf, "falsely rescheduled for UE", user, "in subframe", new_slot[0]

            scheduling_decisions[self.SINR_SF_UE_act <= self.SINR_limit] = False
            self.potential_slots[self.SINR_SF_UE_act <= self.SINR_limit] = False
        self.scheduling_decisions = scheduling_decisions

        if self.SAVE:
            name = None
            if self.BASELINE_SCHEDULING:
                name = "Baseline"
            elif self.BENCHMARK_SCHEDULING:
                name = "Benchmark"
            elif self.OPT_SCHEDULING:
                name = "GA"
            elif self.NEW_SCHEDULING:
                name = "New_" + "_".join(str(self.weight).split("."))
            elif self.EVOLVED_SCHEDULING:
                name = "Evolved"
            if name:
                for small in [cell for cell in self.small_cells if len(cell['attached_users']) == 10]:
                    unsorted_ids = np.array(small['attached_users'])
                    ids = unsorted_ids[np.argsort(self.avg_SINR_over_frame[unsorted_ids])]
                    schedule = self.scheduling_decisions[:,ids]
                    dic = {'schedule': schedule[:8,]}
                    io.savemat(getcwd()+'/Network_Stats/'+str(self.TIME_STAMP)+"/Heatmaps/input/" + name + "_" + str(self.iteration) + "_" + str(cell['id']), dic)

        for user in self.users:
            ue_id = user['id']
            user['SINR_frame'] = self.SINR_SF_UE_act[:, ue_id]
            user['max_SINR'] = self.max_SINR_over_frame[ue_id]
            user['min_SINR'] = self.min_SINR_over_frame[ue_id]

    def compute_scheduling(self):
        """ Compute the SC scheduling for a given scenario."""

        # def pdiv(a, b):
        #     """ Protected division operator to prevent division by zero"""
        #     if type(b) is np.ndarray:
        #         # Then we have matrix division
        #         zeros = b == 0
        #         den = deepcopy(b)
        #         den[zeros] = 1
        #         return a/den
        #     else:
        #         if b == 0:
        #             return a
        #         else:
        #             return a/b

        scheduling_decisions = np.ones(shape=(40,self.n_users), dtype=bool)
        try:
            compile(self.scheduling_algorithm, '<string>', 'eval')
        except MemoryError:
            return scheduling_decisions

        try:
            check = eval(self.scheduling_algorithm)
        except:
            check = None

        if check == None:

            for small in [cell for cell in self.small_cells if len(cell['attached_users']) > 1]:

                # sweep the tree in an order respecting UE average SINR across their full frames
                unsorted_ids = np.array(small['attached_users'])
                attached_ids = unsorted_ids[np.argsort(self.avg_SINR_over_frame[unsorted_ids])]
                ids = attached_ids

                # get all the required statistics
                mat_SINR = self.SINR_SF_UE_est[:8, ids]

                ones = np.ones(shape=mat_SINR.shape)
                num_attached = mat_SINR.shape[1]
                mat_num_shared = ones * num_attached
                mat_good_subframes = ones * (mat_SINR > self.SINR_limit).sum(0)[None, :]

                mat_least_congested_downlinks = np.log2(1+mat_SINR)

                mat_avg_down_F = ones * np.average(mat_least_congested_downlinks, axis=0)[None, :]
                mat_min_down_F = ones * np.min(mat_least_congested_downlinks, axis=0)[None, :]
                mat_max_down_F = ones * np.max(mat_least_congested_downlinks, axis=0)[None, :]
                mat_LPT_down_F = ones * np.percentile(mat_least_congested_downlinks, 25, axis=0)[None, :]
                mat_UPT_down_F = ones * np.percentile(mat_least_congested_downlinks, 75, axis=0)[None, :]

                mat_avg_down_SF = ones * np.average(mat_least_congested_downlinks, axis=1)[:, None]
                mat_min_down_SF = ones * np.min(mat_least_congested_downlinks, axis=1)[:, None]
                mat_max_down_SF = ones * np.max(mat_least_congested_downlinks, axis=1)[:, None]
                mat_LPT_down_SF = ones * np.percentile(mat_least_congested_downlinks, 25, axis=1)[:, None]
                mat_UPT_down_SF = ones * np.percentile(mat_least_congested_downlinks, 75, axis=1)[:, None]

                mat_avg_down_cell = ones * np.average(mat_least_congested_downlinks)
                mat_min_down_cell = ones * np.min(mat_least_congested_downlinks)
                mat_max_down_cell = ones * np.max(mat_least_congested_downlinks)
                mat_LPT_down_cell = ones * np.percentile(mat_least_congested_downlinks, 25)
                mat_UPT_down_cell = ones * np.percentile(mat_least_congested_downlinks, 75)

                ues = np.array(list(range(num_attached)))
                ue_ids = np.tile(ues, (8, 1))

                sfs = np.array(list(range(8)))
                sf_ids = np.tile(sfs, (num_attached, 1)).T

                dropped_calls = deepcopy(mat_SINR)
                dropped_calls[dropped_calls <= self.SINR_limit] = -1.0
                dropped_calls[dropped_calls > self.SINR_limit] = 1.0

                T1 = mat_num_shared
                T2 = mat_good_subframes

                T3 = mat_least_congested_downlinks

                T4 = mat_avg_down_F
                T5 = mat_min_down_F
                T6 = mat_max_down_F
                T7 = mat_LPT_down_F
                T8 = mat_UPT_down_F

                T9 = mat_avg_down_SF
                T10 = mat_min_down_SF
                T11 = mat_max_down_SF
                T12 = mat_LPT_down_SF
                T13 = mat_UPT_down_SF

                T14 = mat_avg_down_cell
                T15 = mat_min_down_cell
                T16 = mat_max_down_cell
                T17 = mat_LPT_down_cell
                T18 = mat_UPT_down_cell

                T19 = ue_ids
                T20 = sf_ids
                T21 = dropped_calls

                ABS = np.array([not i for i in small['ABS_pattern'][:8]], dtype=int)
                ABS = np.tile(ABS, (num_attached, 1)).T
                ABS[ABS==0] = -1

                # print np.sqrt(T9)

                schedule = eval(self.scheduling_algorithm)

                if self.SCHEDULING_TYPE.split("_")[-1] == "threshold":
                    schedule[schedule >= 0] = 1
                    schedule[schedule < 0] = 0

                elif self.SCHEDULING_TYPE.split("_")[-1] == "topology":
                    top = eval(str(self.topology))
                    rows = ((-schedule).argsort(axis=0)[:top, :]).reshape(top*num_attached)
                    cols = list(range(num_attached))*top
                    schedule[:, :] = 0
                    schedule[rows, cols] = 1

                schedule[mat_SINR <= self.SINR_limit] = 0

                lookup = np.sum(schedule, axis=0) == 0
                schedule[:, lookup] = 1

                schedule[mat_SINR <= self.SINR_limit] = 0

                lookup = np.sum(schedule, axis=1) == 0
                schedule[lookup, :] = 1

                schedule = np.vstack((schedule, schedule, schedule, schedule, schedule))
                scheduling_decisions[:, ids] = schedule.astype(bool)
                small['schedule'] = schedule

        # quit()

        return scheduling_decisions

    def compute_cell_requirements(self):
        """ Prepare all necessary info for pre-computing the network."""

        all_cell_dict = {}

        for small in [cell for cell in self.small_cells if len(cell['attached_users']) > 1]:

            # sweep the tree in an order respecting UE average SINR across their full frames
            unsorted_ids = np.array(small['attached_users'])
            attached_ids = unsorted_ids[np.argsort(self.avg_SINR_over_frame[unsorted_ids])]
            ids = attached_ids

            # get all the required statistics
            mat_SINR = self.SINR_SF_UE_est[:8, ids]

            ones = np.ones(shape=mat_SINR.shape)
            num_attached = mat_SINR.shape[1]
            mat_num_shared = ones * num_attached
            mat_good_subframes = ones * (mat_SINR > self.SINR_limit).sum(0)[None, :]

            mat_least_congested_downlinks = np.log2(1+mat_SINR)

            mat_avg_down_F = ones * np.average(mat_least_congested_downlinks, axis=0)[None, :]
            mat_min_down_F = ones * np.min(mat_least_congested_downlinks, axis=0)[None, :]
            mat_max_down_F = ones * np.max(mat_least_congested_downlinks, axis=0)[None, :]
            mat_LPT_down_F = ones * np.percentile(mat_least_congested_downlinks, 25, axis=0)[None, :]
            mat_UPT_down_F = ones * np.percentile(mat_least_congested_downlinks, 75, axis=0)[None, :]

            mat_avg_down_SF = ones * np.average(mat_least_congested_downlinks, axis=1)[:, None]
            mat_min_down_SF = ones * np.min(mat_least_congested_downlinks, axis=1)[:, None]
            mat_max_down_SF = ones * np.max(mat_least_congested_downlinks, axis=1)[:, None]
            mat_LPT_down_SF = ones * np.percentile(mat_least_congested_downlinks, 25, axis=1)[:, None]
            mat_UPT_down_SF = ones * np.percentile(mat_least_congested_downlinks, 75, axis=1)[:, None]

            mat_avg_down_cell = ones * np.average(mat_least_congested_downlinks)
            mat_min_down_cell = ones * np.min(mat_least_congested_downlinks)
            mat_max_down_cell = ones * np.max(mat_least_congested_downlinks)
            mat_LPT_down_cell = ones * np.percentile(mat_least_congested_downlinks, 25)
            mat_UPT_down_cell = ones * np.percentile(mat_least_congested_downlinks, 75)

            ues = np.array(list(range(num_attached)))
            ue_ids = np.tile(ues, (8, 1))

            sfs = np.array(list(range(8)))
            sf_ids = np.tile(sfs, (num_attached, 1)).T

            dropped_calls = deepcopy(mat_SINR)
            dropped_calls[dropped_calls <= self.SINR_limit] = -1.0
            dropped_calls[dropped_calls > self.SINR_limit] = 1.0

            T1 = mat_num_shared
            T2 = mat_good_subframes

            T3 = mat_least_congested_downlinks

            T4 = mat_avg_down_F
            T5 = mat_min_down_F
            T6 = mat_max_down_F
            T7 = mat_LPT_down_F
            T8 = mat_UPT_down_F

            T9 = mat_avg_down_SF
            T10 = mat_min_down_SF
            T11 = mat_max_down_SF
            T12 = mat_LPT_down_SF
            T13 = mat_UPT_down_SF

            T14 = mat_avg_down_cell
            T15 = mat_min_down_cell
            T16 = mat_max_down_cell
            T17 = mat_LPT_down_cell
            T18 = mat_UPT_down_cell

            T19 = ue_ids
            T20 = sf_ids
            T21 = dropped_calls

            ABS = np.array([not i for i in small['ABS_pattern'][:8]],
                           dtype=int)
            ABS = np.tile(ABS, (num_attached, 1)).T
            ABS[ABS == 0] = -1

            cell_dict = {"T1":T1, "T2":T2, "T3":T3, "T4":T4, "T5":T5, "T6":T6,
                         "T7":T7, "T8":T8, "T9":T9, "T10":T10, "T11":T11,
                         "T12":T12, "T13":T13, "T14":T14, "T15":T15, "T16":T16,
                         "T17":T17, "T18":T18, "T19":T19, "T20":T20, "T21":T21,
                         "ABS":ABS}

            all_cell_dict[str(small['id'])] = cell_dict

        return all_cell_dict

    def genetic_alg(self):
        scheduling_decisions = np.ones(shape=(40, self.n_users))
        for i in range(self.n_small_cells):
            small = self.small_cells[i]
            num_attached = len(small['attached_users'])
            all_SC_data={}
            if self.REALISTIC:
                real_network = "/Real"
            else:
                real_network = "/Genie"

            path1 = getcwd()+'/scheduling_data'
            path2 = path1+real_network
            path3 = path2+'/top'+str(self.topology)
            path4 = path3 +'/'+str(self.n_small_cells)+'SCs'
            path5 = path4+'/SC'+str(i)
            paths = [path1, path2, path3, path4, path5]
            for full_path in paths:
                if not path.exists(full_path):
                    mkdir(full_path)

            if path.exists(path5 + '/all_data'+str(self.iteration)+".mat"):
                GA_CHECK = False
            else:
                GA_CHECK = True

            if num_attached > 2:
                all_SC_data['num_attached'] = num_attached

                unsorted_ids = np.array(small['attached_users'])
                attached_ids = unsorted_ids[np.argsort(-self.avg_SINR_over_frame[unsorted_ids])]
                ids = attached_ids

                mat_SINR = self.SINR_SF_UE_est[:8, ids]

                ones = np.ones(shape=mat_SINR.shape)
                num_attached = mat_SINR.shape[1]
                mat_num_shared = ones * num_attached
                mat_good_subframes = ones * (mat_SINR > 1).sum(0)[None, :]

                mat_least_congested_downlinks = np.log2(1+mat_SINR)
                mat_half_congested_downlinks = np.log2(1+mat_SINR) / int(num_attached*0.5)
                mat_fully_congested_downlinks = np.log2(1+mat_SINR) / (num_attached)

                mat_avg_down_F = ones * np.average(mat_least_congested_downlinks, axis=0)[None, :]
                mat_min_down_F = ones * np.min(mat_least_congested_downlinks, axis=0)[None, :]
                mat_max_down_F = ones * np.max(mat_least_congested_downlinks, axis=0)[None, :]
                mat_LPT_down_F = ones * np.percentile(mat_least_congested_downlinks, 25, axis=0)[None, :]
                mat_UPT_down_F = ones * np.percentile(mat_least_congested_downlinks, 75, axis=0)[None, :]

                mat_avg_down_SF = ones * np.average(mat_least_congested_downlinks, axis=1)[:, None]
                mat_min_down_SF = ones * np.min(mat_least_congested_downlinks, axis=1)[:, None]
                mat_max_down_SF = ones * np.max(mat_least_congested_downlinks, axis=1)[:, None]
                mat_LPT_down_SF = ones * np.percentile(mat_least_congested_downlinks, 25, axis=1)[:, None]
                mat_UPT_down_SF = ones * np.percentile(mat_least_congested_downlinks, 75, axis=1)[:, None]

                mat_avg_down_cell = ones * np.average(mat_least_congested_downlinks)
                mat_min_down_cell = ones * np.min(mat_least_congested_downlinks)
                mat_max_down_cell = ones * np.max(mat_least_congested_downlinks)
                mat_LPT_down_cell = ones * np.percentile(mat_least_congested_downlinks, 25)
                mat_UPT_down_cell = ones * np.percentile(mat_least_congested_downlinks, 75)

                if GA_CHECK:
                    schedules = opt.get_schedule(num_attached,
                                                 mat_least_congested_downlinks,
                                                 mat_SINR, self.topology, i)

                    all_SC_data['mat_SINR'] = mat_SINR
                    all_SC_data['mat_num_shared'] = mat_num_shared
                    all_SC_data['mat_good_subframes'] = mat_good_subframes
                    all_SC_data['mat_least_congested_downlinks'] = mat_least_congested_downlinks
                    all_SC_data['mat_half_congested_downlinks'] = mat_half_congested_downlinks
                    all_SC_data['mat_fully_congested_downlinks'] = mat_fully_congested_downlinks

                    all_SC_data['mat_avg_down_F'] = mat_avg_down_F
                    all_SC_data['mat_min_down_F'] = mat_min_down_F
                    all_SC_data['mat_max_down_F'] = mat_max_down_F
                    all_SC_data['mat_LPT_down_F'] = mat_LPT_down_F
                    all_SC_data['mat_UPT_down_F'] = mat_UPT_down_F

                    all_SC_data['mat_avg_down_SF'] = mat_avg_down_SF
                    all_SC_data['mat_min_down_SF'] = mat_min_down_SF
                    all_SC_data['mat_max_down_SF'] = mat_max_down_SF
                    all_SC_data['mat_LPT_down_SF'] = mat_LPT_down_SF
                    all_SC_data['mat_UPT_down_SF'] = mat_UPT_down_SF

                    all_SC_data['mat_avg_down_cell'] = mat_avg_down_cell
                    all_SC_data['mat_min_down_cell'] = mat_min_down_cell
                    all_SC_data['mat_max_down_cell'] = mat_max_down_cell
                    all_SC_data['mat_LPT_down_cell'] = mat_LPT_down_cell
                    all_SC_data['mat_UPT_down_cell'] = mat_UPT_down_cell
                    all_SC_data['schedules'] = schedules

                else:
                    data = io.loadmat(path5 + '/all_data'+str(self.iteration))
                    schedules = data['schedules']

                schedules = np.vstack((schedules, schedules, schedules, schedules, schedules))
                schedules[schedules > 0.0] = True
                schedules[schedules <= 0.0] = False
                scheduling_decisions[:, ids] = schedules.astype(bool)
            else:
                all_SC_data['num_attached'] = 2
                mat_SINR = np.array([[10, 10], [8, 8], [7, 7], [4, 4], [4, 4], [4, 4], [4, 4], [4, 4]])

                if GA_CHECK:
                    ones = np.ones(shape=mat_SINR.shape)
                    num_attached = mat_SINR.shape[1]
                    mat_num_shared = ones * num_attached
                    mat_good_subframes = ones * (mat_SINR > 1).sum(0)[None, :]

                    mat_least_congested_downlinks = np.log2(1+mat_SINR)
                    mat_half_congested_downlinks = np.log2(1+mat_SINR) / int(num_attached*0.5)
                    mat_fully_congested_downlinks = np.log2(1+mat_SINR) / (num_attached)

                    mat_avg_down_F = ones * np.average(mat_least_congested_downlinks, axis=0)[None, :]
                    mat_min_down_F = ones * np.min(mat_least_congested_downlinks, axis=0)[None, :]
                    mat_max_down_F = ones * np.max(mat_least_congested_downlinks, axis=0)[None, :]
                    mat_LPT_down_F = ones * np.percentile(mat_least_congested_downlinks, 25, axis=0)[None, :]
                    mat_UPT_down_F = ones * np.percentile(mat_least_congested_downlinks, 75, axis=0)[None, :]

                    mat_avg_down_SF = ones * np.average(mat_least_congested_downlinks, axis=1)[:, None]
                    mat_min_down_SF = ones * np.min(mat_least_congested_downlinks, axis=1)[:, None]
                    mat_max_down_SF = ones * np.max(mat_least_congested_downlinks, axis=1)[:, None]
                    mat_LPT_down_SF = ones * np.percentile(mat_least_congested_downlinks, 25, axis=1)[:, None]
                    mat_UPT_down_SF = ones * np.percentile(mat_least_congested_downlinks, 75, axis=1)[:, None]

                    mat_avg_down_cell = ones * np.average(mat_least_congested_downlinks)
                    mat_min_down_cell = ones * np.min(mat_least_congested_downlinks)
                    mat_max_down_cell = ones * np.max(mat_least_congested_downlinks)
                    mat_LPT_down_cell = ones * np.percentile(mat_least_congested_downlinks, 25)
                    mat_UPT_down_cell = ones * np.percentile(mat_least_congested_downlinks, 75)

                    schedules = opt.get_schedule(num_attached,
                                                 mat_least_congested_downlinks,
                                                 mat_SINR, self.topology, i)

                    all_SC_data['mat_SINR'] = mat_SINR
                    all_SC_data['mat_num_shared'] = mat_num_shared
                    all_SC_data['mat_good_subframes'] = mat_good_subframes
                    all_SC_data['mat_least_congested_downlinks'] = mat_least_congested_downlinks
                    all_SC_data['mat_half_congested_downlinks'] = mat_half_congested_downlinks
                    all_SC_data['mat_fully_congested_downlinks'] = mat_fully_congested_downlinks

                    all_SC_data['mat_avg_down_F'] = mat_avg_down_F
                    all_SC_data['mat_min_down_F'] = mat_min_down_F
                    all_SC_data['mat_max_down_F'] = mat_max_down_F
                    all_SC_data['mat_LPT_down_F'] = mat_LPT_down_F
                    all_SC_data['mat_UPT_down_F'] = mat_UPT_down_F

                    all_SC_data['mat_avg_down_SF'] = mat_avg_down_SF
                    all_SC_data['mat_min_down_SF'] = mat_min_down_SF
                    all_SC_data['mat_max_down_SF'] = mat_max_down_SF
                    all_SC_data['mat_LPT_down_SF'] = mat_LPT_down_SF
                    all_SC_data['mat_UPT_down_SF'] = mat_UPT_down_SF

                    all_SC_data['mat_avg_down_cell'] = mat_avg_down_cell
                    all_SC_data['mat_min_down_cell'] = mat_min_down_cell
                    all_SC_data['mat_max_down_cell'] = mat_max_down_cell
                    all_SC_data['mat_LPT_down_cell'] = mat_LPT_down_cell
                    all_SC_data['mat_UPT_down_cell'] = mat_UPT_down_cell
                    all_SC_data['schedules'] = schedules

            if GA_CHECK:
                io.savemat(path5 + '/all_data' + str(self.iteration), all_SC_data)
        return scheduling_decisions

    def get_downlink_percentile(self, percentile):
        """Get the total downlink rate for all users in a network. Return
           downlink based on the required input percentile."""

        """Step 1: Order all users by downlink value, from lowest to highest"""
        all_users = []
        for user in self.users:
            if user['downlink']:
                all_users.append([user['id'], user['downlink']])
        all_users.sort(key=itemgetter(1))

        """Step 2: Multiply percentile by total number of users"""
        index = percentile * self.n_users
        if index < 1:
            index = 1

        """step 3: Check if index is an integer. If not, then return the
           average of two values, if so then return the index value."""
        if int(index) != index: # means it's not an integer
            one = int(floor(index))
            two = int(ceil(index))
            percentile_down_1 = all_users[one]
            percentile_down_2 = all_users[two]
            downlink_percentiles = mean([percentile_down_1[1], percentile_down_2[1]])
        else:
            downlink_percentiles = all_users[int(index)][1]

        return downlink_percentiles

    def get_SINR_percentile(self, percentile):
        """Get the total SINR for all users in a network. Return SINR
           based on the required input percentile."""

        """Step 1: Order all users by SINR value, from lowest to highest"""
        all_users = []
        for user in self.users:
            all_users.append([user['id'], user['average_SINR']])
        all_users.sort(key=itemgetter(1))

        """Step 2: Multiply percentile by total number of users"""
        index = percentile * self.n_users
        if index < 1:
            index = 1

        """step 3: Check if index is an integer. If not, then return the
           average of two values, if so then return the index value."""
        if int(index) != index: # means it's not an integer
            one = int(floor(index))
            two = int(ceil(index))
            percentile_SINR_1 = all_users[one]
            percentile_SINR_2 = all_users[two]
            total_SINR = mean([percentile_SINR_1[1], percentile_SINR_2[1]])
        else:
            total_SINR = all_users[int(index)][1]

        return total_SINR

    def get_user_statistics(self, FIRST=False):
        """ Get the measurement statistics for all UEs in the network:
                Average downlink rate of each UE
                Average SINR of each UE
                Peak downlink rate of the overall network
                Minimum downlink rate of the overall network
                CDF of both downlink and SINR (based on average values)
        """

        average_downlinks = np.average(self.received_downlinks, axis=0)
        average_SINRs = np.average(self.SINR_SF_UE_act, axis=0, weights=self.SINR_SF_UE_act.astype(bool))
        self.average_SINRs = average_SINRs

        log_average_downlinks = np.log(average_downlinks[average_downlinks > 0])
        log_average_downlinks[log_average_downlinks == -np.inf] = 0

        log_average_SINRs = np.log(average_SINRs)
        log_average_SINRs[log_average_SINRs == -np.inf] = 0

        if self.CDF_log:
            self.CDF_downlink = (log_average_downlinks).tolist()
            self.CDF_downlink.extend([0 for i in average_downlinks[average_downlinks == 0]])
        else:
            self.CDF_downlink = (average_downlinks/1024/1024).tolist()

        if self.CDF_log:
            self.CDF_SINR = (log_average_SINRs).tolist()
        else:
            self.CDF_SINR = (average_SINRs).tolist()

        self.sum_log_SINR = np.sum(log_average_SINRs)
        self.sum_log_R = np.sum(log_average_downlinks)

        self.max_downlink = [np.max(average_downlinks)/1024/1024, np.argmax(average_downlinks)]
        self.min_downlink = [np.min(average_downlinks[average_downlinks > 0])/1024/1024, np.argmax(average_downlinks[average_downlinks > 0])]

        if self.BENCHMARK_SCHEDULING:
            self.benchmark_downlinks = average_downlinks
        elif not FIRST:
            self.evolved_downlinks = average_downlinks

        for user_id, user in enumerate(self.users):
            user['downlink'] = average_downlinks[user_id]
            user['average_SINR'] = average_SINRs[user_id]
            # if not self.PRE_COMPUTE:
            #     if len(user['previous_downlink_frame']) < 5*40:
            #         # Only track statistics for a 1/5th of second
            #         user['previous_downlink_frame'] += (self.received_downlinks[:, user_id]).tolist()
            #     else:
            #         user['previous_downlink_frame'] += (self.received_downlinks[:, user_id]).tolist()
            #         remove_indices = len(user['previous_downlink_frame'])
            #         del user['previous_downlink_frame'][remove_indices-40:remove_indices]

        for cell_id in range(self.n_all_cells):
            if cell_id < self.n_macro_cells:
                cell = self.macro_cells[cell_id]
                attached_users = cell['attached_users']
            else:
                cell = self.small_cells[cell_id-self.n_macro_cells]
                attached_users = cell['attached_users']
            attached_ue_ids = attached_users
            if len(attached_ue_ids) > 0:
                cell['average_downlink'] = np.average(average_downlinks[attached_ue_ids])
                available_down = average_downlinks[attached_ue_ids]
                cell_log_ave_down = np.log(available_down[available_down > 0])
                cell_log_ave_down[cell_log_ave_down == -np.inf] = 0
                cell['sum_log_R'] = np.sum(cell_log_ave_down)
            else:
                cell['average_downlink'] = 0
                cell['sum_log_R'] = 0
            if FIRST:
                cell['first_log_R'] = copy(cell['sum_log_R'])
            if self.BENCHMARK_SCHEDULING:
                cell['bench_log_R'] = copy(cell['sum_log_R'])
            if self.OPT_SCHEDULING:
                cell['OPT_log_R'] = copy(cell['sum_log_R'])
            if self.NEW_SCHEDULING:
                cell['new_log_R'] = copy(cell['sum_log_R'])
            # if self.SIMPLIFIED_SCHEDULING:
            #     cell['simple_log_R'] = copy(cell['sum_log_R'])

        self.CDF_downlink.sort()
        self.CDF_downlink = np.asarray(self.CDF_downlink)
        self.CDF_downlink[self.CDF_downlink == 0] = None
        self.CDF_downlink = self.CDF_downlink[self.SC_attached_UEs]
        self.CDF_downlink = self.CDF_downlink.tolist()
        self.CDF_SINR.sort()

    """
    ---------------------------------------------------------------------------
    Rarely used functions
    """

    def get_average_performance(self, OUTPUT=False):
        """ Look at all SCs in the network and see how performance varies
            across cells of differing sizes."""

        if OUTPUT:
            print("---------")

        SC_UEs = [user['id'] for user in self.users if user['attachment'] == "small"]

        downlink_difference = (self.evolved_downlinks - self.benchmark_downlinks)/1024/1024
        perks = [self.return_percent(orig, new) for orig, new in zip(self.evolved_downlinks[SC_UEs], self.benchmark_downlinks[SC_UEs])]
        downs = downlink_difference[SC_UEs]
        SINRs = self.average_SINRs[SC_UEs]
        eSINRs = np.average(self.SINR_SF_UE_est, axis=0, weights=self.SINR_SF_UE_est.astype(bool))

        self.max_downs_list.append(max(downs))
        self.max_perks_list.append(max(perks))
        self.downlink_5_list.append(self.diff_5)
        self.downlink_50_list.append(self.diff_50)
        self.SLR_difference_list.append(self.diff_SLR)
        self.SLR_difference_list_2.append(self.orig_SLR)
        # self.SLR_difference_list_3.append(self.opt_SLR)

        print("Average max downlink improvement over benchmark:  ", np.average(self.max_downs_list))
        print("Average max percentage improvement over benchmark:", np.average(self.max_perks_list))

        print("Average 5th percentile improvement:", np.average(self.downlink_5_list))
        print("Average 50th percentile improvement:", np.average(self.downlink_50_list))

        print("Average Sum(Log(R)) improvement over baseline:", np.average(self.SLR_difference_list_2))
        print("Average Sum(Log(R)) improvement over benchmark:", np.average(self.SLR_difference_list))
        # print "Average Sum(Log(R)) distance to CMA optimum:", np.average(self.SLR_difference_list_3)

        # if OUTPUT:
        #     paired_list = zip(downs, SINRs)
        #     paired_list.sort(key=itemgetter(1))
        #     fig, axes = plt.subplots(figsize=[15,10])
        #     axes.plot([x for x, y in paired_list], color='r')
        #     axes.axhline(color="k")
        #     axes.set_xlabel("Increase in SINR")
        #     axes.set_ylabel("Downlink improvement (Mbps)")
        #     plt.show()
        #     plt.close()

        for cell in self.small_cells:
            orig = cell['first_log_R']
            new = cell['sum_log_R']
            bench = cell['bench_log_R']
            # opt_r = cell['OPT_log_R']
            new_r = cell['new_log_R']
            perc = 0
            b_perc = 0
            # opt_perc = 0
            new_perc = 0
            if orig:
                perc = self.return_percent(orig, new)
                b_perc = self.return_percent(orig, bench)
                # opt_perc = self.return_percent(orig, opt_r)
                new_perc = self.return_percent(orig, new_r)

            if len(cell['attached_users']) in self.SC_dict:
                self.SC_dict[len(cell['attached_users'])].append([b_perc, perc, new_perc])
            else:
                self.SC_dict[len(cell['attached_users'])] = [[b_perc, perc, new_perc]]

        if OUTPUT:

            keys = []
            b_mark = []
            b_mark_std = []
            evolved = []
            evolved_std = []
            # optimum = []
            # optimum_std = []
            # new_log_R = []

            bench_perf_imp = []

            for entry in self.SC_dict:
                keys.append(entry)

                b = np.average([i[0] for i in self.SC_dict[entry]])
                b_std = np.std([i[0] for i in self.SC_dict[entry]])
                b_mark.append(b)
                b_mark_std.append(b_std)

                e = np.average([i[1] for i in self.SC_dict[entry]])
                e_std = np.std([i[1] for i in self.SC_dict[entry]])
                evolved.append(e)
                evolved_std.append(e_std)

                # c = np.average([i[2] for i in self.SC_dict[entry]])
                # c_std = np.std([i[2] for i in self.SC_dict[entry]])
                # optimum.append(c)
                # optimum_std.append(c_std)

                # n = np.average([i[3] for i in self.SC_dict[entry]])
                # new_log_R.append(n)

                bench_imp = -self.return_percent(e, b)

                if bench_imp > 0:
                    bench_perf_imp.append(bench_imp)

                print(("%d\t%d\tB_mark: %.2f  \tEvolved: %.2f \tB-E Diff: %.2f" % (entry, len(self.SC_dict[entry]), b, e, bench_imp)))

            evolved = np.asarray(evolved)
            e_std = np.asarray(evolved_std)
            b_mark = np.asarray(b_mark)
            b_std = np.asarray(b_mark_std)
            # optimum = np.asarray(optimum)
            # optimum_std = np.asarray(optimum_std)
            # new_log_R = np.asarray(new_log_R)

            bench_perf_imp = np.asarray(bench_perf_imp)

            lens = [len(entry) for entry in list(self.SC_dict.values())]
            benz = []
            for entry in self.SC_dict:
                # print entry, len(self.SC_dict[entry])
                benz.extend([entry for i in range(len(self.SC_dict[entry]))])

            ave_lens = np.average(benz)
            std_lens = np.std(benz)
            print("\nAverage SC size:", ave_lens)
            print("Standard deviation of SC size:", std_lens, "\n")

            print("Average cell SLR improvement over baseline:\t", np.average(b_mark))
            print("Average benchmark improvement over baseline:\t", np.average(evolved))
            # print "Average cell SLR distance to GA optimum:   \t", np.average(optimum)

            print("\nAverage increase in performance over benchmark (over baseline):", np.average(bench_perf_imp))

            print("\n")

            fig = plt.figure()#figsize=[15,10])
            ax1 = fig.add_subplot(1, 1, 1)

            # ax1.plot(keys, lens, "b")
            # ax1.set_ylabel("Frequency of occurrence of cell of size x")
            # ax1.set_xlabel("Number of UEs per cell")

            ax2 = ax1.twinx()

            ln1 = ax1.plot(keys, evolved, "r", label="Evolved performance improvement")
            # ax1.fill_between(keys, evolved-e_std, evolved+e_std, color="DodgerBlue", alpha=0.5)
            ln2 = ax1.plot(keys, b_mark, "g", label="Benchmark performance improvement")
            # ln4 = ax1.plot(keys, optimum, "k", label="GA-derived performance")
            # ln4 = ax1.plot(keys, new_log_R, "k", label="New algorithm performance")
            # ax1.fill_between(keys, b_mark-b_std, b_mark+b_std, color="palegreen", alpha=0.5)
            ax1.axhline(color="k")
            ax1.set_xlabel("Number of UEs per cell")
            ax1.set_ylabel("Percentage SLR improvement over baseline", color="r")

            ln3 = ax2.plot(keys, lens, "b", label="Frequency of occurrence")
            ax2.set_ylabel("Frequency of occurrence of cell of size x", color="b")
            box = ax1.get_position()

            ax1.set_position([box.x0, box.y0 + box.height * 0.025, box.width, box.height * 0.9])
            ax2.set_position([box.x0, box.y0 + box.height * 0.025, box.width, box.height * 0.9])

            # lns = ln1+ln2+ln3+ln4
            lns = ln1+ln2+ln3
            labs = [l.get_label() for l in lns]
            # ax1.legend(lns, labs, loc="best")
            # ax1.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=3)
            ax1.legend(lns, labs, bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
            # plt.tight_layout()

            if self.SAVE:
                plt.savefig(
                    getcwd() + '/Network_Stats/' + str(self.TIME_STAMP) +
                    '/generalization.pdf', bbox_inches='tight')
            if self.SHOW:
                plt.show()
            if self.SHOW or self.SAVE:
                plt.close()

    def get_benchmark_difference(self):
        """ Find the difference in performance between the given method and
            the benchmark method. Return the difference as a percentage."""

        self.ALL_TOGETHER = True
        self.SYNCHRONOUS_ABS = False
        self.save_scheduling_algorithm = deepcopy(self.scheduling_algorithm)
        self.save_ABS_algorithm = deepcopy(self.ABS_algorithm)
        self.save_scheduling_type = deepcopy(self.SCHEDULING_TYPE)

        baseline_fitness = []
        benchmark_fitness = []
        evolved_fitness = []

        if self.SAVE:
            self.generate_save_folder()

        # Step 1: Get benchmark performance
        for frame in range(self.iterations):
            self.iteration = self.scenario + frame
            # How many full frames of 40 subframes do we want to run?
            # 25 Full frames = 1 second

            self.users = self.user_scenarios[frame]

            # Set Baseline
            if self.PRINT:
                print("Baseline")
            self.ABS_algorithm = None
            self.SCHEDULING = False
            self.scheduling_algorithm = None

            # self.reset_to_zero()
            # self.update_network(FIST=True)
            # answers = self.run_full_frame(first=True, two=self.PRINT)
            self.set_benchmark_pb()
            self.update_network(FIST=True)
            answers_bline = self.run_full_frame(first=True, two=self.PRINT, three=self.SAVE)
            self.first_log_R = answers_bline['sum_log_R']
            baseline_fitness.append(answers_bline)

            baseline_x = self.CDF_downlink
            baseline_y = self.CDF_SINR

            if self.MAP:
                self.save_heatmap('Non-optimised_'+str(self.iteration), SHOW=self.SHOW, SAVE=self.SAVE)

            # Set Benchmark
            if self.PRINT:
                print("Benchmark")
            self.SCHEDULING = True
            self.BENCHMARK_ABS = True
            self.BENCHMARK_SCHEDULING = True

            self.set_benchmark_pb()
            self.update_network()
            answers = self.run_full_frame(first=True, two=self.PRINT)
            answers_bmark = self.run_full_frame(two=self.PRINT, three=self.SAVE)
            benchmark_fitness.append(answers_bmark)

            benchmark_x = self.CDF_downlink
            benchmark_y = self.CDF_SINR

            # Set Evolved
            if self.PRINT:
                print("Evolved")
            self.BENCHMARK_ABS = True
            self.BENCHMARK_SCHEDULING = False
            self.SCHEDULING_TYPE = self.save_scheduling_type
            self.scheduling_algorithm = self.save_scheduling_algorithm
            self.ABS_algorithm = self.save_ABS_algorithm
            self.reset_to_zero()
            self.update_network(FIST=True)
            answers = self.run_full_frame(first=True, two=self.PRINT)
            self.balance_network()
            answers_evo = self.run_full_frame(two=self.PRINT, three=self.SAVE)
            evolved_fitness.append(answers_evo)

            evolved_x = self.CDF_downlink
            evolved_y = self.CDF_SINR

            if self.PRINT:
                print("-----------")

            fig = plt.figure(figsize=[20,15])
            ax1 = fig.add_subplot(1,1,1)

            yar = self.actual_frequency

            ax1.plot(evolved_x, yar, 'r', label="Evolved ABS & Scheduling")
            ax1.plot(benchmark_x, yar, 'b', label="Benchmark ABS & Scheduling")
            ax1.plot(baseline_x, yar, 'k', label="Baseline ABS & Scheduling")

            ax1.set_ylabel('Cumulative distribution')
            ax1.set_xlabel('Log of downlink rates (bits/sec)', color='b')
            ax1.set_ylim([0,1])
            ax1.legend(loc='best')

            if self.SAVE:
                if self.SYNCHRONOUS_ABS:
                    plt.savefig(getcwd() + '/Network_Stats/' + str(self.TIME_STAMP)+'/Synchronous_ABS_Complete_Comparison_'+str(self.iteration)+'.pdf', bbox_inches='tight')
                else:
                    plt.savefig(getcwd()+ self.slash+'Network_Stats'+self.slash +str(self.TIME_STAMP)+self.slash+'Asynchronous_ABS_Complete_Comparison_'+str(self.iteration)+'.pdf', bbox_inches='tight')
            if self.SHOW:
                plt.show()
            if self.SHOW or self.SAVE:
                plt.close()

            if self.MAP:
                self.save_heatmap('Optimised_'+str(self.iteration), SHOW=self.SHOW, SAVE=self.SAVE)

        ave_baseline_sum_log_r = self.average([i['sum_log_R'] for i in baseline_fitness])
        ave_benchmark_sum_log_r = self.average([i['sum_log_R'] for i in benchmark_fitness])
        ave_evolved_sum_log_r = self.average([i['sum_log_R'] for i in evolved_fitness])

        benchmark_difference = self.return_percent(ave_baseline_sum_log_r, ave_benchmark_sum_log_r)
        evolved_difference = self.return_percent(ave_baseline_sum_log_r, ave_evolved_sum_log_r)

        return evolved_difference - benchmark_difference

    def get_normalised_benchmark_difference(self):
        """ Find the difference in performance between the given method and
            the benchmark method. Return the difference as a percentage.
            Levels the playing field so all scheduling methods are compared
            from the same starting point."""

        self.ALL_TOGETHER = True
        self.SYNCHRONOUS_ABS = False
        self.save_scheduling_algorithm = deepcopy(self.scheduling_algorithm)
        self.save_ABS_algorithm = deepcopy(self.ABS_algorithm)
        self.save_scheduling_type = deepcopy(self.SCHEDULING_TYPE)

        baseline_fitness = []
        benchmark_fitness = []
        evolved_fitness = []

        if self.SAVE:
            self.generate_save_folder()

        # Step 1: Get benchmark performance
        for frame in range(self.iterations):
            self.iteration = self.scenario + frame
            # How many full frames of 40 subframes do we want to run?
            # 25 Full frames = 1 second

            self.users = self.user_scenarios[frame]

            # Set Baseline
            if self.PRINT:
                print("Baseline")
            self.SCHEDULING = False
            self.scheduling_algorithm = None

            if self.FAIR:
                self.BENCHMARK_ABS = False
                self.reset_to_zero()
                self.update_network(FIST=True)
                answers_bline = self.run_full_frame(first=True, two=self.PRINT)
                self.balance_network()
                answers_bline = self.run_full_frame(two=self.PRINT, three=self.SAVE)
            else:
                self.BENCHMARK_ABS = True
                self.set_benchmark_pb()
                self.update_network(FIST=True)
                answers_bline = self.run_full_frame(first=True, two=self.PRINT)
                # self.update_network()
            # answers_bline = self.run_full_frame(two=self.PRINT, three=self.SAVE)
            self.first_log_R = answers_bline['sum_log_R']
            baseline_fitness.append(answers_bline)

            baseline_x = self.CDF_downlink
            baseline_y = self.CDF_SINR

            if self.MAP:
                self.save_heatmap('Non-optimised_'+str(self.iteration), SHOW=self.SHOW, SAVE=self.SAVE)

            # Set Benchmark
            if self.PRINT:
                print("Benchmark")
            self.SCHEDULING = True
            self.BENCHMARK_SCHEDULING = True

            if self.FAIR:
                self.BENCHMARK_ABS = False
                self.reset_to_zero()
                self.update_network(FIST=True)
                answers = self.run_full_frame(first=True, two=self.PRINT)
                self.balance_network()
                answers = self.run_full_frame(first=True, two=self.PRINT)
            else:
                self.BENCHMARK_ABS = True
                self.set_benchmark_pb()
                self.update_network(FIST=True)
                answers = self.run_full_frame(first=True, two=self.PRINT)
                self.update_network()
            answers_bmark = self.run_full_frame(two=self.PRINT, three=self.SAVE)
            benchmark_fitness.append(answers_bmark)

            benchmark_x = self.CDF_downlink
            benchmark_y = self.CDF_SINR

            # Set Evolved
            if self.PRINT:
                print("Evolved")

            self.BENCHMARK_SCHEDULING = False
            self.SCHEDULING_TYPE = self.save_scheduling_type
            self.scheduling_algorithm = self.save_scheduling_algorithm

            if self.FAIR:
                self.BENCHMARK_ABS = False
                self.reset_to_zero()
                self.update_network(FIST=True)
                answers = self.run_full_frame(first=True, two=self.PRINT)
                self.balance_network()
                answers = self.run_full_frame(first=True, two=self.PRINT)
            else:
                self.BENCHMARK_ABS = True
                self.set_benchmark_pb()
                self.update_network(FIST=True)
                answers = self.run_full_frame(first=True, two=self.PRINT)
                self.update_network()
            answers_evo = self.run_full_frame(two=self.PRINT, three=self.SAVE)
            evolved_fitness.append(answers_evo)

            evolved_x = self.CDF_downlink
            evolved_y = self.CDF_SINR

            if self.PRINT:
                print("-----------")

            fig = plt.figure(figsize=[20,15])
            ax1 = fig.add_subplot(1,1,1)

            yar = self.actual_frequency

            ax1.plot(evolved_x, yar, 'r', label="Evolved Scheduling")
            ax1.plot(benchmark_x, yar, 'b', label="Benchmark Scheduling")
            ax1.plot(baseline_x, yar, 'k', label="Baseline Scheduling")

            ax1.set_ylabel('Cumulative distribution')
            ax1.set_xlabel('Log of downlink rates (bits/sec)', color='b')
            ax1.set_ylim([0,1])
            ax1.legend(loc='best')

            if self.SAVE:
                if self.SYNCHRONOUS_ABS:
                    plt.savefig(getcwd() + '/Network_Stats/' + str(self.TIME_STAMP)+'/Synchronous_ABS_Complete_Comparison_'+str(self.iteration)+'.pdf', bbox_inches='tight')
                else:
                    plt.savefig(getcwd()+ self.slash+'Network_Stats'+self.slash +str(self.TIME_STAMP)+self.slash+'Asynchronous_ABS_Complete_Comparison_'+str(self.iteration)+'.pdf', bbox_inches='tight')
            if self.SHOW:
                plt.show()
            if self.SHOW or self.SAVE:
                plt.close()

            if self.MAP:
                self.save_heatmap('Optimised_'+str(self.iteration), SHOW=self.SHOW, SAVE=self.SAVE)

        ave_baseline_sum_log_r = self.average([i['sum_log_R'] for i in baseline_fitness])
        ave_benchmark_sum_log_r = self.average([i['sum_log_R'] for i in benchmark_fitness])
        ave_evolved_sum_log_r = self.average([i['sum_log_R'] for i in evolved_fitness])

        benchmark_difference = self.return_percent(ave_baseline_sum_log_r, ave_benchmark_sum_log_r)
        evolved_difference = self.return_percent(ave_baseline_sum_log_r, ave_evolved_sum_log_r)

        return evolved_difference - benchmark_difference

    def get_difficulty_difference(self):
        """ Find the difference in performance between the given method and
            the benchmark method. Return the difference as a percentage."""

        self.ALL_TOGETHER = True
        self.SYNCHRONOUS_ABS = False

        diff_1 = []
        diff_2 = []
        diff_3 = []

        if self.SAVE:
            self.generate_save_folder()

        # Step 1: Get benchmark performance
        for frame in range(self.iterations):
            self.iteration = self.scenario + frame
            self.users = self.user_scenarios[frame]

            if self.PRINT:
                print("Difficulty 1")
            self.DIFFICULTY = 1

            self.reset_to_zero()
            self.update_network(FIST=True)
            answers = self.run_full_frame(first=True, two=self.PRINT)
            self.balance_network()
            answers_evo = self.run_full_frame(two=self.PRINT, three=self.SAVE)
            diff_1.append(answers_evo)

            diff_1_x = self.CDF_downlink
            diff_1_y = self.CDF_SINR

            if self.MAP:
                self.save_heatmap('Non-optimised_'+str(self.iteration), SHOW=self.SHOW, SAVE=self.SAVE)

            if self.PRINT:
                print("Difficulty 2")
            self.DIFFICULTY = 2

            self.reset_to_zero()
            self.update_network(FIST=True)
            answers = self.run_full_frame(first=True, two=self.PRINT)
            self.balance_network()
            answers_evo = self.run_full_frame(two=self.PRINT, three=self.SAVE)
            diff_2.append(answers_evo)

            diff_2_x = self.CDF_downlink
            diff_2_y = self.CDF_SINR

            if self.PRINT:
                print("Difficulty 3")
            self.DIFFICULTY = 3

            self.reset_to_zero()
            self.update_network(FIST=True)
            answers = self.run_full_frame(first=True, two=self.PRINT)
            self.balance_network()
            answers_evo = self.run_full_frame(two=self.PRINT, three=self.SAVE)
            diff_3.append(answers_evo)

            diff_3_x = self.CDF_downlink
            diff_3_y = self.CDF_SINR

            if self.PRINT:
                print("-----------")

            fig = plt.figure(figsize=[20,15])
            ax1 = fig.add_subplot(1,1,1)

            yar = self.actual_frequency

            ax1.plot(diff_3_x, yar, 'r', label="SINR Quantized and Averaged")
            ax1.plot(diff_2_x, yar, 'b', label="SINR Quantized [0:2:30]")
            ax1.plot(diff_1_x, yar, 'k', label="Quantized CGM")

            ax1.set_ylabel('Cumulative distribution')
            ax1.set_xlabel('Log of downlink rates (bits/sec)', color='b')
            ax1.set_ylim([0,1])
            ax1.legend(loc='best')

            if self.SAVE:
                if self.SYNCHRONOUS_ABS:
                    plt.savefig(getcwd() + '/Network_Stats/' + str(self.TIME_STAMP)+'/Synchronous_ABS_Complete_Comparison_'+str(self.iteration)+'.pdf', bbox_inches='tight')
                else:
                    plt.savefig(getcwd()+ self.slash+'Network_Stats'+self.slash +str(self.TIME_STAMP)+self.slash+'Asynchronous_ABS_Complete_Comparison_'+str(self.iteration)+'.pdf', bbox_inches='tight')
            if self.SHOW:
                plt.show()
            if self.SHOW or self.SAVE:
                plt.close()

            if self.MAP:
                self.save_heatmap('Optimised_'+str(self.iteration), SHOW=self.SHOW, SAVE=self.SAVE)

        ave_1_sum_log_r = self.average([i['sum_log_R'] for i in diff_1])
        ave_2_sum_log_r = self.average([i['sum_log_R'] for i in diff_2])
        ave_3_sum_log_r = self.average([i['sum_log_R'] for i in diff_3])

        return {"Diff 1":ave_1_sum_log_r,
                "Diff 2":ave_2_sum_log_r,
                "Diff 3":ave_3_sum_log_r}

    def generate_maps(self):

        minimum = []
        maximum = []
        optimised = []
        self.SCHEDULING = False
        self.ALL_TOGETHER = True

        if self.SAVE:
            self.generate_save_folder()

        for frame in range(self.iterations):
            self.iteration = self.scenario + frame
            self.users = self.user_scenarios[frame]

            self.reset_to_zero()
            self.update_network(FIST=True)
            answers = self.run_full_frame(first=True, two=self.PRINT)

            minimum.append(answers)
            minimum_x = self.CDF_downlink
            minimum_y = self.CDF_SINR

            if self.MAP:
                self.save_heatmap('Minimum_PB_'+str(self.iteration), SHOW=self.SHOW, SAVE=self.SAVE)

            self.balance_network()
            answers = self.run_full_frame(two=self.PRINT, three=self.SAVE)

            optimised.append(answers)
            optimised_x = self.CDF_downlink
            optimised_y = self.CDF_SINR

            if self.MAP:
                self.save_heatmap('Optimised_PB_'+str(self.iteration), SHOW=self.SHOW, SAVE=self.SAVE)

            self.set_benchmark_pb()
            self.update_network(FIST=True)
            answers = self.run_full_frame(first=True, two=self.PRINT)

            maximum.append(answers)
            maximum_x = self.CDF_downlink
            maximum_y = self.CDF_SINR

            if self.MAP:
                self.save_heatmap('Maximum_PB_'+str(self.iteration), SHOW=self.SHOW, SAVE=self.SAVE)

            fig = plt.figure()#figsize=[20,15])
            ax1 = fig.add_subplot(1,1,1)

            yar = self.actual_frequency

            ax1.plot(maximum_x, yar, 'b', label="Power = 35 dBm, Bias = 7 dBm")
            ax1.plot(minimum_x, yar, 'k', label="Power = 23 dBm, Bias = 0 dBm")
            ax1.plot(optimised_x, yar, 'r', label="Optimised Power & Bias")

            ax1.set_ylabel('Cumulative distribution')
            ax1.set_xlabel('Log of downlink rates (bits/sec)', color='b')
            ax1.set_ylim([0,1])
            ax1.legend(loc='best')

            if self.SAVE:
                plt.savefig(getcwd()+ self.slash+'Network_Stats'+self.slash +str(self.TIME_STAMP)+self.slash+'Complete_Comparison_'+str(self.iteration)+'.pdf', bbox_inches='tight')
            if self.SHOW:
                plt.show()
            if self.SHOW or self.SAVE:
                plt.close()

    def generate_save_folder(self):
        """ Creates all the folders necessary to save figures about the network
        """

        file_path = getcwd()
        if not path.isdir(str(file_path) + "/Network_Stats"):
            mkdir(str(file_path) + "/Network_Stats")
        if not path.isdir(str(file_path) + "/Network_Stats/" + str(self.TIME_STAMP)):
            mkdir(str(file_path) + "/Network_Stats/" + str(self.TIME_STAMP))
        if not path.isdir(str(file_path) + "/Network_Stats/" + str(self.TIME_STAMP) + "/Heatmaps"):
            mkdir(str(file_path) + "/Network_Stats/" + str(self.TIME_STAMP) + "/Heatmaps")
        if not path.isdir(str(file_path) + "/Network_Stats/" + str(self.TIME_STAMP) + "/Heatmaps/input"):
            mkdir(str(file_path) + "/Network_Stats/" + str(self.TIME_STAMP) + "/Heatmaps/input")
        if not path.isdir(str(file_path) + "/Network_Stats/" + str(self.TIME_STAMP) + "/Heatmaps/output"):
            mkdir(str(file_path) + "/Network_Stats/" + str(self.TIME_STAMP) + "/Heatmaps/output")

    def plot_gain_matrix(self, cell, SAVE=True, SHOW=False, plot_users=True, plot_hotspot=False):
        """ generates a heat map plot of a given cell"""

        fig = plt.figure(figsize=[20,20])
        ax = fig.add_subplot(1,1,1)
        ax.axes.get_xaxis().set_ticks([])
        ax.axes.get_yaxis().set_ticks([])
        ax.set_ylabel('S - N', fontsize=40)
        ax.set_xlabel('W - E', fontsize=40)
        data = cell['gain']
        #plt.pcolor(data,cmap=plt.cm.Reds,edgecolors='k')
        heat = plt.imshow(data, origin='lower')
        cb = plt.colorbar(heat, fraction=0.0455, pad=0.04)
        for t in cb.ax.get_yticklabels():
            t.set_fontsize(30)
        cb.set_label('Gain (dB)', fontsize=40)
        plt.scatter(cell['location'][0], cell['location'][1], color='g')

        if plot_hotspot:
            # Find the hottest point in the gain map for the cell
            a = np.unravel_index(cell['gain'].argmax(), cell['gain'].shape)
            plt.scatter(a[1], a[0])
        if plot_users:
            # Plot all the users attached to the cell
           # for i in cell['attached_users']:
           #     user = self.users[i]
            for user in self.users:
                plt.scatter(user['location'][0], user['location'][1])

        if SAVE:
            plt.savefig(getcwd()+'/Network_Stats/'+str(self.TIME_STAMP)+'/' + str(cell['id']) + '.pdf', bbox_inches='tight')
        if SHOW:
            plt.show()

    def plot_MC_sector(self, iteration, cell_id, SHOW=False, SAVE=False):
        """ generates a heat map plot of a given MC sector"""
        self.generate_save_folder()
        self.get_macro_small_interaction()
        macro = self.macro_cells[cell_id]
        SCs = macro['small_interactions']
        SC_numbers = SCs

        total_heatmap = None
        self.masks = []
        gain_copy = deepcopy(self.gains)
        for i in range(self.n_all_cells):
            if i < 21:
                gain_copy[i] = np.asarray(gain_copy[i]) + self.macro_cells[i]['power']
            else:
                gain_copy[i] = np.asarray(gain_copy[i]) + self.small_cells[i-21]['power'] + self.small_cells[i-21]['bias']

        gain_power_bias = np.asarray(gain_copy)
        original_gains = deepcopy(gain_power_bias)
        gain_power_bias.sort(axis=0)

        for i, cell in enumerate(original_gains):
            mask = (cell == gain_power_bias[-1])
            self.masks.append(mask)

        total_heatmap = (10**((original_gains[cell_id]-30)/10))
        for i, gain in enumerate(original_gains):
            if (i-21) in SC_numbers:
                total_heatmap = total_heatmap + (10**((gain-30)/10))
        total_heatmap = 10*np.log10(1000*total_heatmap)

        fig = plt.figure()#figsize=[15,15])
        plt.imshow(total_heatmap, origin='lower')

        # Plot contours around cells in question
        hist2D, xedges, yedges = self.compute_histogram([0,self.size+1], [0,self.size+1], self.masks[cell_id])
        plt.contour(hist2D, extent=[xedges[0],xedges[-1], yedges[0],yedges[-1]], levels=[40], linestyles=['-'], colors=['black'], linewidths=2, alpha=0.75)
        for i in SC_numbers:
            hist2D, xedges, yedges = self.compute_histogram([0,self.size+1], [0,self.size+1], self.masks[i+21])
            plt.contour(hist2D, extent=[xedges[0],xedges[-1], yedges[0],yedges[-1]], levels=[40], linestyles=['-'], colors=['red'], linewidths=2, alpha=0.5)

        # Plot all the users attached to the MC
        for i in macro['attached_users']:
            user = self.users[i]
            plt.scatter(user['location'][0], user['location'][1], color='b')

        # Plot SC attached users in region
        for i in macro['potential_users']:
            if i not in macro['attached_users']:
                user = self.users[i]
                plt.scatter(user['location'][0], user['location'][1], color='r')
        if SAVE:
            plt.savefig(getcwd()+'/Network_Stats/'+str(self.TIME_STAMP)+'/MC_'+str(cell_id)+'_'+str(iteration)+'_Map.pdf')
        if SHOW:
            plt.show()
        if SHOW or SAVE:
            plt.close()

    def get_most_complex_SC(self):
        """ Finds the SC in the network which is under the influence of the
            most MCs.
        """

        self.complex_SC = [None, None, None]

        for small in self.small_cells:
            all_UEs = small['attached_users']
            macro_list = {}
            if all_UEs:
                num_attached = len(all_UEs)
              # For each MC sector that the SC overlaps with find the number
              # of UEs that would attach to these MCs if no SC were present.
                for ind in all_UEs:
                    user = self.users[int(ind[2:])]
                    macro = user['macro']
                    if macro in macro_list:
                        macro_list[macro] += 1
                    else:
                        macro_list[macro] = 1
            if len(macro_list) > self.complex_SC[1]:
                self.complex_SC = [small['id'], len(macro_list), len(small['attached_users'])]
            elif len(macro_list) == self.complex_SC[1]:
                if len(small['attached_users']) > self.complex_SC[2]:
                    self.complex_SC = [small['id'], len(macro_list), len(small['attached_users'])]

    def plot_SC_sector(self, iteration, cell_id, SHOW=False, SAVE=False):
        """ generates a heat map plot of a given MC sector"""

        small = self.small_cells[cell_id]
        all_UEs = small['attached_users']
        macro_list = {}

        for ind in all_UEs:
            user = self.users[int(ind[2:])]
            macro = user['macro']
            if macro in macro_list:
                macro_list[macro] += 1
            else:
                macro_list[macro] = 1
        MC_numbers = []
        for i in macro_list:
            MC_numbers.append(i)
        total_heatmap = None
        self.masks = []
        gain_copy = deepcopy(self.gains)
        for i in range(self.n_all_cells):
            if i < 21:
                gain_copy[i] = np.asarray(gain_copy[i]) + self.macro_cells[i]['power']
            else:
                gain_copy[i] = np.asarray(gain_copy[i]) + self.small_cells[i-21]['power'] + self.small_cells[i-21]['bias']

        gain_power_bias = np.asarray(gain_copy)
        original_gains = deepcopy(gain_power_bias)
        gain_power_bias.sort(axis=0)

        for i, cell in enumerate(original_gains):
            mask = (cell == gain_power_bias[-1])
            self.masks.append(mask)

        total_heatmap = (10**((original_gains[21+cell_id]-30)/10))
        for i, gain in enumerate(original_gains):
            if i in MC_numbers:
                total_heatmap = total_heatmap + (10**((gain-30)/10))
        total_heatmap = 10*np.log10(1000*total_heatmap)

        fig = plt.figure()#figsize=[15,15])
        plt.imshow(total_heatmap, origin='lower')

        # Plot contours around cells in question
        hist2D, xedges, yedges = self.compute_histogram([0,self.size+1], [0,self.size+1], self.masks[21+cell_id])
        plt.contour(hist2D, extent=[xedges[0],xedges[-1], yedges[0],yedges[-1]], levels=[40], linestyles=['-'], colors=['red'], linewidths=2, alpha=0.5)
        for i in MC_numbers:
            hist2D, xedges, yedges = self.compute_histogram([0,self.size+1], [0,self.size+1], self.masks[i])
            plt.contour(hist2D, extent=[xedges[0],xedges[-1], yedges[0],yedges[-1]], levels=[40], linestyles=['-'], colors=['black'], linewidths=2, alpha=0.5)

        # Plot all the users attached to the SC
        for i in small['attached_users']:
            user = self.users[i]
            plt.scatter(user['location'][0], user['location'][1], color='b')

        # Plot MC attached users in region
        for i in MC_numbers:
            macro = self.macro_cells[i]
            for UE in macro['attached_users']:
                user = self.users[UE]
                plt.scatter(user['location'][0], user['location'][1], color='g')
        if SAVE:
            plt.savefig(getcwd()+'/Network_Stats/'+str(self.TIME_STAMP)+'/SC_'+str(cell_id)+'_'+str(iteration)+'_Map.pdf')
        if SHOW:
            plt.show()
        if SHOW or SAVE:
            plt.close()

    def compute_histogram(self, XRANGE, YRANGE, mask):
        """ This function returns a closed contour that encloses cell coverage
            areas. It computes a 'concave hull' like trace around the set of
            points that constitute a cell coverage area. This is achieved by
            computing a historgram in 2-D over the points.
        """

        Bins = 100
        hist2D, xedges, yedges = np.histogram2d(np.nonzero(mask)[0], np.nonzero(mask)[1], bins=[Bins,Bins], range=[XRANGE,YRANGE], normed=False)
        return hist2D, xedges, yedges

    def save_heatmap(self, iteration, SHOW=False, SAVE=False):
        """ Saves a heatmap of the overall state of the network based on cell
            gains, powers, and biases. Includes delineated boundaries and UEs.
        """
        total_heatmap = None
        self.masks = []

        gain_copy = deepcopy(self.gains)
        power_copy = deepcopy(self.gains)
        for i in range(self.n_all_cells):

            if i < 21:
                gain_copy[i] = np.asarray(gain_copy[i]) + self.macro_cells[i]['power']
                power_copy[i] = np.asarray(power_copy[i]) + self.macro_cells[i]['power']

            else:
                power_copy[i] = np.asarray(power_copy[i]) + self.small_cells[i-21]['power']
                gain_copy[i] = np.asarray(gain_copy[i]) + self.small_cells[i-21]['power'] + self.small_cells[i-21]['bias']

        gain_power_bias = np.asarray(gain_copy)
        gain_power = np.asarray(power_copy)

        original_gains = deepcopy(gain_power_bias)
        original_power = deepcopy(gain_power)

        gain_power_bias.sort(axis=0)
        gain_power.sort(axis=0)

        if SHOW or SAVE:
            fig = plt.figure(figsize=[20,20])
            ax = fig.add_subplot(1,1,1)
            ax.axes.get_xaxis().set_ticks([])
            ax.axes.get_yaxis().set_ticks([])
            ax.set_ylabel('S - N', fontsize=40)
            ax.set_xlabel('W - E', fontsize=40)

        for i, cell in enumerate(original_gains):
            mask1 = (cell == gain_power_bias[-1])
            mask2 = (original_power[i] == gain_power[-1])
            self.masks.append([mask1, mask2])

        total_heatmap = (10**((original_gains[0]-30)/10))
        for i, gain in enumerate(original_gains):
            if i >= 1:
                total_heatmap = total_heatmap + (10**((gain-30)/10))
        total_heatmap = 10*np.log10(1000*total_heatmap)

        if SHOW or SAVE:
            heat = plt.imshow(total_heatmap, origin='lower')

        hist_list = []
        for i, mask in enumerate(self.masks):
            hist2Da, xedgesa, yedgesa = self.compute_histogram([0,self.size+1], [0,self.size+1], mask[0])
            if i >= 21:
                hist2Db, xedgesb, yedgesb = self.compute_histogram([0,self.size+1], [0,self.size+1], mask[1])
            else:
                hist2Db = None
            hist_list.append([hist2Da, hist2Db])
            if SHOW or SAVE:
                [L3] = [40]
                if i < 21:
                    plt.contour(hist2Da, extent=[xedgesa[0],xedgesa[-1], yedgesa[0],yedgesa[-1]], levels=[L3], linestyles=['-'], colors=['black'], linewidths=2, alpha=0.75)
                else:
                    plt.contour(hist2Da, extent=[xedgesa[0],xedgesa[-1], yedgesa[0],yedgesa[-1]], levels=[L3], linestyles=['-'], colors=['red'], linewidths=2, alpha=0.5)
                    if self.small_cells[i-21]['bias'] != 0:
                        plt.contour(hist2Db, extent=[xedgesa[0],xedgesa[-1], yedgesa[0],yedgesa[-1]], levels=[L3], linestyles=['-'], colors=['blue'], linewidths=2, alpha=0.5)
        if SHOW or SAVE:
            cb = plt.colorbar(heat, fraction=0.0455, pad=0.04)
            for t in cb.ax.get_yticklabels():
                t.set_fontsize(30)
            cb.set_label('Gain (dB)', fontsize=40)
            for user in self.users:
                plt.scatter(user['location'][0], user['location'][1])
        if SAVE:
            plt.savefig(getcwd()+'/Network_Stats/'+str(self.TIME_STAMP)+'/Network_Map_' + str(iteration) + '.pdf', bbox_inches='tight')
        if SHOW:
            plt.show()
        if SHOW or SAVE:
            plt.close()
        return total_heatmap, hist_list, xedgesa, yedgesa

    def save_helpless_UEs_heatmap(self, iteration, SHOW=False, SAVE=False):
        """ Saves a heatmap of the overall state of the network based on cell
            gains, powers, and biases. Includes delineated boundaries and the
            locations of UEs who have a maximum SINR of less than 1 (i.e. they
            cannot be scheduled at all).
        """
        total_heatmap = None
        self.masks = []

        gain_copy = deepcopy(self.gains)
        power_copy = deepcopy(self.gains)
        for i in range(self.n_all_cells):

            if i < 21:
                gain_copy[i] = np.asarray(gain_copy[i]) + self.macro_cells[i]['power']
                power_copy[i] = np.asarray(power_copy[i]) + self.macro_cells[i]['power']

            else:
                power_copy[i] = np.asarray(power_copy[i]) + self.small_cells[i-21]['power']
                gain_copy[i] = np.asarray(gain_copy[i]) + self.small_cells[i-21]['power'] + self.small_cells[i-21]['bias']

        gain_power_bias = np.asarray(gain_copy)
        gain_power = np.asarray(power_copy)

        original_gains = deepcopy(gain_power_bias)
        original_power = deepcopy(gain_power)

        gain_power_bias.sort(axis=0)
        gain_power.sort(axis=0)

        if SHOW or SAVE:
            fig = plt.figure(figsize=[20,20])
            ax = fig.add_subplot(1,1,1)
            ax.axes.get_xaxis().set_ticks([])
            ax.axes.get_yaxis().set_ticks([])
            ax.set_ylabel('S - N', fontsize=40)
            ax.set_xlabel('W - E', fontsize=40)

        for i, cell in enumerate(original_gains):
            mask1 = (cell == gain_power_bias[-1])
            mask2 = (original_power[i] == gain_power[-1])
            self.masks.append([mask1, mask2])

        total_heatmap = (10**((original_gains[0]-30)/10))
        for i, gain in enumerate(original_gains):
            if i >= 1:
                total_heatmap = total_heatmap + (10**((gain-30)/10))
        total_heatmap = 10*np.log10(1000*total_heatmap)

        if SHOW or SAVE:
            heat = plt.imshow(total_heatmap, origin='lower')

        hist_list = []
        for i, mask in enumerate(self.masks):
            hist2Da, xedgesa, yedgesa = self.compute_histogram([0,self.size+1], [0,self.size+1], mask[0])
            if i >= 21:
                hist2Db, xedgesb, yedgesb = self.compute_histogram([0,self.size+1], [0,self.size+1], mask[1])
            else:
                hist2Db = None
            hist_list.append([hist2Da, hist2Db])
            if SHOW or SAVE:
                [L3] = [40]
                if i < 21:
                    plt.contour(hist2Da, extent=[xedgesa[0],xedgesa[-1], yedgesa[0],yedgesa[-1]], levels=[L3], linestyles=['-'], colors=['black'], linewidths=2, alpha=0.75)
                else:
                    plt.contour(hist2Da, extent=[xedgesa[0],xedgesa[-1], yedgesa[0],yedgesa[-1]], levels=[L3], linestyles=['-'], colors=['red'], linewidths=2, alpha=0.5)
                    if self.small_cells[i-21]['bias'] != 0:
                        plt.contour(hist2Db, extent=[xedgesa[0],xedgesa[-1], yedgesa[0],yedgesa[-1]], levels=[L3], linestyles=['-'], colors=['blue'], linewidths=2, alpha=0.5)
        if SHOW or SAVE:
            cb = plt.colorbar(heat, fraction=0.0455, pad=0.04)
            for t in cb.ax.get_yticklabels():
                t.set_fontsize(30)
            cb.set_label('Gain (dB)', fontsize=40)
            for ind in self.helpless_UEs:
                user = self.users[ind]
                plt.scatter(user['location'][0], user['location'][1], color="w")
        if SAVE:
            plt.savefig(getcwd()+'/Network_Stats/'+str(self.TIME_STAMP)+'/Network_Map_' + str(iteration) + '.pdf', bbox_inches='tight')
        if SHOW:
            plt.show()
        if SHOW or SAVE:
            plt.close()

    def save_CDF_bottom(self, name, opts, SHOW=False, SAVE=False):
        """ Saves a CDF plot of the Sum Log R and SINR of all users in the
            network.
        """

        fig = plt.figure()#figsize=[20,15])
        ax1 = fig.add_subplot(1,1,1)

        yar = np.array(list(range(len(opts['Baseline'])))) / float(
            len(opts['Baseline']))
        half_UEs = int(len(yar)/2)

        for opt in sorted(opts.keys()):
            ax1.plot(opts[opt][:half_UEs], yar[:half_UEs],
                         label=str(opt))  # , linewidth=2.5)

        upper_limit = max([max(opts[opt][:half_UEs]) for opt in opts])
        lower_limit = min([min(opts[opt][:half_UEs]) for opt in opts])

        ax1.set_ylim([0, 0.5])
        ax1.grid(True)

        ax1.grid(which='major', alpha=0.5)
        ax1.grid(which='minor', alpha=0.5)

        minor_ticks = np.arange(lower_limit, upper_limit, 1)
        ax1.set_xticks(minor_ticks, minor=True)

        major_ticks = np.arange(0, 0.6, 0.1)
        ax1.set_yticks(major_ticks, minor=True)

        # ax1.set_title(name, fontsize=30)
        ax1.set_ylabel('Cumulative distribution')
        ax1.set_xlabel('Downlink rates (Mbps)')

        legend = ax1.legend(loc='lower right', shadow=True)#, prop={'size': 20})
        frame = legend.get_frame()
        frame.set_facecolor('0.90')

        if SAVE:
            plt.savefig(getcwd()+'/Network_Stats/'+str(self.TIME_STAMP)+'/' +
                        str(name) + '_1.pdf', bbox_inches='tight')
        if SHOW:
            plt.show()

        if SHOW or SAVE:
            plt.close()

    def save_CDF_top(self, name, opts, SHOW=False,
                        SAVE=False):
        """ Saves a CDF plot of the Sum Log R and SINR of all users in the
            network.
        """

        fig = plt.figure()  # figsize=[20,15])
        ax1 = fig.add_subplot(1, 1, 1)

        yar = np.array(list(range(len(opts['Baseline'])))) / float(
            len(opts['Baseline']))
        half_UEs = int(len(yar) / 2)

        for opt in sorted(opts.keys()):
            ax1.semilogx(opts[opt][half_UEs:], yar[half_UEs:],
                     label=str(opt))  # , linewidth=2.5)

        ax1.set_ylim([0.5, 1])
        ax1.grid(True)

        majorLocator = LogLocator(10)
        majorFormatter = FormatStrFormatter('%.1f')
        ax1.xaxis.set_major_locator(majorLocator)
        ax1.xaxis.set_major_formatter(majorFormatter)

        ax1.grid(which='minor', alpha=0.5)

        major_ticks = np.arange(0.5, 1, 0.1)
        ax1.set_yticks(major_ticks, minor=True)

        # ax1.set_title(name, fontsize=30)
        ax1.set_ylabel('Cumulative distribution')
        ax1.set_xlabel('Downlink rates (Mbps)')

        legend = ax1.legend(loc='lower right', shadow=True)#, prop={'size': 20})
        frame = legend.get_frame()
        frame.set_facecolor('0.90')

        if SAVE:
            plt.savefig(
                getcwd() + '/Network_Stats/' + str(self.TIME_STAMP) + '/' +
                str(name) + '_2.pdf', bbox_inches='tight')
        if SHOW:
            plt.show()

        if SHOW or SAVE:
            plt.close()

    def save_CDF_whole(self, name, opts, SHOW=False,
                        SAVE=False):
        """ Saves a CDF plot of the Sum Log R and SINR of all SC users in the
            network.
        """

        fig = plt.figure()  # figsize=[18, 12])
        ax1 = fig.add_subplot(1, 1, 1)

        yar = np.array(list(range(len(opts['Baseline']))))/float(len(opts['Baseline']))

        for opt in sorted(opts.keys()):
            ax1.semilogx(opts[opt], yar, label=str(opt))#, linewidth=2.5)

        ax1.set_ylim([0, 1])
        ax1.grid(True)

        majorLocator = LogLocator(10)
        majorFormatter = FormatStrFormatter('%.1f')
        ax1.xaxis.set_major_locator(majorLocator)
        ax1.xaxis.set_major_formatter(majorFormatter)

        ax1.grid(which='minor', alpha=0.5)

        major_ticks = np.arange(0, 1, 0.1)
        ax1.set_yticks(major_ticks, minor=True)

        # ax1.set_title(name, fontsize=30)
        ax1.set_ylabel('Cumulative distribution')#, fontsize=25)
        ax1.set_xlabel('Downlink rates [Mbps]')#, fontsize=25)

        legend = ax1.legend(loc='lower right', shadow=True)#, prop={'size': 20})
        frame = legend.get_frame()
        frame.set_facecolor('0.90')

        if SAVE:
            plt.savefig(
                getcwd() + '/Network_Stats/' + str(self.TIME_STAMP) + '/' +
                str(name) + '.pdf', bbox_inches='tight')
        if SHOW:
            plt.show()

        plt.close()

    def save_CDF_plot(self, iteration, SHOW=False, SAVE=False):
        """ Saves a CDF plot of the Sum Log R and SINR of all users in the
            network.
        """

        fig = plt.figure(figsize=[20,15])
        ax1 = fig.add_subplot(1,1,1)
        ax2 = ax1.twiny()

        xar = self.CDF_downlink
        yar = self.actual_frequency
        zar = self.CDF_SINR

        minor_ticks = np.arange(0, 200, 1)
        ax1.set_xticks(minor_ticks, minor=True)
        ax1.grid(which='minor', alpha=0.8)
        major_ticks = np.arange(0, 1, 0.1)
        ax1.set_yticks(major_ticks)
        ax1.set_yticks(major_ticks, minor=True)
        ax1.grid(which='major', alpha=0.5)

        ax1.plot(self.first_xar, yar, 'b', label="Pre-Optimization Downlink")
        ax1.plot(xar, yar, 'r', label="Post-Optimization Downlink")
        ax1.set_ylabel('Cumulative distribution')
        ax1.set_ylim([0,1])
        ax1.set_xlabel('Log of downlink rates (bits/sec)', color='b')
        ax1.legend(loc=2)

        ax2.plot(self.first_zar, yar, '#ffa500', label="Pre-Optimization SINR")
        ax2.plot(zar, yar, 'g', label="Post-Optimization SINR")
        ax2.set_xlabel('Log of SINR', color='g')
        ax2.legend(loc=4)

        if SAVE:
            plt.savefig(getcwd()+'/Network_Stats/'+str(self.TIME_STAMP)+'/Network_CDF_' + str(iteration) + '.pdf', bbox_inches='tight')
        if SHOW:
            plt.show()

        if SHOW or SAVE:
            plt.close()

    def redistribute_users(self, scenario=1):
        """ Re-distributes the UEs about the map, taking hotspots into account.
            Also takes the environmental encoding into account and doesn't
            place users in water.
        """

        self.seed += scenario
        seed(self.seed)
        np.random.seed(self.seed)
        self.user_locations = []
        self.users = []
        hotspots = deepcopy(self.hotspots)
        while len(self.user_locations) < int(self.n_users):
          # Put 5-25 UEs in a hotspot location that is either randomly
          # positioned on the map or positioned near a SC.
            prob_generating_hotspot = random()
            if len(hotspots) > 0:
                if prob_generating_hotspot < 0.2:
                    spot = randint(0, len(hotspots)-1)
                    hotspot = hotspots[spot]
                    hotspot['target'] = randint(5,20)
                    hotspots.pop(spot)
                    for i in range(hotspot['target']):
                        stop = False
                        while stop == False:
                           # x = int(round(gauss(hotspot['location'][0], 5)))
                           # y = int(round(gauss(hotspot['location'][1], 5)))
                            theta = np.random.rand()*2*np.pi
                            r = np.random.uniform(0, 160)
                            x = hotspot['location'][0] + int(np.sqrt(r)*np.cos(theta))
                            y = hotspot['location'][1] + int(np.sqrt(r)*np.sin(theta))
                            if (0 <= x <= self.size) and (0 <= y<= self.size):
                                env_loc = self.environmental_encoding[y, x]
                                if (env_loc != 0.5):
                                    stop = True
                        self.user_locations.append([x, y])
                    hotspot["users"] = hotspot['target']

                else:
                    # Uniformly distribute 5-20 UEs onto the map i.e. not in
                    # hotspots. Maybe we could assign a velocity vector to these
                    # inter-hotspot UEs.
                    num_uniform_dist_UEs = randint(5,20)
                    for i in range(num_uniform_dist_UEs):
                        stop = False
                        while stop == False:
                            x, y = [randint(0, self.size), randint(0,self.size)]
                            env_loc = self.environmental_encoding[y, x]
                            if env_loc != 0.5:
                                stop = True
                        self.user_locations.append([x, y])
            else:
                # Uniformly distribute 5-20 UEs onto the map i.e. not in
                # hotspots. Maybe we could assign a velocity vector to these
                # inter-hotspot UEs.
                num_uniform_dist_UEs = randint(5,20)
                for i in range(num_uniform_dist_UEs):
                    stop = False
                    while stop == False:
                        x, y = [randint(0, self.size), randint(0,self.size)]
                        env_loc = self.environmental_encoding[y, x]
                        if env_loc != 0.5:
                            stop = True
                    self.user_locations.append([x, y])

        if len(self.user_locations) > self.n_users:
            for i in range(len(self.user_locations)-self.n_users):
                del self.user_locations[i]

        for i in range(self.n_users):
            idx = 'UE' + str(i)
            location = [self.user_locations[i][0], self.user_locations[i][1]]
            user = {'location':location, 'id':idx}
            self.users.append(user)
        self.user_locations = self.user_locations[:self.n_users]

    def get_location(self, x, lim):
        """ Given percentage values, returns actual locations."""

        return round(float(lim)/100 * (x + (x*(100-99.99)/99.99)))

    def evo_distribute_users(self, scenario=1):
        """ Uses GP to re-distribute the UEs about the map, taking hotspots
            into account. Also takes the environmental encoding into account
            and doesn't place users in water.
        """

        def get_random_location():
            stop = False
            while stop == False:
                x, y = [randint(0, self.size), randint(0,self.size)]
                env_loc = self.environmental_encoding[y, x]
                if env_loc != 0.5:
                    stop = True
            return [x, y]

        hotspots = deepcopy(self.scenario_inputs[0])
        n_hotspots = len(hotspots)
        p_hotspot = self.scenario_inputs[1] # 0 - 100
        n_in_hotspots = self.get_location(self.scenario_inputs[2], self.n_users)

        self.seed += scenario
        seed(self.seed)
        np.random.seed(self.seed)
        self.user_locations = []
        self.users = []

        total_hotspot_size = sum([spot['size'] for spot in hotspots])

        # What is the total sum of all percentages of all hotspots? Can be
        # over 100.

        # The "proportion" of a hotspot is an integer between 0 and 100. We
        # sum all proportions together to find the total proportion, then take
        # each hotspot proportion generate a percentage value which takes into
        # account all other hotspots in the current scenario. For each hotspot
        # we then take the total number of UEs in all hotspots and apply this
        # percentage value in order to find how many UEs will be in each
        # hotspot. Weird way of doing things, but hey, it's interesting.

        total_proportion = 0
        for spot in hotspots:
            spot['users'] = 0
            if spot['size'] == total_hotspot_size:
                spot['proportion'] = 1
            else:
                spot['proportion'] = 1 - spot['size']/total_hotspot_size
            total_proportion += spot['proportion']
        for spot in hotspots:
            spot['target'] = spot['proportion']*n_in_hotspots
            prob_hotspot_near_SC = random()
            if prob_hotspot_near_SC < spot["near_SC"]:
                spot['location'][0] = self.get_location(spot['location'][0], self.size)
                spot['location'][1] = self.get_location(spot['location'][1], self.size)
            else:
                selected_SC = randint(0, self.n_small_cells-1)
                spot['location'] = self.small_cells[selected_SC]['location']
                spot['location'][0] += spot["SC_offset"][0]
                spot['location'][1] += spot["SC_offset"][1]
                if spot['location'][0] < 0:
                    spot['location'][0] = 0
                if spot['location'][1] < 0:
                    spot['location'][1] = 0
                if spot['location'][0] > self.size:
                    spot['location'][0] = 0
                if spot['location'][1] > self.size:
                    spot['location'][1] = 0

        for i in range(self.n_users):
            idx = 'UE' + str(i)
            prob_generating_hotspot = random()
            if (len(hotspots) > 0) and n_in_hotspots:
                if prob_generating_hotspot < p_hotspot/100.0:
                    spot = randint(0, len(hotspots)-1)
                    hotspot = hotspots[spot]
                    stop = False
                    while stop == False:
                       # x = int(round(gauss(hotspot['location'][0], hot['radius'])))
                       # y = int(round(gauss(hotspot['location'][1], hot['radius'])))
                        theta = np.random.rand()*2*np.pi
                        r = np.random.uniform(0, hotspot['radius'])
                        x = hotspot['location'][0] + int(np.sqrt(r)*np.cos(theta))
                        y = hotspot['location'][1] + int(np.sqrt(r)*np.sin(theta))
                        if (0 <= x <= self.size) and (0 <= y<= self.size):
                           # env_loc = self.environmental_encoding[y, x]
                           # if (env_loc != 0.5):
                            stop = True
                    location = [x, y]
                    hotspot['users'] += 1
                    if hotspot['users'] == hotspot['target']:
                        hotspots.remove(hotspot)
                else:
                    location = get_random_location()
            else:
                location = get_random_location()
            user = {'id':idx, 'location':location}
            self.users.append(user)

"""
    def approve_handover(self, user, cell, small):
        # checks whether a handover will lead to an increase in
        # performance for a user. Only recommends a handover if
        # performance increases. This is for use with multiple macro
        # cells running ABS

        handover = false
        gain_macro = cell.gain(user.location(1), user.location(2))
        gain_small = small.gain(user.location(1), user.location(2))
        sum_macro = 0
        other_cells = {}
        for macro in self.n_macro_cells:
            if ~ macro == cell
                if isempty(other_cells)
                    other_cells{1} = macro
                else
                    other_cells{end+1} = macro

        for i = 1:(self.n_macro_cells - 1):
            macro = other_cells{i}
            huk = macro.gain(user.location(1), user.location(2))+macro.power
            sum_macro = sum_macro + huk

        signal = (gain_small+small.power) * ((gain_small+small.power)+sum_macro) / ((gain_macro+macro.power)-(gain_small+small.power))
        interference = get_interference(self, user)
        if signal > interference
            handover = true
        return handover
"""
