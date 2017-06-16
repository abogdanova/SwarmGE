#! /usr/bin/env python

# PonyGE
# Copyright (c) 2009 Erik Hemberg, James McDermott,
#                   Michael Fenton and David Fagan
# Hereby licensed under the GNU GPL v3.
""" Python GE implementation """

from utilities.algorithm.general import check_python_version

check_python_version()

from stats.stats import get_stats
from algorithm.parameters import params, set_params
import sys


def mane():
    """ Run program """

    # Run evolution
    individuals = params['SEARCH_LOOP']()

    # Print final review
    get_stats(individuals, end=True)


if __name__ == "__main__":
    set_params(sys.argv[1:])  # exclude the ponyge.py arg itself
    mane()
