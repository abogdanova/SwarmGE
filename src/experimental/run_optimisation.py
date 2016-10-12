
from os import getcwd, path
from time import sleep
import random
random.seed(10)
scheduling = {}


def mane():
    """allows you to run the Optimise_Network program outside of an
    evolutionary setting."""
    SC_DISTRIBUTION = "test"

    """ Number of Small Cells in the simulation. Currently available sets are
        3, 30, 50, 79, and 100 SCs."""
    no_small_cells = 30

    """ Number of users in the simulation."""
    N_USERS = 5000 # 1260 # 5000

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

    """ Do we want to give the benchmark the best possible chance? Then we
        allow SC powers and biases to change using our optimisation algorithm.
        Otherwise they're fixed (which is how the benchmark works, but isn't
        exactly fair)."""
    fair = False

    """ Compares given solutions against both baseline and benchmark results.
        Returns the average difference in performance between the evolved and
        benchmark methods (in terms of a percentage)."""
    COMPARE = False

    """ Run the network but using the benchmark methods for ABS and scheduling.
    """
    BENCHMARK = False

    """ Runs the network using realistic network parameters, including
        quantized SINR information."""
    REALISTIC = True

    """ Apply all optimisation steps on the network in one go rather than
        running each step (power & bias, ABS, scheduling) separately. Gives the
        same SumLogR value ultimately, but takes much less time as the network
        only needs to be run once. Turning to False will mean the returned
        fitness is the improvement realised by the last applied operation (e.g.
        Power/Bias, ABS, or Scheduling optimisation)."""
    OPT_ALL_TOGETHER = False

    """ Display CDF plots of network performance at each full frame."""
    SHOW_PLOTS = True

    """ Saves stats of network performance at each full frame. If SHOW_PLOTS or
        MAP_NETWORK are true, then saves thos respective things too."""
    SAVE_STATS = False

    """ Generates a heatmap of the network with all UEs located on the map.
        Either SHOW_PLOTS or SAVE_PLOTS must be set to True for this to does
        something."""
    MAP_NETWORK = False

    """ Prints out network statistics after each full frame."""
    PRINT_STATS = True

    """ Number of different scenarios the network is to be run for."""
    iterations = 100

    """ Starting scenario from which to run the network."""
    scenario = 10

    """ Main scheduling method to use on the network. Available scheduling
        methods are defined in the "scheduling" dictionary below."""
    scheduling_type = "simplified_threshold"

    scheduling['original_low_density_threshold'] = "(T20-(pdiv(T13, T14)-pdiv((((np.sign(np.sin(T15))+np.sign((T16*T10)))*(T6*pdiv(pdiv(T17, T7), pdiv(T5, T18))))+(((T13*(T8-T4))-(np.sqrt(abs(T9))+(T21+T18)))+pdiv(((T21+T20)-T17), np.sqrt(abs(pdiv(T11, ABS)))))), (((ABS+pdiv(ABS, T8))-pdiv(pdiv(pdiv(T9, T8), np.sqrt(abs(T19))), (T13*T9)))+((np.sign((T16*T7))+pdiv(ABS, np.sign(T20)))-np.sin((np.log(1+abs(T9))*np.log(1+abs(T20)))))))))"

    scheduling['simplified_low_density_threshold'] = "T20-(pdiv(T13, T14)-pdiv(((2*(T6*pdiv(pdiv(T17, T7), pdiv(T5, T18))))+(((T13*(T8-T4))-(1.5 +(T21+T18)))+pdiv(((T21+T20)-T17), 2.14125255))), ABS))"

    scheduling['simplified_threshold'] = "ABS*(0.5+((T6*T17*(T4-T5))-T4))"
    
    scheduling['test_topology'] = "np.sqrt(abs((pdiv((pdiv(((T17*T15)+np.sign((T20*T12))), +0.6)*((T16*T3)-(np.sin((T20*T2))+(pdiv(T20, T15)-pdiv(T14, T17))))), pdiv((T9-(np.sign(T11)-np.sqrt(abs((T4-T3))))), ((pdiv(T2, np.sin(T20))-(T5-pdiv(T3, T12)))+(((T7*T2)*(T15+T2))*(pdiv(T5, T17)+pdiv(T21, T17))))))*pdiv((T5-T15), ((T18*np.log(1+abs((np.sqrt(abs(T3))+np.log(1+abs(T13))))))+np.sin((((T19+T19)+(T2*T20))-np.log(1+abs(T19)))))))))"

    if True:
        import hold_network_info
        curr_path = getcwd()
        run_sim = False
        if not path.isfile(curr_path + "/bell_simulation/gain_" + str(no_small_cells) + ".mat"):
            print("\nError: gain matrix does not exist for network with", no_small_cells, "small cells.\n")
            sleep(1)
            print("Matlab must be run to generate a new gain matrix.\n")
            sleep(1)
            user_input = input("Do you wish to run Matlab? ['yes' | 'no']\n\n")
            if user_input in ["yes", "y", "Yes", "YES", "Y"]:
                run_sim = True
            elif user_input in ["no", "n", "NO", "No", "N"]:
                print("\nSuit yourself so.\n")
                quit()

        print("\nEvaluating", SC_DISTRIBUTION, "network with", no_small_cells, "small cells...\n")

        hold_network_info.init(run_sim, N_USERS,
            test=no_small_cells,
            both=False,
            set=SC_DISTRIBUTION,
            b_lim=15,
            ITERATIONS=iterations,
            STRESS=stress_test,
            SCENARIO=scenario)

        if True:
            scheduling["original_sched"] = "self.pdiv(min_SINR, SINR - max_SINR) < (self.pdiv(tan(min_cell_SINR - num_shared), max_cell_SINR * good_slots) + min_cell_SINR)"

            scheduling["genetic_alg"] = "Run a genetic algorithm to compute schedules"

            scheduling["instructive_topology"] = "(pdiv(T3, T9)*(pdiv((np.log(1+abs((pdiv(pdiv(pdiv((+0.1+(T13-T13)), (np.sqrt(abs(T10))*(T3-T5))), (np.sqrt(abs(np.sin(pdiv(pdiv(T12, T7), np.sign((np.log(1+abs(pdiv(T4, T10)))*np.log(1+abs(T11))))))))+(pdiv(T15, T18)+pdiv(T16, T7)))), T2)+T7)))-T12), (T11*T12))--0.7))"

            scheduling["instructive_threshold"] = "pdiv(pdiv((np.log(1+abs((((np.log(1+abs(T5))+T10)-T13)-T10)))*pdiv((T15-T1), (T14-T9))), (np.sqrt(abs(np.sin(T15)))+(np.log(1+abs((T12+pdiv(pdiv(T16, T18), T5))))*(np.sin(T4)+T7)))), (pdiv(((T5-T14)-((np.sqrt(abs(np.sin(np.sin(((pdiv(T3, T1)*np.sqrt(abs(T16)))-(np.sqrt(abs(T2))-np.sqrt(abs(np.log(1+abs(T2))))))))))*(T7+T1))-T15)), ((T18*T18)-np.sqrt(abs(T18))))+((pdiv(T6, T7)-(T5-T17))-np.sign((T7*T8)))))"

            scheduling["evaluative_topology"] = "(pdiv(np.log(1+abs(T10)), (T11-T7))-((((T16+(((np.log(1+abs((np.sqrt(abs((np.log(1+abs(T3))+pdiv(T1, T3))))*((T12+pdiv(pdiv(pdiv(T15, T3), (T13-T5)), T4))*(T9+T4)))))*pdiv(np.sign(T6), np.sign(T4)))-(T16+T5))+(T4-pdiv((T5-T15), (T13*T14)))))+(np.log(1+abs((T7-pdiv(T18, T12))))-T2))-(T3*T4))*pdiv(np.sqrt(abs(T8)), pdiv(T9, T8))))"

            scheduling["evaluative_threshold"] = "(((pdiv(np.sin(pdiv(np.sqrt(abs(pdiv(T17, T13))), T5)), T12)*T20)*((((np.log(1+abs((T3*T2)))*np.sign((T5-T3)))+((T6*pdiv(T2, T3))*np.log(1+abs(T8))))*(T9*pdiv((+0.5-T17), T2)))-((T7*(T3+np.sin(pdiv(T4, T13))))*(np.sqrt(abs(T9))-T14))))+((T15-(np.sign(np.sign(np.sin(np.sin(T2))))*T5))+((pdiv(pdiv(pdiv((T7-T15), (T3-T4)), pdiv(pdiv(T6, T12), pdiv(T20, T6))), ((np.log(1+abs(T5))+(T9-T16))-np.sin(np.log(1+abs(T9)))))+np.sin(pdiv((pdiv(T23, T14)-pdiv(T7, T6)), np.log(1+abs(pdiv(T6, T4))))))+T17)))"

            scheduling['None'] = None

        pb_algorithm = "self.pdiv(ms_log_R, N_s)"#"self.pdiv(R_ms_avg * ms_log_R, R_s_avg * N_s)"#

        abs_algorithm = "self.pdiv(ABS_MUEs, non_ABS_MUEs + ABS_MSUEs)"#"self.pdiv(ABS_MUEs * ABS_MUEs, (float('7') + non_ABS_MUEs * non_ABS_MUEs + float('8')))"#

        import Optimise_Network as OPT

        network = OPT.Optimise_Network(
            PB_ALGORITHM=pb_algorithm,
            ABS_ALGORITHM=abs_algorithm,
            SCHEDULING_ALGORITHM=scheduling[scheduling_type],
            SCHEDULING_TYPE=scheduling_type,
            ALL_TOGETHER=OPT_ALL_TOGETHER,
            PRINT=PRINT_STATS,
            MAP=MAP_NETWORK,
            SAVE=SAVE_STATS,
            SHOW=SHOW_PLOTS,
            DISTRIBUTION=SC_DISTRIBUTION,
            REAL=REALISTIC,
            DIFFERENCE=COMPARE,
            DIFFICULTY=difficulty,
            FAIR=fair,
            BENCHMARK=BENCHMARK)
        fitnesses = network.run_all_2()
        network.get_average_performance(OUTPUT=True)
        if SAVE_STATS:
            TIME_STAMP = network.TIME_STAMP
            import visualise_schedule
            visualise_schedule.mane(getcwd() + "/Network_Stats/" + str(TIME_STAMP) + "/Heatmaps/", str(TIME_STAMP))

        if network.difference:
            print("Performance differential:", fitnesses)
        else:
            print("Fitnesses:")
            for key in list(fitnesses.keys()):
                if ('CDF' not in key) and (key != 'frequency') and (key != 'power_bias'):
                    print(" ", str(key), ":\t", fitnesses[key])

        print("\n\n")

if __name__ == "__main__":
    mane()
