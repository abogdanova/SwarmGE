from os import path
from time import sleep

from algorithm.parameters import params
from experimental import pre_computed_network as PCN


def main():
    
    run_matlab = False
    if params['SIMULATION']:
        run_matlab = True

    if not params['SIMULATION'] and not path.isfile(
              "network_data/gain_" + str(params['N_SMALL_TRAINING'])
                                                            + ".mat"):
        if params['TEST_DATA'] and not path.isfile(
               "network_data/gain_" + str(params['N_SMALL_TEST'])
                                                            + ".mat"):
            print("\nError: gain matrices do not exist for networks with",
                  params['N_SMALL_TRAINING'], "and",
                  params['N_SMALL_TEST'], "small cells.\n")
            sleep(1)
            print("Matlab must be run to generate new gain matrices.\n")
        
        else:
            print("\nError: gain matrix does not exist for network with",
                  params['N_SMALL_TRAINING'], "small cells.\n")
            sleep(1)
            print("Matlab must be run to generate a new gain matrix.\n")
        
        sleep(1)
        user_input = input("Do you wish to run Matlab? ['yes' | 'no']\n\n")
        
        if user_input in ["yes", "y", "Yes", "YES", "Y"]:
            run_matlab = True
        
        elif user_input in ["no", "n", "NO", "No", "N"]:
            print("\nSuit yourself so.\n")
            quit()

    elif params['TEST_DATA'] and not params['SIMULATION'] and not \
            path.isfile("network_data/gain_" + str(params['N_SMALL_TEST'])
                                                    + ".mat"):
        print("\nError: gain matrix does not exist for network with",
              params['N_SMALL_TEST'], "small cells.\n")
        sleep(1)
        print("Matlab must be run to generate a new gain matrix.\n")
        sleep(1)
        user_input = input("Do you wish to run Matlab? ['yes' | 'no']\n\n")
        if user_input in ["yes", "y", "Yes", "YES", "Y"]:
            run_matlab = True
        elif user_input in ["no", "n", "NO", "No", "N"]:
            print("\nSuit yourself so.\n")
            quit()

    from experimental import hold_network_info
    hold_network_info.init(run_matlab, set="training")

    if params['PRE_COMPUTE']:
        
        print("\nPre-computing network...")
        from experimental import standalone_scheduler
        PCN.standalone_scheduler = \
            standalone_scheduler.Standalone_Fitness(
            realistic=params['REALISTIC'], difficulty=params['DIFFICULTY'])
        # We can pre-compute the network stats to schedule really fast.

        PCN.pre_computed_network = PCN.standalone_scheduler.pre_compute_network()
