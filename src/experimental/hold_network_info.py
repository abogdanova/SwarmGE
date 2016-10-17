from algorithm.parameters import params
from os import path, getcwd


def init(simulation, set="test"):

    import experimental.Define_Network as DEFNET
    global network_params_2, network_params_1

    curr_path = getcwd()

    if params['TEST_DATA']:
        if not path.isfile("network_data/gain_" +
                                   str(params['N_SMALL_TRAINING']) + ".mat"):
            simulation_1 = True
        else:
            simulation_1 = False
        
        if not path.isfile(curr_path + "/network_data/gain_" + str(
                params['N_SMALL_TEST']) + ".mat"):
            simulation_2 = True
        else:
            simulation_1 = False
            simulation_2 = False

        print("Generating network training scenario for",
              params['N_SMALL_TRAINING'], "small cells...")
        het_net_1 = DEFNET.Define_Network(simulation_1)
        network_params_1 = het_net_1.run_all(params['N_SMALL_TRAINING'])

        print("Generating network testing scenario for",
              params['N_SMALL_TEST'], "small cells...")
        het_net_2 = DEFNET.Define_Network(simulation_2,
                                          iterations=2*params['ITERATIONS'],
                                          scenario=params['ITERATIONS'])
        network_params_2 = het_net_2.run_all(params['N_SMALL_TEST'])

    elif set == "test":
        het_net_2 = DEFNET.Define_Network(simulation)
        network_params_1 = None
        network_params_2 = het_net_2.run_all(params['N_SMALL_TEST'])
    
    elif set == "training":
        het_net_1 = DEFNET.Define_Network(simulation)
        network_params_1 = het_net_1.run_all(params['N_SMALL_TRAINING'])
        network_params_2 = None
    
    else:
        print("\nError: incorrect options for hold_network_info specified.")
        quit()


def get_network(dist):
    
    if dist == "training":
        return network_params_1
    
    elif dist == "test":
        return network_params_2
