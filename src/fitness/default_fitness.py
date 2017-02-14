from algorithm.parameters import params
from sys import maxsize

def default_fitness():
    """Return a default fitness value."""
    if params['FITNESS_FUNCTION'].maximise:
        return -maxsize
    else:
        return maxsize
