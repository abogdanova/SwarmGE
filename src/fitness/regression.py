from utilities.helper_methods import get_Xy_train_test, get_Xy_train_test_separate
from utilities.error_metrics import mae, mse, rmse
from os import listdir, getcwd
from numpy import log, sqrt
from copy import deepcopy
from sys import maxsize
from math import isnan
import numpy as np


class regression:
    """ fitness function for regression problems. Given a set of training or
    test data, returns the RMS error between inputs and outputs for a set.
    """
    maximise = False
    def __init__(self, experiment):
        self.training_in, self.training_exp, self.test_in, self.test_exp = get_data(experiment)
        self.n_vars = np.shape(self.test_in)[1]

    def __call__(self, func, dist):

        if dist == "test":
            x = deepcopy(self.test_in)
            try:
                test_out = eval(func)
                fitness = mse(test_out, self.test_exp)
            except:
                fitness = maxsize

        elif dist == "training":
            x = deepcopy(self.training_in)
            try:
                training_out = eval(func)
                fitness = mse(training_out, self.training_exp)
            except:
                fitness = maxsize

        if (not fitness) or (fitness == np.nan) or isnan(fitness):
            fitness = maxsize

        return fitness

def pdiv(a, b):
    """ Protected division operator to prevent division by zero"""

    if type(b) is np.ndarray:
        mask = abs(b) < 1e-5
        if type(a) is np.ndarray:
            a[mask] = 1
            b[mask] = 1
        elif (type(a) is np.float64) or (type(a) is float) or (type(a) is int):
            b[mask] = a
        else:
            print ("New type encountered in pdiv:\t", type(a), "\n\n", a)
            quit()
        return a/b
    else:
        if b < 1e-5:
            return 1
        else:
            return a/b

def psqrt(x):
    """ Protected square root operator"""

    if type(x) is np.ndarray:
        mask = x < 0
        x[np.logical_not(mask)] = sqrt(x[np.logical_not(mask)])
        return x
    else:
        if x < 0:
            return x
        else:
            return sqrt(x)

def plog(x):
    """ Protected log operator"""

    if type(x) is np.ndarray:
        mask = x <= 0
        x[np.logical_not(mask)] = log(x[np.logical_not(mask)])
        return x
    else:
        if x <= 0:
            return x
        else:
            return log(x)

def get_data(experiment):
    """ Return the training and test data for the current experiment.
    """

    file_type = "txt"
    datasets = listdir(getcwd() + "/datasets/")
    for dataset in datasets:
        exp = dataset.split('.')[0].split('-')[0]
        if exp == experiment:
            file_type = dataset.split('.')[1]
    train_set = "datasets/" + experiment + "-Train." + str(file_type)
    test_set = "datasets/" + experiment + "-Test." + str(file_type)
    training_in, training_out, test_in, test_out = get_Xy_train_test_separate(train_set, test_set, skip_header=1)
    return training_in, training_out, test_in, test_out
