from utilities.helper_methods import get_Xy_train_test_separate
from utilities.error_metrics import mse
from os import listdir, getcwd
from numpy import log, sqrt, abs
from sys import maxsize
from math import isnan
import numpy as np


class Regression:
    """Fitness function for supervised learning, ie regression and
    classification problems. Given a set of training or test data,
    returns the error between y (true labels) and yhat (estimated
    labels).

    We can pass in the error metric to be used. MSE is suitable for
    regression, while F1-score, hinge-loss and others are suitable for
    classification."""

    maximise = False

    def __init__(self, experiment, error=None):
        self.training_in, self.training_exp, self.test_in, self.test_exp = \
            get_data(experiment)
        self.n_vars = np.shape(self.test_in)[1]

        if error is None:
            self.error = mse
        else:
            self.error = error

    def __call__(self, func, dist):
        # We can call regression objects,
        # ie r = regression(exp); r(f, "training").

        if dist == "test":
            x = self.test_in
            y = self.test_exp
        elif dist == "training":
            x = self.training_in
            y = self.training_exp

        try:
            yhat = eval(func)  # func will refer to "x", created above

            # if func is a constant, eg 0.001 (doesn't refer to x),
            # then yhat will be a constant. that can confuse the error
            # metric.  so convert to a constant array.
            if not isinstance(yhat, np.ndarray):
                yhat = np.ones_like(y) * yhat

            # let's always call the error function with the true values first,
            # the estimate second
            fitness = self.error(y, yhat)
        except:
            fitness = maxsize

        # don't use "not fitness" here, because what if fitness = 0.0?!
        if isnan(fitness):
            fitness = maxsize

        return fitness


def pdiv(a, b):
    """The analytic quotient, intended as a "better protected division",
    from: Ji Ni and Russ H. Drieberg and Peter I. Rockett, "The Use of
    an Analytic Quotient Operator in Genetic Programming", IEEE
    Transactions on Evolutionary Computation."""
    return a / sqrt(1.0 + b * b)


def psqrt(x):
    """ Protected square root operator"""
    return sqrt(abs(x))


def plog(x):
    """ Protected log operator"""
    return log(1.0 + abs(x))


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
    training_in, training_out, test_in, \
    test_out = get_Xy_train_test_separate(train_set, test_set, skip_header=1)
    return training_in, training_out, test_in, test_out
