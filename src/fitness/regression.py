from . import supervised_learning

from algorithm.parameters import params
from utilities.fitness.error_metric import mse


class regression(supervised_learning.supervised_learning):
    """Fitness function for regression. We just slightly specialise the
    function for supervised_learning."""
    
    def __init__(self):
        super().__init__()
        
        # Set error metric if it's not set already.
        if params['ERROR_METRIC'] is None:
            params['ERROR_METRIC'] = mse

        self.maximise = params['ERROR_METRIC'].maximise
