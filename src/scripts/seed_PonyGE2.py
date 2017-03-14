from sys import path
path.append("../src")

from utilities.algorithm.general import check_python_version

check_python_version()

import sys

from scripts import GE_LR_parser
from ponyge import mane
from algorithm.parameters import params, set_params


if __name__ == '__main__':
    # Set parameters
    set_params(sys.argv[1:])
    
    # Parse seed individual and store in params.
    params['SEED_INDIVIDUAL'] = GE_LR_parser.main()
    
    # Launch PonyGE2.
    mane()
