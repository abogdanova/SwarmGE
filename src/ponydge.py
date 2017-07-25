#! /usr/bin/env python

# Distributed grammatical evolution for Multi-Agent systems
# Copyright (c) 2017 Aadesh Neupane
# Hereby licensed under the GNU GPL v3.

""" Distributed Grammatical evolution for Multi-Agent system implementation """

from utilities.algorithm.general import check_python_version

check_python_version()

from stats.stats import get_stats
from algorithm.parameters import params, set_params
#from agent.agent import Agent

import sys



def main():
    """ Run program """

    # Run evolution
    #if params['MULTIAGENT']:
    #    individuals = params['search_multiagent']()        
        ##Create agents based on the number of agent passed as parameters
        #agents = create_agents(params['AGENT_SIZE'],params['INTERACTION_PROBABILITY'])
        #print (agents[0].individual)
    #else:
    individuals = params['SEARCH_LOOP']()

    # Print final review
    #print (individuals)
    get_stats(individuals, end=True)


if __name__ == "__main__":
    set_params(sys.argv[1:])  # exclude the ponydge.py arg itself
    main()