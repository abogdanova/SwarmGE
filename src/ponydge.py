#! /usr/bin/env python

# Distributed grammatical evolution for Multi-Agent systems
# Copyright (c) 2017 Aadesh Neupane
# Hereby licensed under the GNU GPL v3.

""" Distributed Grammatical evolution for Multi-Agent system implementation """

from utilities.algorithm.general import check_python_version

check_python_version()

from stats.stats import get_stats
from algorithm.parameters import params, set_params
from agent.agent import Agent

import sys

def create_agents(n,p):
    return [Agent(p) for a in range(n)]

def main():
    """ Run program """

    # Run evolution
    if params['MULTIAGENT']:
        ##Create agents based on the number of agent passed as parameters
        agents = create_agents(params['AGENT_SIZE'],params['INTERACTION_PRBABILITY'])
        pass
    else:
        individuals = params['SEARCH_LOOP']()

    # Print final review
    get_stats(individuals, end=True)


if __name__ == "__main__":
    set_params(sys.argv[1:])  # exclude the ponydge.py arg itself
    main()